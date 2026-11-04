import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knova_backend.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import StudentProfile, ParentProfile, UniversityStaff, University

def create_users():
    # 1. Admin User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@knova.com', 'admin123')
        print("Created admin user.")
        
    # 2. Student User
    if not User.objects.filter(username='student1').exists():
        student_user = User.objects.create_user('student1', 'student@knova.com', 'student123')
        student_user.first_name = "Alex"
        student_user.last_name = "Student"
        student_user.save()
        StudentProfile.objects.create(user=student_user)
        print("Created student user.")
        
    # 3. Parent User
    if not User.objects.filter(username='parent1').exists():
        parent_user = User.objects.create_user('parent1', 'parent@knova.com', 'parent123')
        parent_user.first_name = "Sarah"
        parent_user.last_name = "Parent"
        parent_user.save()
        ParentProfile.objects.create(user=parent_user)
        print("Created parent user.")
        
    # 4. University Staff User
    if not User.objects.filter(username='uni_staff1').exists():
        uni_user = User.objects.create_user('uni_staff1', 'staff@university.com', 'staff123')
        uni_user.first_name = "Dr. John"
        uni_user.last_name = "Smith"
        uni_user.save()
        
        # Get or create a university
        uni = University.objects.first()
        if not uni:
            uni = University.objects.create(name="Oxford University", slug="oxford-university")
            
        UniversityStaff.objects.create(user=uni_user, university=uni)
        print("Created university staff user.")

if __name__ == '__main__':
    create_users()
