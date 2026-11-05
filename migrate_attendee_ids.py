import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knova_backend.settings')
django.setup()

from core.models import Registration, StudentProfile, ParentProfile, StudentChallengePassport
from core.utils import generate_unique_attendee_id

valid_prefixes = ('KNOVA-ST-', 'KNOVA-EX-', 'KNOVA-PA-', 'KNOVA-SP-', 'KNOVA-AT-')

print("--- Updating Registrations ---")
for r in Registration.objects.all():
    old_id = r.registration_id
    if not old_id or not any(old_id.startswith(p) for p in valid_prefixes):
        new_id = generate_unique_attendee_id(r.role)
        r.registration_id = new_id
        r.save(update_fields=['registration_id'])
        print(f"Updated Registration {r.id} ({r.role}): {old_id} -> {new_id}")

print("--- Updating Student Profiles ---")
for s in StudentProfile.objects.all():
    old_qr = s.qr_identifier
    reg = Registration.objects.filter(email__iexact=s.user.email).first() if s.user else None
    if reg and reg.registration_id and reg.registration_id.startswith('KNOVA-ST-'):
        target_id = reg.registration_id
    elif not old_qr or not old_qr.startswith('KNOVA-ST-'):
        target_id = generate_unique_attendee_id('Student')
    else:
        target_id = old_qr

    if s.qr_identifier != target_id:
        s.qr_identifier = target_id
        s.save(update_fields=['qr_identifier'])
        print(f"Updated StudentProfile {s.id}: {old_qr} -> {target_id}")

print("--- Updating Parent Profiles ---")
for p in ParentProfile.objects.all():
    old_qr = p.qr_identifier
    reg = Registration.objects.filter(email__iexact=p.user.email).first() if p.user else None
    if reg and reg.registration_id and reg.registration_id.startswith('KNOVA-PA-'):
        target_id = reg.registration_id
    elif not old_qr or not old_qr.startswith('KNOVA-PA-'):
        target_id = generate_unique_attendee_id('Parent')
    else:
        target_id = old_qr

    if p.qr_identifier != target_id:
        p.qr_identifier = target_id
        p.save(update_fields=['qr_identifier'])
        print(f"Updated ParentProfile {p.id}: {old_qr} -> {target_id}")

print("--- Updating Passports ---")
for cp in StudentChallengePassport.objects.all():
    old_badge = cp.badge_id
    if not old_badge or not old_badge.startswith('KNOVA-ST-'):
        reg = cp.registration
        if reg and reg.registration_id and reg.registration_id.startswith('KNOVA-ST-'):
            target_id = reg.registration_id
        else:
            target_id = generate_unique_attendee_id('Student')
        cp.badge_id = target_id
        cp.save(update_fields=['badge_id'])
        print(f"Updated Passport {cp.id}: {old_badge} -> {target_id}")

print("Done migrating attendee IDs!")
