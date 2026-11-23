import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knova_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from core.models import University, UniversityProfile, UniversityStaff, Exhibitor, ExpoBooth, EventLocation, Registration

User = get_user_model()

def main():
    with transaction.atomic():
        loc = EventLocation.objects.filter(is_active=True).first() or EventLocation.objects.first()

        # 1. User admission@malabaruniversity.in
        u_malabar = User.objects.filter(email__iexact='admission@malabaruniversity.in').first()
        if not u_malabar:
            u_malabar = User.objects.filter(username__iexact='admission@malabaruniversity.in').first()
        if not u_malabar:
            u_malabar = User.objects.create(
                username='admission@malabaruniversity.in',
                email='admission@malabaruniversity.in',
                first_name='Malabar',
                last_name='Admissions',
                is_active=True
            )
        u_malabar.set_password('Admin@123456')
        u_malabar.is_active = True
        u_malabar.save()
        print(f"Malabar User: id={u_malabar.id}, email={u_malabar.email}, password_ok={u_malabar.check_password('Admin@123456')}")

        # 2. University Malabar University
        uni_malabar = University.objects.filter(name__iexact='Malabar University').first()
        if not uni_malabar:
            uni_malabar = University.objects.create(
                name='Malabar University',
                slug='malabar-university',
                hero_priority=1,
                is_approved=True
            )
        else:
            uni_malabar.hero_priority = 1
            uni_malabar.is_approved = True
            uni_malabar.save()

        prof_malabar, _ = UniversityProfile.objects.get_or_create(university=uni_malabar)
        prof_malabar.location_city = 'Malappuram'
        prof_malabar.location_state_country = 'Kerala, India'
        prof_malabar.website = 'https://malabaruniversity.in'
        prof_malabar.established_year = 2012
        prof_malabar.short_description = 'Premier higher education university providing advanced undergraduate, postgraduate, and professional study programs.'
        prof_malabar.save()

        # 3. Exhibitor Malabar University
        exh_malabar = Exhibitor.objects.filter(company_name__iexact='Malabar University').first()
        if not exh_malabar:
            exh_malabar = Exhibitor.objects.create(
                user=u_malabar,
                university=uni_malabar,
                company_name='Malabar University',
                event_location=loc,
                country='Kerala, India',
                website='https://malabaruniversity.in',
                is_verified=True
            )
        else:
            exh_malabar.user = u_malabar
            exh_malabar.university = uni_malabar
            exh_malabar.is_verified = True
            exh_malabar.country = 'Kerala, India'
            exh_malabar.save()

        # 4. UniversityStaff
        staff_malabar = UniversityStaff.objects.filter(user=u_malabar).first()
        if not staff_malabar:
            staff_malabar = UniversityStaff.objects.create(
                user=u_malabar,
                university=uni_malabar,
                role='Director of Admissions'
            )
        else:
            staff_malabar.university = uni_malabar
            staff_malabar.save()

        # 5. Booth C-03 for Malabar University
        b_c03 = ExpoBooth.objects.filter(booth_number__iexact='Booth C-03').first() or ExpoBooth.objects.filter(booth_number__iexact='C-03').first()
        if b_c03:
            b_c03.exhibitor = exh_malabar
            b_c03.university = uni_malabar
            b_c03.status = 'ASSIGNED'
            b_c03.hall = 'Hall 1 Main Concourse'
            b_c03.save()
        else:
            import uuid
            b_c03 = ExpoBooth.objects.create(
                booth_number='Booth C-03',
                hall='Hall 1 Main Concourse',
                exhibitor=exh_malabar,
                university=uni_malabar,
                status='ASSIGNED',
                qr_code=f"BOOTH-{uuid.uuid4().hex[:8].upper()}"
            )

        # 6. Saudi Uni (Slot 5, Booth C-01)
        uni_saudi1 = University.objects.filter(name__iexact='Saudi Uni').first()
        exh_saudi1 = Exhibitor.objects.filter(company_name__iexact='Saudi Uni').first()
        if uni_saudi1:
            uni_saudi1.hero_priority = 5
            uni_saudi1.is_approved = True
            uni_saudi1.save()
        if exh_saudi1 and uni_saudi1:
            exh_saudi1.university = uni_saudi1
            exh_saudi1.is_verified = True
            exh_saudi1.save()
        b_c01 = ExpoBooth.objects.filter(booth_number__icontains='C-01').first()
        if b_c01:
            b_c01.exhibitor = exh_saudi1
            b_c01.university = uni_saudi1
            b_c01.status = 'ASSIGNED'
            b_c01.hall = 'Hall 1 Main Concourse'
            b_c01.save()

        # 7. Saudi Univ (Slot 6, Booth C-06)
        uni_saudi2 = University.objects.filter(name__iexact='Saudi Univ').first()
        exh_saudi2 = Exhibitor.objects.filter(company_name__iexact='Saudi Univ').first()
        if uni_saudi2:
            uni_saudi2.hero_priority = 6
            uni_saudi2.is_approved = True
            uni_saudi2.save()
        if exh_saudi2 and uni_saudi2:
            exh_saudi2.university = uni_saudi2
            exh_saudi2.is_verified = True
            exh_saudi2.save()
        b_c06 = ExpoBooth.objects.filter(booth_number__icontains='C-06').first()
        if b_c06:
            b_c06.exhibitor = exh_saudi2
            b_c06.university = uni_saudi2
            b_c06.status = 'ASSIGNED'
            b_c06.hall = 'Hall 1 Main Concourse'
            b_c06.save()

        # 8. Bahrain Univ (Slot 2, Booth C-05)
        uni_bahrain = University.objects.filter(name__iexact='Bahrain Univ').first()
        exh_bahrain = Exhibitor.objects.filter(company_name__iexact='Bahrain Univ').first()
        if uni_bahrain:
            uni_bahrain.hero_priority = 2
            uni_bahrain.is_approved = True
            uni_bahrain.save()
        if exh_bahrain and uni_bahrain:
            exh_bahrain.university = uni_bahrain
            exh_bahrain.save()
        b_c05 = ExpoBooth.objects.filter(booth_number__icontains='C-05').first()
        if b_c05:
            b_c05.exhibitor = exh_bahrain
            b_c05.university = uni_bahrain
            b_c05.status = 'ASSIGNED'
            b_c05.hall = 'Hall 1 Main Concourse'
            b_c05.save()

        # 9. Virginia Commonwealth University (Slot 3, Booth C-04)
        uni_vcu = University.objects.filter(name__icontains='Virginia Commonwealth').first()
        exh_vcu = Exhibitor.objects.filter(company_name__icontains='Virginia Commonwealth').first()
        if uni_vcu:
            uni_vcu.hero_priority = 3
            uni_vcu.is_approved = True
            uni_vcu.save()
        if exh_vcu and uni_vcu:
            exh_vcu.university = uni_vcu
            exh_vcu.save()
        b_c04 = ExpoBooth.objects.filter(booth_number__icontains='C-04').first()
        if b_c04:
            b_c04.exhibitor = exh_vcu
            b_c04.university = uni_vcu
            b_c04.status = 'ASSIGNED'
            b_c04.hall = 'Hall 1 Main Concourse'
            b_c04.save()

    print("\n=== VERIFICATION SUMMARY ===")
    for s in range(1, 8):
        u = University.objects.filter(hero_priority=s).first()
        if u:
            b = u.allocated_booth
            b_str = f"{b.booth_number} ({b.hall})" if b else "No Booth"
            exh = getattr(u, 'exhibitor', None)
            exh_str = f"Exh ID={exh.id}" if exh else "No Exh"
            print(f"Slot #{s}: {u.name} | {b_str} | {exh_str}")
        else:
            print(f"Slot #{s}: [OPEN / UNASSIGNED]")

    print("\n=== ALL REGISTERED EXHIBITORS ===")
    for e in Exhibitor.objects.all().order_by('id'):
        b_str = e.booth.booth_number if hasattr(e, 'booth') and e.booth else "No Booth"
        print(f"Exh ID={e.id}: {e.company_name} | Uni={e.university.name if e.university else 'None'} | Booth={b_str} | Verified={e.is_verified}")

if __name__ == '__main__':
    main()
