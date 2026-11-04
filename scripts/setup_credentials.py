import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knova_backend.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import Client
from core.models import (
    StudentProfile, ParentProfile, UniversityStaff, University,
    Exhibitor, Speaker, Sponsor, EventLocation, StudentChallengePassport, SeminarStaff
)

def setup_all_credentials():
    print("Setting up and validating credentials for all user types...")

    loc = EventLocation.objects.filter(is_active=True).first() or EventLocation.objects.first()

    # 1. Superuser / Admin
    admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@knova.com'})
    admin_user.email = 'admin@knova.com'
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.set_password('admin123')
    admin_user.save()

    # 2. Student User
    student_user, _ = User.objects.get_or_create(username='student1', defaults={'email': 'student@knova.com'})
    student_user.email = 'student@knova.com'
    student_user.first_name = "Alex"
    student_user.last_name = "Student"
    student_user.set_password('student123')
    student_user.save()
    stu_prof, _ = StudentProfile.objects.get_or_create(user=student_user)
    StudentChallengePassport.objects.get_or_create(
        user=student_user,
        defaults={
            'student_name': 'Alex Student',
            'student_email': 'student@knova.com',
            'badge_id': 'KNOVA-STU-001'
        }
    )

    # 3. Parent User
    parent_user, _ = User.objects.get_or_create(username='parent1', defaults={'email': 'parent@knova.com'})
    parent_user.email = 'parent@knova.com'
    parent_user.first_name = "Sarah"
    parent_user.last_name = "Parent"
    parent_user.set_password('parent123')
    parent_user.save()
    par_prof, _ = ParentProfile.objects.get_or_create(user=parent_user)
    if stu_prof not in par_prof.linked_students.all():
        par_prof.linked_students.add(stu_prof)

    # 4. University Representative (Kerala University)
    kerala_uni = University.objects.filter(name__icontains='Kerala').first()
    if not kerala_uni:
        kerala_uni = University.objects.create(name="Kerala University", slug="kerala-university")
    arjun_user, _ = User.objects.get_or_create(username='arjun@keralauniversity.in', defaults={'email': 'arjun@keralauniversity.in'})
    arjun_user.email = 'arjun@keralauniversity.in'
    arjun_user.first_name = "Arjun"
    arjun_user.last_name = "Nair"
    arjun_user.set_password('kerala123')
    arjun_user.save()
    arjun_staff, _ = UniversityStaff.objects.get_or_create(user=arjun_user, defaults={'university': kerala_uni})
    arjun_staff.university = kerala_uni
    arjun_staff.save()
    if not Exhibitor.objects.filter(user=arjun_user).exists():
        Exhibitor.objects.create(
            user=arjun_user,
            company_name=kerala_uni.name,
            event_location=loc,
            country="India",
            is_verified=True
        )

    # 5. University Staff User (Cambridge / Global)
    uni_user, _ = User.objects.get_or_create(username='uni_staff1', defaults={'email': 'staff@university.com'})
    uni_user.email = 'staff@university.com'
    uni_user.first_name = "Dr. John"
    uni_user.last_name = "Smith"
    uni_user.set_password('staff123')
    uni_user.save()
    first_uni = University.objects.exclude(pk=kerala_uni.pk).first() or kerala_uni
    uni_staff, _ = UniversityStaff.objects.get_or_create(user=uni_user, defaults={'university': first_uni})
    if not uni_staff.university:
        uni_staff.university = first_uni
        uni_staff.save()

    # 6. Exhibitor User
    exhibitor_user, _ = User.objects.get_or_create(username='exhibitor_test', defaults={'email': 'exhibitor@test.com'})
    exhibitor_user.email = 'exhibitor@test.com'
    exhibitor_user.first_name = "Tech Corp"
    exhibitor_user.last_name = "Representative"
    exhibitor_user.set_password('exhibitor123')
    exhibitor_user.save()
    exhibitor_prof = Exhibitor.objects.filter(user=exhibitor_user).first()
    if not exhibitor_prof:
        exhibitor_prof = Exhibitor.objects.create(
            user=exhibitor_user,
            company_name="Tech Corp Global",
            event_location=loc,
            country="United States",
            is_verified=True
        )

    # 7. Speaker User
    speaker_user, _ = User.objects.get_or_create(username='speaker_test', defaults={'email': 'speaker@test.com'})
    speaker_user.email = 'speaker@test.com'
    speaker_user.first_name = "Dr. Jane"
    speaker_user.last_name = "Smith"
    speaker_user.set_password('speaker123')
    speaker_user.save()
    speaker_prof = Speaker.objects.filter(user=speaker_user).first()
    if not speaker_prof:
        speaker_prof = Speaker.objects.create(
            user=speaker_user,
            name="Dr. Jane Smith",
            title="Dean of Artificial Intelligence & Global Education",
            organization="KNOVA Academic Council",
            is_verified=True
        )

    # 8. Sponsor User
    sponsor_user, _ = User.objects.get_or_create(username='sponsor_test', defaults={'email': 'sponsor@test.com'})
    sponsor_user.email = 'sponsor@test.com'
    sponsor_user.first_name = "Lumentra"
    sponsor_user.last_name = "Ventures"
    sponsor_user.set_password('sponsor123')
    sponsor_user.save()
    sponsor_prof = Sponsor.objects.filter(user=sponsor_user).first()
    if not sponsor_prof:
        lum_sponsor = Sponsor.objects.filter(name__icontains='Lumentra').first()
        if lum_sponsor:
            lum_sponsor.user = sponsor_user
            lum_sponsor.save()
            sponsor_prof = lum_sponsor
        else:
            sponsor_prof = Sponsor.objects.create(
                user=sponsor_user,
                name="Lumentra Ventures",
                category="Headline Partner",
                event_location=loc,
                is_verified=True
            )

    # 9. Seminar Staff User
    seminar_user, _ = User.objects.get_or_create(username='seminar1', defaults={'email': 'seminar@knova.com'})
    seminar_user.email = 'seminar@knova.com'
    seminar_user.first_name = "Amina"
    seminar_user.last_name = "Al Mansoor"
    seminar_user.set_password('seminar123')
    seminar_user.save()
    SeminarStaff.objects.get_or_create(
        user=seminar_user,
        defaults={
            'event_location': loc,
            'hall_name': 'Hall A',
            'designation': 'Lead Seminar Hall Coordinator'
        }
    )

    print("\n--- CREDENTIALS SUMMARY TABLE ---")
    credentials_table = [
        ('Administrator / Superuser', 'admin', 'admin@knova.com', 'admin123', 'admin'),
        ('Student', 'student1', 'student@knova.com', 'student123', 'student'),
        ('Parent', 'parent1', 'parent@knova.com', 'parent123', 'parent'),
        ('University Rep (Kerala University)', 'arjun@keralauniversity.in', 'arjun@keralauniversity.in', 'kerala123', 'exhibitor'),
        ('University Staff (General)', 'uni_staff1', 'staff@university.com', 'staff123', 'exhibitor'),
        ('Exhibitor / Booth Lead', 'exhibitor_test', 'exhibitor@test.com', 'exhibitor123', 'exhibitor'),
        ('Seminar Hall Staff', 'seminar1', 'seminar@knova.com', 'seminar123', 'seminar'),
        ('Keynote Speaker', 'speaker_test', 'speaker@test.com', 'speaker123', 'speaker'),
        ('Headline Sponsor', 'sponsor_test', 'sponsor@test.com', 'sponsor123', 'sponsor'),
    ]

    client = Client()
    for role_name, username, email, pwd, expected_role in credentials_table:
        u_auth = authenticate(username=username, password=pwd)
        assert u_auth is not None, f"Failed auth for username: {username}"
        client.force_login(u_auth)
        resp = client.get('/dashboard/')
        assert resp.status_code == 200, f"Dashboard failed for {username}: status {resp.status_code}"
        rendered_role = expected_role
        if resp.context:
            try:
                rendered_role = resp.context.get('role', expected_role)
            except AttributeError:
                rendered_role = resp.context[0].get('role', expected_role)
        print(f"[OK] {role_name:<35} | {username:<28} | {pwd:<12} | Status: {resp.status_code}")

    print("\nALL CREDENTIALS CONFIGURED & VERIFIED!")

if __name__ == '__main__':
    setup_all_credentials()
