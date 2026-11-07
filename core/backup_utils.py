import os
import io
import gzip
import json
import time
import zipfile
import tempfile
import email.utils
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.core.management import call_command
from django.db import connection, transaction
from django.apps import apps
from django.core.mail import get_connection, EmailMessage

EXCLUDED_APPS_MODELS = ['contenttypes', 'auth.permission', 'sessions.session']


def get_backup_dir():
    """Returns absolute path to the directory where backups are stored."""
    if hasattr(settings, 'BACKUP_DIR') and settings.BACKUP_DIR:
        backup_dir = settings.BACKUP_DIR
    else:
        # Check if on production server (/var/www/knova/backups) or local
        prod_path = '/var/www/knova/backups'
        if os.path.isdir('/var/www/knova'):
            backup_dir = prod_path
        else:
            backup_dir = os.path.join(str(settings.BASE_DIR), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def generate_backup(compressed=False):
    """
    Dumps all data across all models in JSON format.
    Excludes ephemeral sessions and auto-generated contenttypes/auth.permission.
    Returns dict:
      - content: bytes
      - filename: str
      - record_count: int
      - size_bytes: int
      - size_formatted: str
      - timestamp: str
    """
    out = io.StringIO()
    call_command(
        'dumpdata',
        exclude=EXCLUDED_APPS_MODELS,
        format='json',
        indent=2,
        stdout=out
    )
    json_data = out.getvalue()
    raw_objs = json.loads(json_data)
    record_count = len(raw_objs)

    timestamp_str = timezone.now().strftime('%Y%m%d_%H%M%S')
    display_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

    if compressed:
        gz_buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=gz_buffer, mode='wb') as gz:
            gz.write(json_data.encode('utf-8'))
        content_bytes = gz_buffer.getvalue()
        filename = f"knova_backup_{timestamp_str}.json.gz"
    else:
        content_bytes = json_data.encode('utf-8')
        filename = f"knova_backup_{timestamp_str}.json"

    size_bytes = len(content_bytes)
    if size_bytes < 1024:
        size_fmt = f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        size_fmt = f"{size_bytes / 1024:.1f} KB"
    else:
        size_fmt = f"{size_bytes / (1024 * 1024):.2f} MB"

    return {
        'content': content_bytes,
        'filename': filename,
        'record_count': record_count,
        'size_bytes': size_bytes,
        'size_formatted': size_fmt,
        'timestamp': display_time,
        'timestamp_slug': timestamp_str,
    }


def save_backup_to_disk(dump_bytes, filename, retention_hours=24):
    """
    Saves backup bytes to the local backup directory.
    Automatically cleans up any backups older than retention_hours.
    """
    backup_dir = get_backup_dir()
    file_path = os.path.join(backup_dir, filename)
    with open(file_path, 'wb') as f:
        f.write(dump_bytes)

    # Purge backups older than retention_hours
    purged_count = purge_expired_backups(retention_hours=retention_hours)

    return file_path, purged_count


def purge_expired_backups(retention_hours=24):
    """
    Deletes local backup files older than retention_hours (default: 24h).
    Returns count of deleted files.
    """
    backup_dir = get_backup_dir()
    cutoff_time = time.time() - (retention_hours * 3600)
    purged_count = 0

    if not os.path.exists(backup_dir):
        return 0

    for fname in os.listdir(backup_dir):
        if fname.startswith('knova_backup_') and (fname.endswith('.json') or fname.endswith('.gz') or fname.endswith('.zip')):
            fpath = os.path.join(backup_dir, fname)
            try:
                if os.path.isfile(fpath) and os.path.getmtime(fpath) < cutoff_time:
                    os.remove(fpath)
                    purged_count += 1
            except Exception:
                pass

    return purged_count


def list_recent_backups(max_items=50):
    """
    Returns list of local backups stored within the last 24 hours.
    """
    backup_dir = get_backup_dir()
    if not os.path.exists(backup_dir):
        return []

    backups = []
    now = time.time()
    for fname in sorted(os.listdir(backup_dir), reverse=True):
        if fname.startswith('knova_backup_') and (fname.endswith('.json') or fname.endswith('.gz') or fname.endswith('.zip')):
            fpath = os.path.join(backup_dir, fname)
            try:
                stat = os.stat(fpath)
                mtime = stat.st_mtime
                age_secs = now - mtime
                age_mins = int(age_secs // 60)
                if age_mins < 60:
                    age_str = f"{age_mins}m ago"
                else:
                    age_str = f"{age_mins // 60}h {age_mins % 60}m ago"

                sz = stat.st_size
                if sz < 1024:
                    sz_str = f"{sz} B"
                elif sz < 1024 * 1024:
                    sz_str = f"{sz / 1024:.1f} KB"
                else:
                    sz_str = f"{sz / (1024 * 1024):.2f} MB"

                created_dt = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

                backups.append({
                    'filename': fname,
                    'size_formatted': sz_str,
                    'created_at': created_dt,
                    'age_string': age_str,
                    'is_compressed': fname.endswith('.gz') or fname.endswith('.zip'),
                })
                if len(backups) >= max_items:
                    break
            except Exception:
                pass

    return backups


def restore_database_dump(file_bytes_or_buffer, original_filename, clean_wipe=False):
    """
    Restores the database from uploaded JSON, .gz, or .zip.
    Optionally wipes existing core records if clean_wipe=True.
    Resets PostgreSQL sequences after restore.
    Returns (success: bool, message: str, restored_count: int).
    """
    if hasattr(file_bytes_or_buffer, 'read'):
        raw_bytes = file_bytes_or_buffer.read()
    else:
        raw_bytes = file_bytes_or_buffer

    filename_lower = original_filename.lower()
    json_bytes = None

    try:
        if filename_lower.endswith('.gz'):
            with gzip.GzipFile(fileobj=io.BytesIO(raw_bytes), mode='rb') as gz:
                json_bytes = gz.read()
        elif filename_lower.endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(raw_bytes), 'r') as zf:
                # Find first .json file in zip
                json_files = [n for n in zf.namelist() if n.endswith('.json')]
                if not json_files:
                    return False, "No .json fixture found inside the uploaded ZIP archive.", 0
                json_bytes = zf.read(json_files[0])
        else:
            json_bytes = raw_bytes

        # Validate that json_bytes is valid JSON array of Django fixtures
        parsed = json.loads(json_bytes.decode('utf-8'))
        if not isinstance(parsed, list):
            return False, "Invalid backup format: root element must be a JSON array of model fixtures.", 0
        restored_count = len(parsed)
    except Exception as e:
        return False, f"Failed to decompress or parse backup file: {str(e)}", 0

    # Write JSON fixture to an isolated temporary directory to avoid Django fixture collisions
    with tempfile.TemporaryDirectory() as temp_dir:
        fixture_path = os.path.join(temp_dir, 'restore_fixture.json')
        with open(fixture_path, 'wb') as f:
            f.write(json_bytes)

        try:
            with transaction.atomic():
                if clean_wipe:
                    # Clean wipe core models in reverse dependency order
                    core_models = [m for m in apps.get_models() if m._meta.app_label == 'core']
                    for model in reversed(core_models):
                        try:
                            model.objects.all().delete()
                        except Exception:
                            pass

                # Run loaddata on the isolated fixture
                call_command('loaddata', fixture_path, verbosity=0)

            # Reset sequences in PostgreSQL
            if connection.vendor == 'postgresql':
                from django.core.management.color import no_style
                core_auth_models = [m for m in apps.get_models() if m._meta.app_label in ['core', 'auth']]
                sequence_sql = connection.ops.sequence_reset_sql(no_style(), core_auth_models)
                with connection.cursor() as cursor:
                    for sql in sequence_sql:
                        try:
                            cursor.execute(sql)
                        except Exception:
                            pass

            return True, f"Successfully restored {restored_count} database objects from snapshot.", restored_count

        except Exception as e:
            return False, f"Database restoration failed: {str(e)}", 0


def get_smtp_config():
    """
    Reads SMTP configuration from SiteConfiguration or environment variables.
    """
    from core.models import SiteConfiguration
    config = SiteConfiguration.objects.first()

    smtp_host = getattr(config, 'smtp_host', '') or os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    smtp_port = getattr(config, 'smtp_port', 0) or int(os.environ.get('EMAIL_PORT', 587))
    smtp_user = getattr(config, 'smtp_user', '') or os.environ.get('EMAIL_HOST_USER', '')
    smtp_password = getattr(config, 'smtp_password', '') or os.environ.get('EMAIL_HOST_PASSWORD', '')
    smtp_use_tls = getattr(config, 'smtp_use_tls', True)
    recipient = getattr(config, 'backup_email_recipient', '') or os.environ.get('BACKUP_EMAIL_RECIPIENT', 'arjunaravinda@gmail.com')

    return {
        'host': smtp_host,
        'port': smtp_port,
        'user': smtp_user,
        'password': smtp_password,
        'use_tls': smtp_use_tls,
        'recipient': recipient.strip() or 'arjunaravinda@gmail.com',
    }


def send_backup_email(dump_bytes, filename, record_count, size_formatted, recipient=None, custom_smtp=None):
    """
    Sends backup snapshot to recipient with RFC 2156/4021 24h expiration headers.
    Returns (success: bool, status_message: str).
    """
    smtp_cfg = custom_smtp or get_smtp_config()
    to_email = recipient or smtp_cfg.get('recipient') or 'arjunaravinda@gmail.com'
    sender_email = smtp_cfg.get('user') or 'backup@knovaexpo.com'

    if not smtp_cfg.get('user') or not smtp_cfg.get('password'):
        return False, (
            "SMTP credentials not configured. Please enter your SMTP username and App Password "
            "in the settings below to enable automatic email delivery to " + to_email
        )

    # Calculate expiration time (24 hours from now) for email headers
    expire_time = time.time() + (24 * 3600)
    rfc_expire_date = email.utils.formatdate(expire_time, localtime=True)
    rfc_sent_date = email.utils.formatdate(time.time(), localtime=True)

    subject = f"[KNOVA EXPO] Full Database Backup ({record_count} objects) - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    body = f"""KNOVA 2027 Global Education Expo - Automated Database Backup Snapshot
======================================================================

Date & Time    : {timezone.now().strftime('%A, %d %B %Y, %I:%M:%S %p')} ({timezone.get_current_timezone_name()})
Archive File   : {filename}
Snapshot Size  : {size_formatted}
Total Records  : {record_count} verified objects
Platform Host  : knovaexpo.com

Data Included:
-------------
- 100% Complete Snapshot: Users, University & Exhibitor Profiles, Booths,
  Exams, Question Banks, Registrations, Attendees, Direct Messages,
  Leads, CMS Configuration, FAQs, and SEO Settings.

Retention & Auto-Deletion:
--------------------------
This backup was automatically dispatched by your 5-minute automated backup system.
In accordance with your retention policy, this snapshot email is tagged with an
Expires header for 24 hours. Local server backups older than 24 hours are
automatically purged from disk.

Restoration Instructions:
-------------------------
In the event of data loss or disaster recovery:
1. Log in to the KNOVA Admin Dashboard: https://knovaexpo.com/dashboard/settings/?tab=backup
2. Navigate to 'Database Backup & Restore' -> 'Restore Database'
3. Upload this attached file ({filename})
4. Click 'Restore Database Now' to restore 100% of your platform data.

--
KNOVA EXPO 2027 Automated Backup Daemon
Future Begins Here
"""

    try:
        backend_conn = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=smtp_cfg.get('host', 'smtp.gmail.com'),
            port=smtp_cfg.get('port', 587),
            username=smtp_cfg.get('user'),
            password=smtp_cfg.get('password'),
            use_tls=smtp_cfg.get('use_tls', True),
            timeout=25
        )

        email_msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=sender_email,
            to=[to_email],
            connection=backend_conn,
            headers={
                'Expires': rfc_expire_date,
                'X-Auto-Delete': '24-Hours',
                'X-Auto-Expire': '24-Hours',
                'Date': rfc_sent_date,
                'X-Mailer': 'Knova-Automated-Backup/1.0',
            }
        )

        # Attach file
        mime_type = 'application/gzip' if filename.endswith('.gz') else 'application/json'
        email_msg.attach(filename, dump_bytes, mime_type)

        email_msg.send(fail_silently=False)

        # If IMAP is available with the same credentials, attempt to clean up emails older than 24h
        try:
            cleanup_gmail_imap_backups(smtp_cfg.get('user'), smtp_cfg.get('password'))
        except Exception:
            pass

        return True, f"Backup email successfully dispatched to {to_email} with 24-hour expiration header."

    except Exception as e:
        return False, f"SMTP dispatch to {to_email} failed: {str(e)}"


def cleanup_gmail_imap_backups(username, password, retention_hours=24):
    """
    Connects to Gmail via IMAP and moves backup emails sent to the recipient older than 24 hours to Trash.
    """
    if not username or not password or '@gmail.com' not in username.lower():
        return 0

    import imaplib
    purged_count = 0
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993, timeout=15)
        mail.login(username, password)
        mail.select('INBOX')

        # Find emails with subject '[KNOVA EXPO] Full Database Backup' before cutoff date
        cutoff_date = (datetime.now() - timedelta(hours=retention_hours)).strftime('%d-%b-%Y')
        search_query = f'(BEFORE "{cutoff_date}" SUBJECT "[KNOVA EXPO] Full Database Backup")'
        status, data = mail.search(None, search_query)

        if status == 'OK' and data[0]:
            msg_ids = data[0].split()
            for msg_id in msg_ids:
                mail.store(msg_id, '+FLAGS', '\\Deleted')
                purged_count += 1
            mail.expunge()

        mail.logout()
    except Exception:
        pass

    return purged_count

