import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knova_backend.settings')
django.setup()

from core.models import University, CourseCategory, Course

def seed():
    # 1. Create categories
    cat_eng, _ = CourseCategory.objects.get_or_create(name='Engineering & Technology')
    cat_biz, _ = CourseCategory.objects.get_or_create(name='Business & Management')
    cat_art, _ = CourseCategory.objects.get_or_create(name='Arts & Humanities')
    cat_sci, _ = CourseCategory.objects.get_or_create(name='Science & Mathematics')

    # 2. Get or create universities
    u1, _ = University.objects.get_or_create(name='Tech University', defaults={'slug': 'tech-university', 'is_approved': True})
    u2, _ = University.objects.get_or_create(name='Global Business School', defaults={'slug': 'global-business-school', 'is_approved': True})
    u3, _ = University.objects.get_or_create(name='Arts College', defaults={'slug': 'arts-college', 'is_approved': True})

    # 3. Add some courses
    courses_data = [
        {'name': 'B.Tech Computer Science', 'category': cat_eng, 'university': u1, 'degree_type': 'UG', 'stream': 'CS', 'duration': '4 Years', 'mode': 'Full Time', 'fees': '$20,000/yr', 'eligibility': 'High School'},
        {'name': 'MBA', 'category': cat_biz, 'university': u2, 'degree_type': 'PG', 'stream': 'Management', 'duration': '2 Years', 'mode': 'Full Time', 'fees': '$35,000/yr', 'eligibility': 'Bachelor Degree'},
        {'name': 'B.A. Fine Arts', 'category': cat_art, 'university': u3, 'degree_type': 'UG', 'stream': 'Arts', 'duration': '3 Years', 'mode': 'Full Time', 'fees': '$15,000/yr', 'eligibility': 'High School'},
        {'name': 'M.S. Data Science', 'category': cat_eng, 'university': u1, 'degree_type': 'PG', 'stream': 'Data', 'duration': '2 Years', 'mode': 'Full Time', 'fees': '$25,000/yr', 'eligibility': 'Bachelor Degree'},
        {'name': 'BBA Online', 'category': cat_biz, 'university': u2, 'degree_type': 'UG', 'stream': 'Business', 'duration': '3 Years', 'mode': 'Online', 'fees': '$12,000/yr', 'eligibility': 'High School'},
        {'name': 'Ph.D Physics', 'category': cat_sci, 'university': u1, 'degree_type': 'PhD', 'stream': 'Physics', 'duration': '5 Years', 'mode': 'Full Time', 'fees': '$10,000/yr', 'eligibility': 'Master Degree'},
    ]

    for c in courses_data:
        Course.objects.get_or_create(
            name=c['name'], university=c['university'],
            defaults={
                'category': c['category'], 'degree_type': c['degree_type'], 'stream': c['stream'],
                'duration': c['duration'], 'mode': c['mode'], 'fees': c['fees'], 'eligibility': c['eligibility'],
                'is_active': True, 'status': 'Approved'
            }
        )

    print("Successfully seeded categories, universities, and courses.")

if __name__ == '__main__':
    seed()
