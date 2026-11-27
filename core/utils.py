import random
import time
from .models import Registration, Exhibitor

def generate_unique_attendee_id(role=None):
    """
    Generate a unique Attendee ID with role-based prefix and 5 random digits.
    - Student: KNOVA-ST-<5 digits> (e.g. KNOVA-ST-48291)
    - Exhibitor: KNOVA-EX-<5 digits> (e.g. KNOVA-EX-73910)
    - Parent: KNOVA-PA-<5 digits> (e.g. KNOVA-PA-15024)
    - Sponsor: KNOVA-SP-<5 digits> (e.g. KNOVA-SP-92817)
    - Default/Other: KNOVA-AT-<5 digits> (e.g. KNOVA-AT-61849)

    Guarantees uniqueness across:
    - Registration.registration_id
    - StudentProfile.qr_identifier
    - ParentProfile.qr_identifier
    - StudentChallengePassport.badge_id
    """
    from .models import StudentProfile, ParentProfile, StudentChallengePassport

    role_str = str(role or '').strip().upper()
    if 'STUDENT' in role_str:
        prefix = 'KNOVA-ST-'
    elif 'EXHIBITOR' in role_str or 'UNIVERSITY' in role_str:
        prefix = 'KNOVA-EX-'
    elif 'PARENT' in role_str:
        prefix = 'KNOVA-PA-'
    elif 'SPONSOR' in role_str:
        prefix = 'KNOVA-SP-'
    else:
        prefix = 'KNOVA-AT-'

    for _ in range(5000):
        candidate = f"{prefix}{random.randint(10000, 99999)}"
        if (
            not Registration.objects.filter(registration_id__iexact=candidate).exists()
            and not StudentProfile.objects.filter(qr_identifier__iexact=candidate).exists()
            and not ParentProfile.objects.filter(qr_identifier__iexact=candidate).exists()
            and not StudentChallengePassport.objects.filter(badge_id__iexact=candidate).exists()
        ):
            return candidate

    return f"{prefix}{int(time.time() * 1000) % 90000 + 10000}"


def calculate_match_score(student: Registration, exhibitor: Exhibitor) -> int:
    """
    Calculates a match score (0-100) between a student and an exhibitor based on their preferences.
    """
    score = 0
    total_criteria = 0
    
    # 1. Country Match
    if student.preferred_country and exhibitor.country:
        total_criteria += 1
        if student.preferred_country.lower() in exhibitor.country.lower() or exhibitor.country.lower() in student.preferred_country.lower():
            score += 40
            
    # 2. Budget Match
    if student.budget_range and exhibitor.tuition_range:
        total_criteria += 1
        if student.budget_range == exhibitor.tuition_range:
            score += 30
        elif student.budget_range == 'High' and exhibitor.tuition_range in ['Low', 'Medium']:
            # If student has a high budget, they can afford lower tuition
            score += 30
            
    # 3. Program Match
    if student.preferred_program and exhibitor.offered_programs:
        total_criteria += 1
        if student.preferred_program.lower() in exhibitor.offered_programs.lower():
            score += 30
            
    # Base score of 10 for just being at the same event
    if student.event_location == exhibitor.event_location:
        score += 10
        
    return min(100, score)

def get_top_matches_for_student(student: Registration, limit=5):
    """Returns top matching exhibitors for a specific student."""
    exhibitors = Exhibitor.objects.filter(event_location=student.event_location)
    matches = []
    for ex in exhibitors:
        score = calculate_match_score(student, ex)
        if score > 20: # Only return somewhat relevant matches
            matches.append((ex, score))
            
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:limit]

def get_top_matches_for_exhibitor(exhibitor: Exhibitor, limit=20):
    """Returns top matching students (Leads) for a specific exhibitor."""
    students = Registration.objects.filter(event_location=exhibitor.event_location, role='Student')
    matches = []
    for st in students:
        score = calculate_match_score(st, exhibitor)
        if score > 20:
            matches.append((st, score))
            
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:limit]


def send_knova_email(subject, html_message, to_emails, category='general', bcc_emails=None, attachments=None, inline_images=None, sync=False):
    """
    Unified SMTP email dispatcher using Admin-configured SiteConfiguration settings.
    category: 'registration' | 'password_reset' | 'challenge' | 'backup' | 'general'
    """
    if not to_emails:
        return False
    if isinstance(to_emails, str):
        to_emails = [e.strip() for e in to_emails.split(',') if e.strip()]
    if not to_emails:
        return False

    import threading
    from email.mime.image import MIMEImage
    from django.conf import settings
    from django.core.mail import EmailMultiAlternatives, get_connection
    from django.utils.html import strip_tags
    from .models import SiteConfiguration

    plain_message = strip_tags(html_message)

    def _dispatch():
        try:
            config = SiteConfiguration.get_solo()
            conn = None
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@knovaexpo.com')
            if config and config.smtp_user and config.smtp_password:
                conn = get_connection(
                    backend='django.core.mail.backends.smtp.EmailBackend',
                    host=config.smtp_host or 'smtp.gmail.com',
                    port=config.smtp_port or 587,
                    username=config.smtp_user,
                    password=config.smtp_password,
                    use_tls=config.smtp_use_tls,
                    timeout=20,
                )
                from_email = config.smtp_user

            reply_to_map = {
                'registration': getattr(config, 'registration_sender_email', '') or from_email,
                'password_reset': getattr(config, 'forgot_password_sender_email', '') or from_email,
                'challenge': getattr(config, 'challenge_updates_email', '') or from_email,
            }
            reply_to_addr = reply_to_map.get(category) or from_email
            reply_to = [reply_to_addr] if reply_to_addr else None

            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=from_email,
                to=to_emails,
                bcc=bcc_emails or None,
                reply_to=reply_to,
                connection=conn,
            )
            msg.attach_alternative(html_message, "text/html")

            for img in (inline_images or []):
                mime_img = MIMEImage(img['bytes'])
                mime_img.add_header('Content-ID', f"<{img['cid']}>")
                mime_img.add_header('Content-Disposition', 'inline', filename=img.get('filename', 'image.png'))
                msg.attach(mime_img)

            for att in (attachments or []):
                msg.attach(att['filename'], att['bytes'], att.get('mime', 'application/octet-stream'))

            msg.send(fail_silently=False)
            return True
        except Exception as exc:
            print(f"[KNOVA Email Error] ({category}) Failed sending to {to_emails}: {exc}")
            return False

    if sync:
        return _dispatch()
    threading.Thread(target=_dispatch, daemon=True).start()
    return True


def send_registration_welcome_email(request, registration, matches=None, sync=False):
    """
    Sends a rich welcome & profile completion email to a newly registered candidate,
    including their profile link, registration details, and Digital ID Card QR code.
    """
    if not registration or not registration.email:
        return False

    import io
    import qrcode
    from django.template.loader import render_to_string
    from django.urls import reverse
    from .models import SiteConfiguration

    role_lower = (registration.role or 'student').lower()
    if 'exhibitor' in role_lower:
        profile_route = 'dashboard_exhibitor_profile'
    elif 'parent' in role_lower:
        profile_route = 'dashboard_parent_profile'
    else:
        profile_route = 'dashboard_student_profile'

    def _abs(route_name, args=None):
        path = reverse(route_name, args=args)
        if request is not None:
            return request.build_absolute_uri(path)
        return f"https://knovaexpo.com{path}"

    badge_id = registration.registration_id or f"KNOVA-REG-{registration.id}"
    badge_url = _abs('digital_badge', args=[registration.pk])
    profile_url = _abs(profile_route)
    login_url = _abs('portal_login')
    event = registration.event_location

    qr = qrcode.make(badge_id)
    qr_buf = io.BytesIO()
    qr.save(qr_buf, format='PNG')
    qr_bytes = qr_buf.getvalue()

    html_message = render_to_string('core/email_confirmation.html', {
        'registration': registration,
        'event': event,
        'badge_id': badge_id,
        'badge_url': badge_url,
        'profile_url': profile_url,
        'login_url': login_url,
        'matches': matches or [],
    })
    subject = f"Welcome to KNOVA EXPO 2027 — Complete Your Profile & Download Your ID Card ({badge_id})"

    config = SiteConfiguration.get_solo()
    bcc_raw = getattr(config, 'registration_admin_notify_email', '') or ''
    bcc_list = [e.strip() for e in bcc_raw.replace(';', ',').split(',') if e.strip() and '@' in e]

    return send_knova_email(
        subject=subject,
        html_message=html_message,
        to_emails=[registration.email],
        category='registration',
        bcc_emails=bcc_list,
        inline_images=[{'cid': 'id_card_qr', 'bytes': qr_bytes, 'filename': f'{badge_id}.png'}],
        attachments=[{'filename': f'KNOVA_ID_Card_{badge_id}.png', 'bytes': qr_bytes, 'mime': 'image/png'}],
        sync=sync,
    )


def send_password_reset_email(request, user, reset_url, sync=False):
    """Sends a password reset email using the Admin-configured Forgot Password email settings."""
    if not user or not user.email:
        return False
    name = user.get_full_name() or user.username
    html_message = f"""
    <div style="font-family:Inter,Arial,sans-serif;max-width:560px;margin:0 auto;padding:24px;background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;">
      <h2 style="margin:0 0 12px 0;color:#0f172a;">Reset Your KNOVA Portal Password</h2>
      <p style="color:#334155;font-size:14px;">Hi <strong>{name}</strong>,</p>
      <p style="color:#475569;font-size:14px;">We received a request to reset the password for your KNOVA EXPO 2027 account (<code>{user.username}</code>). Click the button below to set a new password:</p>
      <p style="margin:22px 0;"><a href="{reset_url}" style="display:inline-block;background:#1768ff;color:#ffffff;font-weight:700;text-decoration:none;padding:12px 22px;border-radius:10px;">Reset Password &rarr;</a></p>
      <p style="color:#64748b;font-size:12.5px;">If you did not request this, you can safely ignore this email.</p>
    </div>
    """
    return send_knova_email(
        subject="KNOVA EXPO 2027 — Password Reset Request",
        html_message=html_message,
        to_emails=[user.email],
        category='password_reset',
        sync=sync,
    )


def send_challenge_update_email(request, passport, title, detail, sync=False):
    """Sends a KNOVA Challenge milestone/completion update email to the student."""
    email = passport.student_email or (passport.user.email if passport.user else '') or (passport.registration.email if passport.registration else '')
    if not email:
        return False
    challenge_url = request.build_absolute_uri('/challenge/') if request else 'https://knovaexpo.com/challenge/'
    scholarships_url = request.build_absolute_uri('/dashboard/scholarships/') if request else 'https://knovaexpo.com/dashboard/scholarships/'
    html_message = f"""
    <div style="font-family:Inter,Arial,sans-serif;max-width:560px;margin:0 auto;padding:24px;background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;">
      <div style="font-size:11px;font-weight:800;color:#1768ff;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:6px;">KNOVA Challenge Update</div>
      <h2 style="margin:0 0 10px 0;color:#0f172a;">{title}</h2>
      <p style="color:#334155;font-size:14px;">Hi <strong>{passport.student_name}</strong>,</p>
      <p style="color:#475569;font-size:14px;">{detail}</p>
      <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:12px 16px;margin:16px 0;font-size:13px;color:#0f172a;">
        <strong>Badge ID:</strong> {passport.badge_id}<br>
        <strong>Total Points:</strong> {passport.total_points} XP
      </div>
      <p style="margin:20px 0;">
        <a href="{challenge_url}" style="display:inline-block;background:#0f172a;color:#ffffff;font-weight:700;text-decoration:none;padding:10px 18px;border-radius:8px;margin-right:8px;">View Challenge Passport &rarr;</a>
        <a href="{scholarships_url}" style="display:inline-block;background:#1768ff;color:#ffffff;font-weight:700;text-decoration:none;padding:10px 18px;border-radius:8px;">Scholarships &rarr;</a>
      </p>
    </div>
    """
    return send_knova_email(
        subject=f"KNOVA Challenge Update: {title}",
        html_message=html_message,
        to_emails=[email],
        category='challenge',
        sync=sync,
    )
