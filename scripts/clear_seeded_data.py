import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knova_backend.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from core.models import (
    Registration, University, UniversityProfile, Course, Scholarship, CourseCategory,
    Speaker, Sponsor, ProgrammeSession, ExamQuestion, QuestionChoice, Exhibitor,
    ExpoBooth, ExhibitorStaff, ExhibitorLead, ExhibitorMeeting, BoothVisit,
    StudentChallengePassport, ScholarshipExamSlot, ScholarshipExamBooking,
    ScholarshipExam, ExamSlot, ExamRegistration, ExamAttempt, StudentAnswer,
    FloorActivityZone, DirectMessage, Notification, Enquiry, SavedUniversity,
    SavedCourse, SavedScholarship, UniversityApplication, BoothInteraction,
    SeminarAttendance, StudentSchedule, ParentSchedule, StudentDocument,
    StudentInterest, ChatLead, SeminarStaff, UniversityStaff,
    StudentProfile, ParentProfile, EventLocation, SiteConfiguration,
    ExpoEvent, ExpoSession, DataImportJob, AuditLog
)

def clear_seeded_data():
    print("=" * 60)
    print("STARTING SEEDED DATA PURGE...")
    print("=" * 60)

    # Core system users to retain
    KEEP_USERNAMES = {
        'admin',
        'exhibitor_test',
        'student1',
        'parent1',
        'sponsor_test',
        'seminar1',
        'speaker_test',
        'uni_staff1'
    }

    with transaction.atomic():
        # 1. Clear exam and quiz attempts / answers / questions
        print("Clearing exam and question records...")
        StudentAnswer.objects.all().delete()
        ExamAttempt.objects.all().delete()
        ExamRegistration.objects.all().delete()
        ExamSlot.objects.all().delete()
        QuestionChoice.objects.all().delete()
        ExamQuestion.objects.all().delete()
        ScholarshipExamBooking.objects.all().delete()
        ScholarshipExamSlot.objects.all().delete()
        ScholarshipExam.objects.all().delete()

        # 2. Clear engagement, activity, passport, schedule and communication data
        print("Clearing engagement, leads, passport and messages...")
        StudentChallengePassport.objects.all().delete()
        SeminarAttendance.objects.all().delete()
        BoothInteraction.objects.all().delete()
        BoothVisit.objects.all().delete()
        ExhibitorLead.objects.all().delete()
        ExhibitorMeeting.objects.all().delete()
        ChatLead.objects.all().delete()
        UniversityApplication.objects.all().delete()
        SavedUniversity.objects.all().delete()
        SavedCourse.objects.all().delete()
        SavedScholarship.objects.all().delete()
        Enquiry.objects.all().delete()
        DirectMessage.objects.all().delete()
        Notification.objects.all().delete()
        StudentSchedule.objects.all().delete()
        ParentSchedule.objects.all().delete()
        StudentDocument.objects.all().delete()
        StudentInterest.objects.all().delete()
        FloorActivityZone.objects.all().delete()
        DataImportJob.objects.all().delete()
        AuditLog.objects.all().delete()

        # 3. Clear sessions, registrations and booths
        print("Clearing registrations, sessions, exhibitors, courses, universities...")
        Registration.objects.all().delete()
        ProgrammeSession.objects.all().delete()
        ExpoSession.objects.all().delete()
        ExpoEvent.objects.all().delete()
        Speaker.objects.all().delete()
        Sponsor.objects.all().delete()
        ExpoBooth.objects.all().delete()
        ExhibitorStaff.objects.all().delete()
        Exhibitor.objects.all().delete()

        # 4. Clear academic records
        Scholarship.objects.all().delete()
        Course.objects.all().delete()
        CourseCategory.objects.all().delete()
        UniversityProfile.objects.all().delete()
        UniversityStaff.objects.all().delete()
        SeminarStaff.objects.all().delete()
        University.objects.all().delete()

        # 5. Clean up users and profiles
        print("Cleaning user accounts and profiles...")
        # Delete non-canonical users
        deleted_users_count, _ = User.objects.exclude(username__in=KEEP_USERNAMES).delete()
        print(f"Deleted {deleted_users_count} temporary/e2e test user accounts.")

        # Ensure canonical accounts are in pristine state
        admin_u = User.objects.filter(username='admin').first()
        if admin_u:
            admin_u.is_staff = True
            admin_u.is_superuser = True
            admin_u.set_password('Knova@1234')
            admin_u.save()

        student_u = User.objects.filter(username='student1').first()
        if student_u:
            student_u.first_name = "Alex"
            student_u.last_name = "Student"
            student_u.email = "student@knova.com"
            student_u.set_password('Knova@1234')
            student_u.save()
            # Clean student profile
            StudentProfile.objects.filter(user=student_u).delete()
            StudentProfile.objects.create(
                user=student_u,
                mobile="+971 50 123 4567",
                city="Dubai",
                country_of_residence="United Arab Emirates",
                current_education="High School Final Year",
                school_college="",
                preferred_program="Computer Science & AI",
                preferred_degree="Undergraduate",
                preferred_country="United Arab Emirates"
            )

        parent_u = User.objects.filter(username='parent1').first()
        if parent_u:
            parent_u.first_name = "Sarah"
            parent_u.last_name = "Parent"
            parent_u.email = "parent@knova.com"
            parent_u.set_password('Knova@1234')
            parent_u.save()
            # Clean parent profile
            ParentProfile.objects.filter(user=parent_u).delete()
            par_prof = ParentProfile.objects.create(
                user=parent_u,
                mobile="+971 50 987 6543"
            )
            stu_prof = StudentProfile.objects.filter(user=student_u).first()
            if stu_prof:
                par_prof.linked_students.add(stu_prof)

        for u_name in ['exhibitor_test', 'sponsor_test', 'seminar1', 'speaker_test', 'uni_staff1']:
            u = User.objects.filter(username=u_name).first()
            if u:
                u.set_password('Knova@1234')
                u.save()

        # Clean old sessions
        Session.objects.all().delete()

    print("=" * 60)
    print("SEEDED DATA PURGE COMPLETED SUCCESSFULLY!")
    print("=" * 60)

    # Print summary of remaining counts
    print("\nCURRENT DATABASE RECORD COUNTS:")
    from django.apps import apps
    for model in apps.get_app_config('core').get_models():
        c = model.objects.count()
        print(f"  {model.__name__}: {c}")

    print(f"  auth.User: {User.objects.count()}")

if __name__ == '__main__':
    clear_seeded_data()
