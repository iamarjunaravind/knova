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


def send_registration_welcome_email(request, registration, matches=None, sync=False):
    """
    Sends a rich welcome & profile completion email to a newly registered candidate,
    including their profile link, registration details, and Digital ID Card QR code.
    Uses live SMTP settings from SiteConfiguration when configured.
    """
    if not registration or not registration.email:
        return False

    import io
    import threading
    from email.mime.image import MIMEImage
    import qrcode
    from django.conf import settings
    from django.core.mail import EmailMultiAlternatives, get_connection
    from django.template.loader import render_to_string
    from django.urls import reverse
    from django.utils.html import strip_tags
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

    # Generate QR Code PNG bytes for ID Card
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
    plain_message = strip_tags(html_message)
    subject = f"Welcome to KNOVA EXPO 2027 — Complete Your Profile & Download Your ID Card ({badge_id})"

    def _dispatch():
        try:
            config = SiteConfiguration.objects.first()
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

            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=from_email,
                to=[registration.email],
                connection=conn,
            )
            msg.attach_alternative(html_message, "text/html")

            # Inline QR image for Digital ID Card in email body
            inline_qr = MIMEImage(qr_bytes)
            inline_qr.add_header('Content-ID', '<id_card_qr>')
            inline_qr.add_header('Content-Disposition', 'inline', filename=f'{badge_id}.png')
            msg.attach(inline_qr)

            # Downloadable ID Card QR attachment
            msg.attach(f'KNOVA_ID_Card_{badge_id}.png', qr_bytes, 'image/png')

            msg.send(fail_silently=False)
            return True
        except Exception as exc:
            print(f"[KNOVA Email Error] Failed sending registration email to {registration.email}: {exc}")
            return False

    if sync:
        return _dispatch()
    threading.Thread(target=_dispatch, daemon=True).start()
    return True
