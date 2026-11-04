from django.test import TestCase
from django.contrib.auth.models import User
from .models import StudentProfile, Registration, University, Course, ExpoBooth

class RegistrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student1', email='student1@test.com', password='password123')
        self.student = StudentProfile.objects.create(
            user=self.user,
            date_of_birth='2000-01-01',
        )
        self.reg = Registration.objects.create(
            full_name='Student One',
            email='student1@test.com',
            role='Student'
        )

    def test_registration_creation(self):
        self.assertEqual(Registration.objects.count(), 1)
        self.assertEqual(self.reg.status, 'Pending')
        self.assertTrue(self.reg.registration_id.startswith('KNV-2027'))

    def test_duplicate_registration_protection(self):
        from django.db.utils import IntegrityError
        with self.assertRaises(IntegrityError):
            Registration.objects.create(
                registration_id=self.reg.registration_id,
                full_name='Duplicate',
                email='student1@test.com'
            )

class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='authuser', password='securepass123')

    def test_successful_login(self):
        login = self.client.login(username='authuser', password='securepass123')
        self.assertTrue(login)

    def test_failed_login(self):
        login = self.client.login(username='authuser', password='wrongpassword')
        self.assertFalse(login)

    def test_protected_dashboard(self):
        response = self.client.get('/dashboard/')
        self.assertNotEqual(response.status_code, 200) 

class UniversityTests(TestCase):
    def setUp(self):
        self.uni = University.objects.create(name='Test University', slug='test-uni', is_approved=True)

    def test_course_creation(self):
        course = Course.objects.create(
            university=self.uni,
            name='Computer Science',
            duration='3 Years'
        )
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(course.university.name, 'Test University')

class BoothTests(TestCase):
    def setUp(self):
        self.uni = University.objects.create(name='Booth Uni', slug='booth-uni')
        self.booth = ExpoBooth.objects.create(
            booth_number='A100',
            hall='Main Hall',
            university=self.uni,
            status='ACTIVE'
        )

    def test_booth_assignment(self):
        self.assertEqual(self.booth.get_assigned_organization(), 'Booth Uni')
