import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knova_backend.settings')
django.setup()

from core.models import University, CourseCategory, Course, Scholarship

def run_seed():
    print("Creating course categories...")
    categories = ['Computer Science', 'Business & Management', 'Engineering', 'Arts & Humanities', 'Medicine & Health', 'Sciences']
    cat_objs = []
    for c in categories:
        obj, _ = CourseCategory.objects.get_or_create(name=c)
        cat_objs.append(obj)

    print("Generating courses and scholarships for all universities...")
    universities = University.objects.all()
    
    course_names = {
        'Computer Science': ['BSc Computer Science', 'MSc Artificial Intelligence', 'BSc Software Engineering', 'MSc Data Science'],
        'Business & Management': ['BBA Business Administration', 'MBA Global Business', 'BSc Economics', 'MSc Marketing'],
        'Engineering': ['BEng Mechanical Engineering', 'MEng Civil Engineering', 'BEng Electrical Engineering', 'MSc Aerospace Engineering'],
        'Arts & Humanities': ['BA English Literature', 'MA History', 'BA Philosophy', 'MA Fine Arts'],
        'Medicine & Health': ['MBBS Medicine', 'BSc Nursing', 'MSc Public Health', 'PharmD Pharmacy'],
        'Sciences': ['BSc Physics', 'MSc Chemistry', 'BSc Biology', 'MSc Environmental Science']
    }

    degrees = ['UG', 'PG']
    modes = ['Full Time', 'Part Time', 'Online']
    
    for uni in universities:
        # Create 3-8 courses per university
        num_courses = random.randint(3, 8)
        
        for _ in range(num_courses):
            cat = random.choice(cat_objs)
            name = random.choice(course_names[cat.name])
            Course.objects.create(
                university=uni,
                name=name,
                category=cat,
                degree_type=random.choice(degrees),
                stream=cat.name,
                duration=f"{random.randint(1, 4)} Years",
                mode=random.choice(modes),
                eligibility="High school diploma or equivalent.",
                fees=f"${random.randint(10, 50)},000 / year",
                scholarship_available=random.choice([True, False])
            )
            
        # Create 1-3 scholarships
        num_scholarships = random.randint(1, 3)
        for i in range(num_scholarships):
            Scholarship.objects.create(
                university=uni,
                name=f"{uni.name} Excellence Award {i+1}",
                amount=f"${random.randint(2, 15)},000",
                eligibility="High academic achievement.",
                description="Awarded to outstanding international students."
            )

    print("Successfully seeded courses and scholarships!")

if __name__ == '__main__':
    run_seed()
