import os
import json
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.backup_utils import (
    generate_backup,
    save_backup_to_disk,
    send_backup_email,
    get_smtp_config,
    get_backup_dir,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generates a full database backup snapshot, saves it to disk (purging backups older than 24h), and emails it to arjunaravinda@gmail.com."

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default=None,
            help='Override destination email recipient (default: arjunaravinda@gmail.com)'
        )
        parser.add_argument(
            '--no-compress',
            action='store_true',
            help='Save raw .json instead of compressed .json.gz'
        )
        parser.add_argument(
            '--retention',
            type=int,
            default=24,
            help='Hours to retain backups on disk (default: 24)'
        )
        parser.add_argument(
            '--skip-email',
            action='store_true',
            help='Skip sending the email and only perform disk backup and retention cleanup'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Execute backup even if automated backups are paused in dashboard settings'
        )

    def handle(self, *args, **options):
        compress = not options.get('no_compress')
        retention = options.get('retention', 24)
        recipient = options.get('email')

        # Check if automated backup delivery is paused by admin
        smtp_cfg = get_smtp_config()
        if not options.get('force') and not smtp_cfg.get('enabled', True):
            self.stdout.write(self.style.WARNING(f"[{timezone.now()}] Automated backup email delivery is currently PAUSED by administrator in Dashboard settings. Skipping backup sequence."))
            return

        self.stdout.write(self.style.NOTICE(f"[{timezone.now()}] Starting automated KNOVA database backup..."))

        # 1. Generate full snapshot
        try:
            backup_data = generate_backup(compressed=compress)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Backup generation failed: {str(e)}"))
            return

        # 2. Save to local disk & purge older than 24h
        try:
            file_path, purged_count = save_backup_to_disk(
                backup_data['content'],
                backup_data['filename'],
                retention_hours=retention
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Saved {backup_data['filename']} ({backup_data['size_formatted']}, {backup_data['record_count']} objects). "
                    f"Purged {purged_count} expired backups older than {retention}h."
                )
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to save backup to disk: {str(e)}"))
            file_path = None

        # 3. Email dispatch
        email_status = "Skipped"
        email_ok = False
        if not options.get('skip_email'):
            smtp_cfg = get_smtp_config()
            target_email = recipient or smtp_cfg.get('recipient') or 'arjunaravinda@gmail.com'

            email_ok, email_status = send_backup_email(
                dump_bytes=backup_data['content'],
                filename=backup_data['filename'],
                record_count=backup_data['record_count'],
                size_formatted=backup_data['size_formatted'],
                recipient=target_email
            )

            if email_ok:
                self.stdout.write(self.style.SUCCESS(f"Email sent: {email_status}"))
            else:
                self.stdout.write(self.style.WARNING(f"Email status: {email_status}"))

        # 4. Save execution status metadata
        try:
            backup_dir = get_backup_dir()
            status_file = os.path.join(backup_dir, 'last_backup_status.json')
            status_payload = {
                'timestamp': backup_data['timestamp'],
                'filename': backup_data['filename'],
                'size_formatted': backup_data['size_formatted'],
                'record_count': backup_data['record_count'],
                'email_recipient': recipient or get_smtp_config().get('recipient') or 'arjunaravinda@gmail.com',
                'email_success': email_ok,
                'email_message': email_status,
                'retention_hours': retention,
            }
            with open(status_file, 'w', encoding='utf-8') as sf:
                json.dump(status_payload, sf, indent=2)
        except Exception:
            pass

        self.stdout.write(self.style.SUCCESS(f"[{timezone.now()}] Automated backup sequence completed successfully."))

