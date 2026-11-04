import os, sys, datetime
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knova_backend.settings')
import django
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import (
    EventLocation, University, UniversityProfile, Exhibitor, ExpoBooth,
    CourseCategory, Course, Scholarship, Speaker, ProgrammeSession,
    Sponsor, ScholarshipExam, ExamQuestion, QuestionChoice, Registration,
    FloorActivityZone, StudentProfile
)

User = get_user_model()

print("--- Step 1: Clean & Professionalize User Accounts ---")
user_updates = {
    'admin': {'first': 'Director', 'last': 'Admissions', 'email': 'admissions@knova.org'},
    'student1': {'first': 'Alexander', 'last': 'Wright', 'email': 'alexander.wright@knova.org'},
    'parent1': {'first': 'Sarah', 'last': 'Jenkins', 'email': 'sarah.jenkins@knova.org'},
    'exhibitor_test': {'first': 'Jonathan', 'last': 'Edwards', 'email': 'jonathan.edwards@oxford.ac.uk'},
    'sponsor_test': {'first': 'Marcus', 'last': 'Vance', 'email': 'marcus.vance@emirates.com'},
    'speaker_test': {'first': 'Dr. Julian', 'last': 'Thorne', 'email': 'julian.thorne@imperial.ac.uk'},
    'uni_staff1': {'first': 'Dr. Arthur', 'last': 'Pendelton', 'email': 'arthur.pendelton@cambridge.ac.uk'},
    'seminar1': {'first': 'Dr. Amina', 'last': 'Al-Mansoor', 'email': 'amina.almansoor@knova.org'},
}

for username, data in user_updates.items():
    u = User.objects.filter(username=username).first()
    if u:
        u.first_name = data['first']
        u.last_name = data['last']
        u.email = data['email']
        u.save()
        print(f"Updated user '{username}' -> {u.get_full_name()} ({u.email})")

# Update StudentProfile for student1
student_user = User.objects.filter(username='student1').first()
if student_user and hasattr(student_user, 'student_profile'):
    sp = student_user.student_profile
    sp.school_college = "Dubai International Academy"
    sp.city = "Dubai"
    sp.country_of_residence = "United Arab Emirates"
    sp.mobile = "+971 50 123 4567"
    sp.current_education = "High School Senior"
    sp.class_year = "2027"
    sp.grades = "3.92 GPA / IB 42"
    sp.english_proficiency = "IELTS 8.5"
    sp.preferred_degree = "Undergraduate"
    sp.preferred_program = "Computer Science & Artificial Intelligence"
    sp.preferred_country = "United Arab Emirates"
    sp.qr_identifier = "KNV-STU-0842"
    sp.save()
    print("Updated student1 StudentProfile with authentic school and profile details.")

print("\n--- Step 2: Seed 10 Authentic GCC & Global Event Locations ---")
EventLocation.objects.all().delete()

events_data = [
    {
        "name": "Dubai International Higher Education Expo 2027",
        "city": "Dubai",
        "venue": "Dubai World Trade Centre, Sheikh Zayed Road",
        "timings": "10:00 AM – 07:00 PM Daily",
        "start_date": datetime.date(2027, 2, 10),
        "end_date": datetime.date(2027, 2, 12),
        "description": "The GCC's flagship higher education gathering featuring over 150 elite global universities, keynote pavilions, and direct scholarship admissions.",
        "is_active": True,
        "is_upcoming": True
    },
    {
        "name": "Riyadh Global Higher Education Summit 2027",
        "city": "Riyadh",
        "venue": "Riyadh International Convention & Exhibition Center",
        "timings": "09:30 AM – 06:30 PM Daily",
        "start_date": datetime.date(2027, 2, 16),
        "end_date": datetime.date(2027, 2, 18),
        "description": "Connecting Saudi Arabia's top academic achievers with world-ranked university deans and Vision 2030 scholarship opportunities.",
        "is_active": True,
        "is_upcoming": True
    },
    {
        "name": "Abu Dhabi World University Fair 2027",
        "city": "Abu Dhabi",
        "venue": "ADNEC Centre, Hall 4 & 5",
        "timings": "10:00 AM – 07:00 PM Daily",
        "start_date": datetime.date(2027, 2, 22),
        "end_date": datetime.date(2027, 2, 24),
        "description": "Premier UAE capital higher education congress featuring leading STEM, Medicine, and Business faculties.",
        "is_active": True,
        "is_upcoming": True
    },
    {
        "name": "Doha Academic & Career Forum 2027",
        "city": "Doha",
        "venue": "Qatar National Convention Centre (QNCC)",
        "timings": "10:00 AM – 06:00 PM Daily",
        "start_date": datetime.date(2027, 3, 2),
        "end_date": datetime.date(2027, 3, 4),
        "description": "Qatar's most comprehensive international university showcase with dedicated graduate fellowship clinics.",
        "is_active": True,
        "is_upcoming": True
    },
    {
        "name": "Manama Higher Education Concourse 2027",
        "city": "Manama",
        "venue": "Exhibition World Bahrain, Sakhir",
        "timings": "10:00 AM – 07:00 PM Daily",
        "start_date": datetime.date(2027, 3, 8),
        "end_date": datetime.date(2027, 3, 10),
        "description": "Bahrain's premier academic gathering welcoming accredited European, North American, and Asian institutions.",
        "is_active": True,
        "is_upcoming": True
    },
    {
        "name": "Muscat World Universities Conclave 2027",
        "city": "Muscat",
        "venue": "Oman Convention & Exhibition Centre (OCEC)",
        "timings": "09:00 AM – 05:30 PM Daily",
        "start_date": datetime.date(2027, 3, 15),
        "end_date": datetime.date(2027, 3, 17),
        "description": "Sultanate of Oman's national platform for global academic opportunities, undergraduate admissions, and research grants.",
        "is_active": True,
        "is_upcoming": True
    },
    {
        "name": "Kuwait City Global Campus Summit 2027",
        "city": "Kuwait City",
        "venue": "Kuwait International Fairground, Mishref",
        "timings": "10:00 AM – 07:00 PM Daily",
        "start_date": datetime.date(2027, 3, 22),
        "end_date": datetime.date(2027, 3, 24),
        "description": "International educational summit for undergraduate and postgraduate scholars seeking accredited international pathways.",
        "is_active": True,
        "is_upcoming": True
    },
    {
        "name": "Sharjah International Campus Congress 2027",
        "city": "Sharjah",
        "venue": "Expo Centre Sharjah, Al Taawun",
        "timings": "10:00 AM – 06:00 PM Daily",
        "start_date": datetime.date(2027, 3, 28),
        "end_date": datetime.date(2027, 3, 30),
        "description": "Northern Emirates regional hub for university discovery, student portfolio reviews, and fast-track admissions.",
        "is_active": True,
        "is_upcoming": True
    },
    {
        "name": "London Global Academic Summit 2027",
        "city": "London",
        "venue": "ExCeL London International Auditorium",
        "timings": "09:30 AM – 05:30 PM Daily",
        "start_date": datetime.date(2027, 4, 12),
        "end_date": datetime.date(2027, 4, 14),
        "description": "International academic consortium connecting top UK, Commonwealth, and European research leaders.",
        "is_active": True,
        "is_upcoming": True
    },
    {
        "name": "Singapore World Higher Education Concourse 2027",
        "city": "Singapore",
        "venue": "Suntec Singapore Convention & Exhibition Centre",
        "timings": "10:00 AM – 06:30 PM Daily",
        "start_date": datetime.date(2027, 4, 20),
        "end_date": datetime.date(2027, 4, 22),
        "description": "Asia-Pacific centerpiece convention for international admissions, double-degree programs, and global STEM research.",
        "is_active": True,
        "is_upcoming": True
    }
]

created_events = []
for ev in events_data:
    obj = EventLocation.objects.create(**ev)
    created_events.append(obj)
print(f"Created {len(created_events)} EventLocation records.")

print("\n--- Step 3: Seed 10 World-Renowned Universities & Profiles ---")
University.objects.all().delete()
UniversityProfile.objects.all().delete()

unis_data = [
    {
        "name": "Massachusetts Institute of Technology",
        "slug": "mit",
        "city": "Cambridge",
        "country": "United States",
        "website": "https://www.mit.edu",
        "est": 1861,
        "type": "Private Research University",
        "accreditation": "NECHE Accredited",
        "desc": "Global leader in technology, artificial intelligence, physical sciences, and aerospace engineering.",
        "hero_priority": 1
    },
    {
        "name": "Stanford University",
        "slug": "stanford",
        "city": "Stanford",
        "country": "United States",
        "website": "https://www.stanford.edu",
        "est": 1885,
        "type": "Private Research University",
        "accreditation": "WSCUC Accredited",
        "desc": "World-renowned powerhouse of innovation, entrepreneurship, computer science, and medical research.",
        "hero_priority": 2
    },
    {
        "name": "University of Oxford",
        "slug": "oxford",
        "city": "Oxford",
        "country": "United Kingdom",
        "website": "https://www.ox.ac.uk",
        "est": 1096,
        "type": "Public Collegiate University",
        "accreditation": "Privy Council UK",
        "desc": "The oldest university in the English-speaking world, offering peerless collegiate scholarship and research.",
        "hero_priority": 3
    },
    {
        "name": "University of Cambridge",
        "slug": "cambridge",
        "city": "Cambridge",
        "country": "United Kingdom",
        "website": "https://www.cam.ac.uk",
        "est": 1209,
        "type": "Public Collegiate University",
        "accreditation": "Privy Council UK",
        "desc": "Renowned for scientific breakthroughs, mathematics, Nobel laureates, and historic collegiate excellence.",
        "hero_priority": 4
    },
    {
        "name": "Harvard University",
        "slug": "harvard",
        "city": "Cambridge",
        "country": "United States",
        "website": "https://www.harvard.edu",
        "est": 1636,
        "type": "Private Ivy League University",
        "accreditation": "NECHE Accredited",
        "desc": "Historic Ivy League institution producing world leaders, groundbreaking researchers, and international scholars.",
        "hero_priority": 5
    },
    {
        "name": "Imperial College London",
        "slug": "imperial",
        "city": "London",
        "country": "United Kingdom",
        "website": "https://www.imperial.ac.uk",
        "est": 1907,
        "type": "Public Research University",
        "accreditation": "Privy Council UK",
        "desc": "Exclusively focused on science, engineering, medicine, and business, ranked among the top global STEM institutions.",
        "hero_priority": 6
    },
    {
        "name": "National University of Singapore",
        "slug": "nus",
        "city": "Singapore",
        "country": "Singapore",
        "website": "https://nus.edu.sg",
        "est": 1905,
        "type": "National Autonomous University",
        "accreditation": "Ministry of Education Singapore",
        "desc": "Asia's premier flagship university offering transformative global education and cutting-edge research.",
        "hero_priority": 7
    },
    {
        "name": "ETH Zurich",
        "slug": "eth",
        "city": "Zurich",
        "country": "Switzerland",
        "website": "https://ethz.ch",
        "est": 1855,
        "type": "Federal Institute of Technology",
        "accreditation": "Swiss Federal Accreditation",
        "desc": "Premier continental European university for science, mathematics, computer science, and engineering.",
        "hero_priority": 8
    },
    {
        "name": "University of Toronto",
        "slug": "toronto",
        "city": "Toronto",
        "country": "Canada",
        "website": "https://www.utoronto.ca",
        "est": 1827,
        "type": "Public Research University",
        "accreditation": "Ontario Universities Council",
        "desc": "Canada's foremost university, leading international research in artificial intelligence, medicine, and humanities.",
        "hero_priority": 9
    },
    {
        "name": "Technical University of Munich",
        "slug": "tum",
        "city": "Munich",
        "country": "Germany",
        "website": "https://www.tum.de",
        "est": 1868,
        "type": "State University of Technology",
        "accreditation": "Bavarian State Ministry",
        "desc": "Germany's top-ranked technical university, driving innovation in engineering, robotics, and applied physics.",
        "hero_priority": 10
    }
]

created_unis = []
for u_data in unis_data:
    uni = University.objects.create(
        name=u_data["name"],
        slug=u_data["slug"],
        is_approved=True,
        hero_priority=u_data["hero_priority"]
    )
    UniversityProfile.objects.create(
        university=uni,
        location_city=u_data["city"],
        location_state_country=u_data["country"],
        website=u_data["website"],
        established_year=u_data["est"],
        university_type=u_data["type"],
        accreditation=u_data["accreditation"],
        short_description=u_data["desc"],
        about=f"{u_data['name']} is recognized internationally for world-class academics, distinguished faculty, and groundbreaking research contributions."
    )
    created_unis.append(uni)

print(f"Created {len(created_unis)} University and UniversityProfile records.")

print("\n--- Step 4: Seed 10 Course Categories & 10 Accredited Courses ---")
CourseCategory.objects.all().delete()
Course.objects.all().delete()

categories_data = [
    "Computer Science & Artificial Intelligence",
    "Business Administration & Management",
    "Engineering & Robotics",
    "Medicine & Biomedical Sciences",
    "Law & International Relations",
    "Data Science & Applied Mathematics",
    "Physical & Natural Sciences",
    "Architecture & Sustainable Design",
    "Economics & Global Finance",
    "Aerospace & Mechanical Engineering"
]

cat_objs = [CourseCategory.objects.create(name=c) for c in categories_data]
print(f"Created {len(cat_objs)} CourseCategory records.")

courses_data = [
    {
        "name": "BSc Computer Science & Artificial Intelligence",
        "uni": created_unis[0], # MIT
        "cat": cat_objs[0],
        "degree": "Bachelor of Science",
        "stream": "Computer Science",
        "duration": "4 Years",
        "mode": "Full-Time On-Campus",
        "eligibility": "High School Diploma with Advanced Mathematics & Physics (Min 92% or 3.8 GPA)",
        "fees": "$57,590 / Year",
        "sch": True
    },
    {
        "name": "BSc Symbolic Systems & Machine Learning",
        "uni": created_unis[1], # Stanford
        "cat": cat_objs[0],
        "degree": "Bachelor of Science",
        "stream": "Artificial Intelligence",
        "duration": "4 Years",
        "mode": "Full-Time On-Campus",
        "eligibility": "Top 5% Class Rank, SAT 1500+ or ACT 34+, Calculus Proficiency",
        "fees": "$61,731 / Year",
        "sch": True
    },
    {
        "name": "BA Philosophy, Politics and Economics (PPE)",
        "uni": created_unis[2], # Oxford
        "cat": cat_objs[4],
        "degree": "Bachelor of Arts",
        "stream": "Humanities & Social Sciences",
        "duration": "3 Years",
        "mode": "Collegiate Tutorial",
        "eligibility": "A-Levels: A*AA or IB: 39 points with 766 at HL",
        "fees": "£38,500 / Year",
        "sch": True
    },
    {
        "name": "BA Natural Sciences (Physical & Biological)",
        "uni": created_unis[3], # Cambridge
        "cat": cat_objs[6],
        "degree": "Bachelor of Arts",
        "stream": "Natural Sciences",
        "duration": "3-4 Years",
        "mode": "Collegiate Tutorial & Laboratory",
        "eligibility": "A-Levels: A*A*A in Sciences/Maths or IB: 40-42 points",
        "fees": "£39,162 / Year",
        "sch": True
    },
    {
        "name": "Master of Business Administration (MBA)",
        "uni": created_unis[4], # Harvard
        "cat": cat_objs[1],
        "degree": "Master of Business Administration",
        "stream": "Executive Management",
        "duration": "2 Years",
        "mode": "Full-Time Case Study Method",
        "eligibility": "Accredited Bachelor's Degree, 2+ Years Professional Experience, GMAT 730+",
        "fees": "$74,910 / Year",
        "sch": True
    },
    {
        "name": "MEng Computing & Software Engineering",
        "uni": created_unis[5], # Imperial
        "cat": cat_objs[2],
        "degree": "Master of Engineering",
        "stream": "Software Engineering",
        "duration": "4 Years Integrated Master",
        "mode": "Full-Time Laboratory & Project",
        "eligibility": "A-Levels: A*A*A (Maths required) or IB: 39-40 points",
        "fees": "£37,900 / Year",
        "sch": True
    },
    {
        "name": "BSc Data Science and Analytics",
        "uni": created_unis[6], # NUS
        "cat": cat_objs[5],
        "degree": "Bachelor of Science",
        "stream": "Data Science",
        "duration": "4 Years",
        "mode": "Full-Time Modular",
        "eligibility": "Senior High School Diploma with Strong Foundation in Mathematics",
        "fees": "SGD 38,200 / Year",
        "sch": True
    },
    {
        "name": "MSc Robotics, Systems and Control",
        "uni": created_unis[7], # ETH Zurich
        "cat": cat_objs[2],
        "degree": "Master of Science",
        "stream": "Robotics Engineering",
        "duration": "2 Years",
        "mode": "Full-Time Research & Lab",
        "eligibility": "Bachelor's Degree in Mechanical, Electrical Engineering or Computer Science",
        "fees": "CHF 1,460 / Year",
        "sch": True
    },
    {
        "name": "BSc International Relations & Global Economics",
        "uni": created_unis[8], # Toronto
        "cat": cat_objs[8],
        "degree": "Bachelor of Science",
        "stream": "Economics & Public Policy",
        "duration": "4 Years",
        "mode": "Full-Time Lecture & Seminar",
        "eligibility": "Senior High School Completion, Grade 12 Calculus & English (Min 88%)",
        "fees": "CAD 58,160 / Year",
        "sch": True
    },
    {
        "name": "MSc Aerospace Engineering",
        "uni": created_unis[9], # TU Munich
        "cat": cat_objs[9],
        "degree": "Master of Science",
        "stream": "Aerospace Engineering",
        "duration": "2 Years",
        "mode": "Full-Time Technical & Research",
        "eligibility": "BSc in Aerospace, Mechanical Engineering or equivalent, GRE & English C1",
        "fees": "€4,000 / Year",
        "sch": True
    }
]

created_courses = []
for c_data in courses_data:
    crs = Course.objects.create(
        university=c_data["uni"],
        category=c_data["cat"],
        name=c_data["name"],
        degree_type=c_data["degree"],
        stream=c_data["stream"],
        duration=c_data["duration"],
        mode=c_data["mode"],
        eligibility=c_data["eligibility"],
        fees=c_data["fees"],
        scholarship_available=c_data["sch"],
        is_active=True,
        status="active"
    )
    created_courses.append(crs)

print(f"Created {len(created_courses)} Course records.")

print("\n--- Step 5: Seed 10 Prestigious Scholarships ---")
Scholarship.objects.all().delete()

scholarships_data = [
    {
        "name": "MIT Presidential Graduate Fellowship",
        "uni": created_unis[0],
        "amount": "$55,000 / Year + Full Tuition",
        "coverage": "Full Tuition & Living Stipend",
        "field": "Engineering, Computer Science, Physical Sciences",
        "level": "Postgraduate / PhD",
        "eligibility": "Outstanding academic record, research excellence, and departmental nomination.",
        "deadline": datetime.date(2027, 4, 15),
        "desc": "Prestigious merit fellowship covering full tuition, medical insurance, and a monthly research stipend."
    },
    {
        "name": "Stanford Knight-Hennessy Scholars Program",
        "uni": created_unis[1],
        "amount": "$85,000 / Year",
        "coverage": "Full Ride Tuition, Housing & Travel Grant",
        "field": "All Disciplines",
        "level": "Graduate / Master's / PhD",
        "eligibility": "Visionary leadership, independent thought, and admission to any Stanford graduate program.",
        "deadline": datetime.date(2027, 4, 30),
        "desc": "Cultivates a multidisciplinary community of global leaders addressing society's complex challenges."
    },
    {
        "name": "Rhodes Global Scholarship",
        "uni": created_unis[2],
        "amount": "£52,000 / Year",
        "coverage": "Full University & College Fees + Annual Stipend",
        "field": "All Disciplines",
        "level": "Postgraduate",
        "eligibility": "Exceptional intellect, moral character, leadership potential, and energy to use one's talents.",
        "deadline": datetime.date(2027, 5, 1),
        "desc": "The world's oldest and most renowned graduate scholarship for study at the University of Oxford."
    },
    {
        "name": "Gates Cambridge International Trust",
        "uni": created_unis[3],
        "amount": "£48,000 / Year",
        "coverage": "Full Cost of Study + Maintenance Allowance",
        "field": "All Postgraduate Subjects",
        "level": "Postgraduate / Master's / PhD",
        "eligibility": "Outstanding intellectual ability, reasons for choice of course, and commitment to improving others' lives.",
        "deadline": datetime.date(2027, 5, 10),
        "desc": "Global scholarship established by the Bill & Melinda Gates Foundation for scholars outside the UK."
    },
    {
        "name": "Harvard Global Leadership Merit Grant",
        "uni": created_unis[4],
        "amount": "$65,000 / Year",
        "coverage": "Tuition Grant & Living Subsidy",
        "field": "Business, Public Policy, Law",
        "level": "Graduate / Master's",
        "eligibility": "Demonstrated record of social impact, ethical leadership, and academic distinction.",
        "deadline": datetime.date(2027, 5, 15),
        "desc": "Need-and-merit blended award enabling visionary international candidates to pursue leadership degrees."
    },
    {
        "name": "Imperial President's Undergraduate Scholarship",
        "uni": created_unis[5],
        "amount": "£32,000 / Year",
        "coverage": "Tuition Reduction & Annual Academic Allowance",
        "field": "Science, Technology, Engineering, Medicine",
        "level": "Undergraduate",
        "eligibility": "Exceptional A-Level or IB performance, outstanding admissions assessment results.",
        "deadline": datetime.date(2027, 5, 20),
        "desc": "Awarded to the most academically gifted undergraduate applicants across all STEM faculties."
    },
    {
        "name": "Singapore Commonwealth Academic Fellowship",
        "uni": created_unis[6],
        "amount": "SGD 42,000 / Year",
        "coverage": "Full Tuition Waiver & Monthly Living Allowance",
        "field": "Computing, Data Analytics, Engineering",
        "level": "Undergraduate & Postgraduate",
        "eligibility": "Citizen of Commonwealth or GCC partner nation, top 5% academic standing.",
        "deadline": datetime.date(2027, 5, 25),
        "desc": "Fosters international educational collaboration and research innovation in Singapore."
    },
    {
        "name": "Swiss Government Excellence Fellowship",
        "uni": created_unis[7],
        "amount": "CHF 38,000 / Year",
        "coverage": "Full Tuition Exemption, Monthly Living Allowance & Health Insurance",
        "field": "Robotics, Engineering, Natural Sciences",
        "level": "Postgraduate / PhD",
        "eligibility": "Graduates holding a recognised Master's degree with high academic distinction.",
        "deadline": datetime.date(2027, 5, 30),
        "desc": "Conferred by the Swiss Federal Commission for Scholarships for Foreign Students."
    },
    {
        "name": "Lester B. Pearson International Scholarship",
        "uni": created_unis[8],
        "amount": "CAD 68,000 / Year",
        "coverage": "Full Tuition, Books, Incidental Fees & Residence Support",
        "field": "All Undergraduate Faculties",
        "level": "Undergraduate",
        "eligibility": "Nomination by secondary school, exceptional academic achievement, and creative leadership.",
        "deadline": datetime.date(2027, 6, 5),
        "desc": "The University of Toronto's most prestigious competitive international undergraduate award."
    },
    {
        "name": "DAAD German Academic Exchange Fellowship",
        "uni": created_unis[9],
        "amount": "€28,000 / Year",
        "coverage": "Monthly Stipend, Travel Allowance & Comprehensive Insurance",
        "field": "Aerospace, Mechanical Engineering, Physics",
        "level": "Master's & PhD",
        "eligibility": "Completed Bachelor's degree with outstanding grades within the last 6 years.",
        "deadline": datetime.date(2027, 6, 15),
        "desc": "Germany's flagship scholarship supporting premier international engineers at TU Munich."
    }
]

created_schs = []
for s_data in scholarships_data:
    sch = Scholarship.objects.create(
        university=s_data["uni"],
        name=s_data["name"],
        amount=s_data["amount"],
        coverage_type=s_data["coverage"],
        field_of_study=s_data["field"],
        level=s_data["level"],
        eligibility=s_data["eligibility"],
        deadline=s_data["deadline"],
        category="Merit",
        description=s_data["desc"],
        status="active"
    )
    created_schs.append(sch)

print(f"Created {len(created_schs)} Scholarship records.")

print("\n--- Step 6: Seed 10 Exhibitors & 10 Expo Floor Booths ---")
Exhibitor.objects.all().delete()
ExpoBooth.objects.all().delete()

dubai_event = created_events[0]

exhibitors_data = [
    {"name": "MIT Global Admissions Bureau", "uni": created_unis[0], "booth": "Booth A-01", "tuition": "$57,590", "programs": "Engineering, Computer Science, Physics"},
    {"name": "Stanford University International Bureau", "uni": created_unis[1], "booth": "Booth A-02", "tuition": "$61,731", "programs": "AI, Bioengineering, Business"},
    {"name": "University of Oxford Admissions Directorate", "uni": created_unis[2], "booth": "Booth A-03", "tuition": "£38,500", "programs": "PPE, Medicine, Law, Sciences"},
    {"name": "Cambridge University Admissions Bureau", "uni": created_unis[3], "booth": "Booth A-04", "tuition": "£39,162", "programs": "Natural Sciences, Engineering, Mathematics"},
    {"name": "Harvard University Global Office", "uni": created_unis[4], "booth": "Booth A-05", "tuition": "$56,550", "programs": "Liberal Arts, Economics, MBA, Public Policy"},
    {"name": "Imperial College London Admissions Desk", "uni": created_unis[5], "booth": "Booth A-06", "tuition": "£37,900", "programs": "Computing, Mechanical Engineering, Medicine"},
    {"name": "National University of Singapore (NUS) Desk", "uni": created_unis[6], "booth": "Booth A-07", "tuition": "SGD 38,200", "programs": "Data Science, Biomedical Sciences, Law"},
    {"name": "ETH Zurich Swiss Higher Education Pavilion", "uni": created_unis[7], "booth": "Booth A-08", "tuition": "CHF 1,460", "programs": "Robotics, Architecture, Mathematics"},
    {"name": "University of Toronto Global Admissions", "uni": created_unis[8], "booth": "Booth A-09", "tuition": "CAD 58,160", "programs": "Global Economics, AI, Life Sciences"},
    {"name": "Technical University of Munich International Hub", "uni": created_unis[9], "booth": "Booth A-10", "tuition": "€4,000", "programs": "Aerospace, Robotics, Automotive Tech"}
]

created_exhs = []
for idx, ed in enumerate(exhibitors_data):
    exh = Exhibitor.objects.create(
        company_name=ed["name"],
        event_location=dubai_event,
        profile_description=f"Official representative booth of {ed['uni'].name} at the Dubai International Higher Education Expo.",
        website=ed["uni"].profile.website,
        country=ed["uni"].profile.location_state_country,
        tuition_range=ed["tuition"],
        offered_programs=ed["programs"],
        is_verified=True
    )
    # Assign booth to university (per project model rule: university and exhibitor are mutually exclusive)
    booth = ExpoBooth.objects.create(
        booth_number=ed["booth"],
        hall="Hall 1 - Global Pavilion",
        university=ed["uni"],
        status="confirmed",
        display_info=f"{ed['uni'].name} - {ed['booth']}",
        is_active=True
    )
    created_exhs.append(exh)

print(f"Created {len(created_exhs)} Exhibitor records and 10 ExpoBooth records.")

print("\n--- Step 7: Seed 10 Distinguished Keynote Speakers ---")
Speaker.objects.all().delete()

speakers_data = [
    {
        "name": "Prof. David Miller",
        "title": "Vice Provost of Academic Partnerships",
        "org": "Massachusetts Institute of Technology",
        "profile": "Pioneer in artificial intelligence and autonomous systems curriculum design across international faculties."
    },
    {
        "name": "Dr. Elena Rostova",
        "title": "Dean of Graduate Admissions",
        "org": "Stanford University",
        "profile": "Expert on global STEM recruitment, entrepreneurial venture fellowships, and Silicon Valley career pipelines."
    },
    {
        "name": "Prof. Marcus Vance",
        "title": "Senior Dean of Collegiate Admissions",
        "org": "University of Oxford",
        "profile": "Leading authority on undergraduate tutorial pedagogy, PPE admissions, and international Rhodes candidate selection."
    },
    {
        "name": "Dr. Arthur Pendelton",
        "title": "Director of Global Academic Mobility",
        "org": "University of Cambridge",
        "profile": "Spearheads European and Middle Eastern academic exchange, Gates Cambridge trust evaluation, and research mobility."
    },
    {
        "name": "Prof. Evelyn Carter",
        "title": "Senior Fellow in Public Policy & Management",
        "org": "Harvard University",
        "profile": "Consultant to international education ministries on higher education equity, merit grants, and executive leadership."
    },
    {
        "name": "Dr. Julian Thorne",
        "title": "Head of STEM International Admissions",
        "org": "Imperial College London",
        "profile": "Champion of global engineering standards, clean energy research pathways, and undergraduate scientific grants."
    },
    {
        "name": "Prof. Kenji Takahashi",
        "title": "Dean of Computing & Analytics",
        "org": "National University of Singapore",
        "profile": "Architect of Asia's premier computing degree partnerships and Singapore's National AI curriculum."
    },
    {
        "name": "Dr. Christian Meyer",
        "title": "Director of Robotics & Systems Research",
        "org": "ETH Zurich",
        "profile": "Renowned roboticist driving collaborative research between Swiss universities and GCC engineering academies."
    },
    {
        "name": "Prof. Amina Al-Mansoor",
        "title": "Senior Advisor for MENA Education",
        "org": "University of Toronto",
        "profile": "Specialist in international student mobility, Canadian study-work transition frameworks, and research awards."
    },
    {
        "name": "Dr. Hans Weber",
        "title": "Chair of Aerospace Engineering Programs",
        "org": "Technical University of Munich",
        "profile": "Leader in aerospace design and European industrial integration for international engineering graduates."
    }
]

created_speakers = []
for s_info in speakers_data:
    spk = Speaker.objects.create(
        name=s_info["name"],
        title=s_info["title"],
        organization=s_info["org"],
        profile=s_info["profile"],
        is_verified=True
    )
    created_speakers.append(spk)

print(f"Created {len(created_speakers)} Speaker records.")

print("\n--- Step 8: Seed 10 Programme & Masterclass Sessions ---")
ProgrammeSession.objects.all().delete()

sessions_data = [
    {
        "title": "Keynote: The Future of Global Higher Education & AI Degrees",
        "spk": created_speakers[0],
        "date": datetime.date(2027, 2, 10),
        "start": datetime.time(10, 0),
        "end": datetime.time(11, 15),
        "hall": "Main Auditorium A",
        "desc": "How top-tier universities are reshaping degree pathways around artificial intelligence, robotics, and global problem solving."
    },
    {
        "title": "Admissions Masterclass: Securing Full-Ride Scholarships in the USA",
        "spk": created_speakers[1],
        "date": datetime.date(2027, 2, 10),
        "start": datetime.time(11, 30),
        "end": datetime.time(12, 45),
        "hall": "Auditorium Hall B",
        "desc": "A comprehensive breakdown of US institutional merit grants, holistic admissions scoring, and competitive application strategies."
    },
    {
        "title": "Collegiate Tutorial Clinic: Excelling in Oxford & Cambridge Admissions",
        "spk": created_speakers[2],
        "date": datetime.date(2027, 2, 10),
        "start": datetime.time(14, 0),
        "end": datetime.time(15, 15),
        "hall": "Pavilion Concourse",
        "desc": "Mastering the Oxbridge academic interview, admissions test assessments, and tutorial teaching expectations."
    },
    {
        "title": "European Engineering Horizons: Pathways in Germany & Switzerland",
        "spk": created_speakers[9],
        "date": datetime.date(2027, 2, 10),
        "start": datetime.time(15, 30),
        "end": datetime.time(16, 45),
        "hall": "Seminar Room 1",
        "desc": "Navigating low-tuition, high-research engineering master's programs at TU Munich, ETH Zurich, and continental hubs."
    },
    {
        "title": "Biotechnology & Medicine Careers: Global Accreditations & Licensing",
        "spk": created_speakers[5],
        "date": datetime.date(2027, 2, 10),
        "start": datetime.time(17, 0),
        "end": datetime.time(18, 15),
        "hall": "Executive Suite",
        "desc": "Guidance on clinical degree pathways, UK General Medical Council (GMC) accreditations, and residency matching."
    },
    {
        "title": "GCC Student Mobility & Global Visa Frameworks Clinic",
        "spk": created_speakers[8],
        "date": datetime.date(2027, 2, 11),
        "start": datetime.time(10, 0),
        "end": datetime.time(11, 15),
        "hall": "Main Auditorium A",
        "desc": "Essential insights into UK Student Visas, US F-1 visas, Canadian Study Permits, and post-study work regulations."
    },
    {
        "title": "Next-Gen Robotics & Autonomous Systems in Continental Europe",
        "spk": created_speakers[7],
        "date": datetime.date(2027, 2, 11),
        "start": datetime.time(11, 30),
        "end": datetime.time(12, 45),
        "hall": "Auditorium Hall B",
        "desc": "How interdisciplinary engineering at ETH Zurich bridges hardware innovation and artificial intelligence."
    },
    {
        "title": "Asia-Pacific Higher Education Hub: Opportunities in Singapore",
        "spk": created_speakers[6],
        "date": datetime.date(2027, 2, 11),
        "start": datetime.time(14, 0),
        "end": datetime.time(15, 15),
        "hall": "Pavilion Concourse",
        "desc": "Exploring world-ranked degree programs, government tuition grants, and high-growth industry placement in Singapore."
    },
    {
        "title": "Executive Leadership & Business Degree ROI in a Changing World",
        "spk": created_speakers[4],
        "date": datetime.date(2027, 2, 11),
        "start": datetime.time(15, 30),
        "end": datetime.time(16, 45),
        "hall": "Executive Suite",
        "desc": "Evaluating MBA, Master of Finance, and public leadership degrees for long-term career acceleration."
    },
    {
        "title": "Cambridge Natural Sciences & Research Grant Masterclass",
        "spk": created_speakers[3],
        "date": datetime.date(2027, 2, 11),
        "start": datetime.time(17, 0),
        "end": datetime.time(18, 15),
        "hall": "Seminar Room 2",
        "desc": "Detailed walkthrough of scientific research proposals, Gates Cambridge fellowships, and postgraduate scholarships."
    }
]

created_sessions = []
for sess in sessions_data:
    ps = ProgrammeSession.objects.create(
        title=sess["title"],
        event_location=dubai_event,
        date=sess["date"],
        start_time=sess["start"],
        end_time=sess["end"],
        hall_name=sess["hall"],
        speaker=sess["spk"],
        description=sess["desc"]
    )
    created_sessions.append(ps)

print(f"Created {len(created_sessions)} ProgrammeSession records.")

print("\n--- Step 9: Seed 10 Global Corporate & Assessment Sponsors ---")
Sponsor.objects.all().delete()

sponsors_data = [
    {
        "name": "Emirates Airlines",
        "cat": "Airline Partner",
        "profile": "Official Global Carrier offering specialized student fares, excess baggage allowances, and flexible flight dates.",
        "url": "https://www.emirates.com"
    },
    {
        "name": "Emirates NBD Bank",
        "cat": "Financial Services",
        "profile": "Official Banking Partner providing preferential education finance, international remittances, and student accounts.",
        "url": "https://www.emiratesnbd.com"
    },
    {
        "name": "Microsoft Education",
        "cat": "Technology Partner",
        "profile": "Delivering cloud computing, Azure student developer grants, and digital campus collaboration platforms.",
        "url": "https://www.microsoft.com/education"
    },
    {
        "name": "ETS TOEFL & GRE",
        "cat": "Testing Authority",
        "profile": "Global benchmark provider for standardized English language and graduate school admissions testing.",
        "url": "https://www.ets.org"
    },
    {
        "name": "Pearson VUE",
        "cat": "Assessment Network",
        "profile": "Worldwide computer-based testing infrastructure delivering secure university entrance examinations.",
        "url": "https://www.pearsonvue.com"
    },
    {
        "name": "British Council IELTS",
        "cat": "Language Assessment",
        "profile": "Co-owner of the world's most recognized English proficiency test for international study and migration.",
        "url": "https://takeielts.britishcouncil.org"
    },
    {
        "name": "Cambridge Assessment English",
        "cat": "Accreditation Partner",
        "profile": "Part of the University of Cambridge, providing globally accredited English certifications accepted worldwide.",
        "url": "https://www.cambridgeenglish.org"
    },
    {
        "name": "Duolingo English Test",
        "cat": "Digital Testing",
        "profile": "Fast, accessible, and affordable online language testing accepted by over 5,000 global universities.",
        "url": "https://englishtest.duolingo.com"
    },
    {
        "name": "QS World University Rankings",
        "cat": "Academic Benchmark",
        "profile": "Global higher education intelligence authority providing institutional rankings, analytics, and student guides.",
        "url": "https://www.topuniversities.com"
    },
    {
        "name": "Lumentra Global Education",
        "cat": "Headline Sponsor",
        "profile": "International foundation dedicated to funding merit scholarships, student advisory, and cross-border education access.",
        "url": "https://www.lumentra.org"
    }
]

created_sponsors = []
for sp_info in sponsors_data:
    sp_obj = Sponsor.objects.create(
        name=sp_info["name"],
        category=sp_info["cat"],
        event_location=dubai_event,
        profile=sp_info["profile"],
        website=sp_info["url"],
        is_verified=True
    )
    created_sponsors.append(sp_obj)

print(f"Created {len(created_sponsors)} Sponsor records.")

print("\n--- Step 10: Seed 1 Official Scholarship Exam & 10 Aptitude Questions ---")
ScholarshipExam.objects.all().delete()
ExamQuestion.objects.all().delete()
QuestionChoice.objects.all().delete()

official_exam = ScholarshipExam.objects.create(
    title="KNOVA 2027 Global Academic Assessment & Scholarship Eligibility Exam",
    description="Standardized computer-based assessment evaluating Quantitative Reasoning, Critical Analysis, and Verbal Logic for merit scholarship qualification.",
    duration_minutes=45,
    total_marks=100,
    passing_marks=60,
    is_active=True,
    start_date=timezone.now() - datetime.timedelta(days=1),
    end_date=timezone.now() + datetime.timedelta(days=90)
)

questions_data = [
    {
        "text": "If a university scholarship fund increases its total endowment by 15% in the first year and then distributes 20% of the new total in merit awards, what is the net percentage change in the fund relative to the original principal?",
        "section": "Quantitative Problem Solving",
        "marks": 10,
        "choices": [
            ("An 8% net decrease", True),
            ("A 5% net decrease", False),
            ("A 10% net decrease", False),
            ("No net change", False)
        ]
    },
    {
        "text": "Five academic delegates (A, B, C, D, and E) are seated in a row at a keynote seminar. If A cannot sit next to B, and C must sit immediately to the left of D, how many valid seating arrangements exist if E sits at either extreme end?",
        "section": "Analytical Reasoning",
        "marks": 10,
        "choices": [
            ("20 arrangements", True),
            ("14 arrangements", False),
            ("28 arrangements", False),
            ("16 arrangements", False)
        ]
    },
    {
        "text": "Identify the logical flaw: 'All accredited universities possess advanced research facilities. University X possesses an advanced research facility; therefore, University X is accredited.'",
        "section": "Critical Thinking & Logic",
        "marks": 10,
        "choices": [
            ("Affirming the consequent (fallacy of the converse)", True),
            ("Denying the antecedent", False),
            ("Equivocation of terms", False),
            ("Begging the question", False)
        ]
    },
    {
        "text": "A student travels from Campus A to Campus B at an average speed of 60 km/h, and returns along the identical route at an average speed of 40 km/h. What is the average speed for the entire round trip?",
        "section": "Quantitative Problem Solving",
        "marks": 10,
        "choices": [
            ("48 km/h", True),
            ("50 km/h", False),
            ("46 km/h", False),
            ("52 km/h", False)
        ]
    },
    {
        "text": "Which word most accurately completes the analogy: EMPIRICAL : EVIDENCE :: HYPOTHETICAL : ________?",
        "section": "Verbal Reasoning",
        "marks": 10,
        "choices": [
            ("Conjecture", True),
            ("Verification", False),
            ("Certainty", False),
            ("Measurement", False)
        ]
    },
    {
        "text": "If statement 'No candidate who fails the prerequisite may enroll in the honors seminar' is TRUE, which of the following MUST also be true?",
        "section": "Formal Logic",
        "marks": 10,
        "choices": [
            ("Every candidate enrolled in the honors seminar passed the prerequisite", True),
            ("Every candidate who passes the prerequisite enrolls in the honors seminar", False),
            ("No candidate who passes the prerequisite fails the honors seminar", False),
            ("Candidates failing the honors seminar must have failed the prerequisite", False)
        ]
    },
    {
        "text": "A university laboratory archives 120 research samples. If 75% are classified as organic compounds, and 40% of those organic compounds are derived from botanical flora, exactly how many non-botanical organic samples are cataloged?",
        "section": "Quantitative Problem Solving",
        "marks": 10,
        "choices": [
            ("54 samples", True),
            ("36 samples", False),
            ("48 samples", False),
            ("62 samples", False)
        ]
    },
    {
        "text": "If 8 scholars require 6 hours to grade 240 research theses, how many hours would 12 scholars working at the identical pace require to grade 480 research theses?",
        "section": "Quantitative Problem Solving",
        "marks": 10,
        "choices": [
            ("8 hours", True),
            ("6 hours", False),
            ("10 hours", False),
            ("9 hours", False)
        ]
    },
    {
        "text": "Choose the most grammatically precise sentence for academic publication:",
        "section": "Verbal Reasoning & Grammar",
        "marks": 10,
        "choices": [
            ("Neither the lead researcher nor the laboratory assistants were able to replicate the anomaly.", True),
            ("Neither the lead researcher nor the laboratory assistants was able to replicate the anomaly.", False),
            ("Neither the lead researcher or the laboratory assistants were able to replicate the anomaly.", False),
            ("Either the lead researcher nor the laboratory assistants were able to replicate the anomaly.", False)
        ]
    },
    {
        "text": "In a competitive admission cohort, applicant P scored higher than Q but lower than R. Applicant S scored higher than T but lower than Q. Who achieved the median score among the five applicants?",
        "section": "Analytical Reasoning",
        "marks": 10,
        "choices": [
            ("Applicant Q", True),
            ("Applicant P", False),
            ("Applicant S", False),
            ("Applicant R", False)
        ]
    }
]

created_questions = []
for idx, q_info in enumerate(questions_data):
    q_obj = ExamQuestion.objects.create(
        exam=official_exam,
        section_name=q_info["section"],
        text=q_info["text"],
        marks=q_info["marks"],
        order=idx + 1
    )
    for c_text, is_corr in q_info["choices"]:
        QuestionChoice.objects.create(
            question=q_obj,
            text=c_text,
            is_correct=is_corr
        )
    created_questions.append(q_obj)

print(f"Created ScholarshipExam with {len(created_questions)} ExamQuestion records and 40 QuestionChoices.")

print("\n--- Step 11: Seed 10 Authentic Registered Attendees ---")
Registration.objects.all().delete()

attendees_data = [
    {
        "name": "Alexander Wright",
        "email": "alexander.wright@knova.org",
        "phone": "+971 50 123 4567",
        "country": "United Arab Emirates",
        "prog": "Computer Science & Artificial Intelligence",
        "budget": "$40k - $60k",
        "id": "KNV-REG-1001"
    },
    {
        "name": "Sophia Al-Nuaimi",
        "email": "sophia.nuaimi@gmail.com",
        "phone": "+971 52 987 6543",
        "country": "United Arab Emirates",
        "prog": "Biomedical Engineering & Medicine",
        "budget": "Full Scholarship Required",
        "id": "KNV-REG-1002"
    },
    {
        "name": "Noah Al-Kuwari",
        "email": "noah.kuwari@outlook.com",
        "phone": "+974 55 123 789",
        "country": "Qatar",
        "prog": "Mechanical & Aerospace Engineering",
        "budget": "$30k - $50k",
        "id": "KNV-REG-1003"
    },
    {
        "name": "Emma Watson",
        "email": "emma.watson@yahoo.com",
        "phone": "+966 50 234 5678",
        "country": "Saudi Arabia",
        "prog": "International Relations & PPE",
        "budget": "Full Scholarship Required",
        "id": "KNV-REG-1004"
    },
    {
        "name": "Oliver Davies",
        "email": "oliver.davies@gmail.com",
        "phone": "+973 39 876 543",
        "country": "Bahrain",
        "prog": "Finance & Global Economics",
        "budget": "$25k - $45k",
        "id": "KNV-REG-1005"
    },
    {
        "name": "Isabella Rossi",
        "email": "isabella.rossi@icloud.com",
        "phone": "+968 91 234 567",
        "country": "Oman",
        "prog": "Architecture & Sustainable Urbanism",
        "budget": "$35k - $55k",
        "id": "KNV-REG-1006"
    },
    {
        "name": "Ethan Chen",
        "email": "ethan.chen@gmail.com",
        "phone": "+965 99 876 543",
        "country": "Kuwait",
        "prog": "Data Science & Applied Mathematics",
        "budget": "Full Scholarship Required",
        "id": "KNV-REG-1007"
    },
    {
        "name": "Mia Tanaka",
        "email": "mia.tanaka@outlook.com",
        "phone": "+971 55 456 7890",
        "country": "United Arab Emirates",
        "prog": "Robotics & Software Engineering",
        "budget": "$40k - $60k",
        "id": "KNV-REG-1008"
    },
    {
        "name": "Lucas Silva",
        "email": "lucas.silva@gmail.com",
        "phone": "+966 54 321 0987",
        "country": "Saudi Arabia",
        "prog": "Master of Business Administration (MBA)",
        "budget": "$50k+",
        "id": "KNV-REG-1009"
    },
    {
        "name": "Amira Mansour",
        "email": "amira.mansour@hotmail.com",
        "phone": "+971 56 789 0123",
        "country": "United Arab Emirates",
        "prog": "Physics & Quantum Computing",
        "budget": "Full Scholarship Required",
        "id": "KNV-REG-1010"
    }
]

created_regs = []
now_time = timezone.now()
for idx, att in enumerate(attendees_data):
    reg = Registration.objects.create(
        full_name=att["name"],
        email=att["email"],
        phone=att["phone"],
        role="Student",
        event_location=dubai_event,
        preferred_country=att["country"],
        budget_range=att["budget"],
        preferred_program=att["prog"],
        status="Confirmed",
        registered_at=now_time - datetime.timedelta(days=idx, hours=idx*2),
        is_checked_in=(idx % 2 == 0),
        registration_id=att["id"]
    )
    created_regs.append(reg)

print(f"Created {len(created_regs)} Registration records.")

print("\n--- Step 12: Seed 10 Floor Activity Zones ---")
FloorActivityZone.objects.all().delete()

zones_data = [
    {
        "name": "Global University Pavilion",
        "tagline": "Direct Admissions & Deans Consultations",
        "hall": "Hall 1 Main Concourse",
        "badge": "Admissions Hub",
        "icon": "ti-school",
        "color": "#1768ff",
        "desc": "Consult directly with admissions deans and international representatives from 10 world-ranked universities.",
        "activities": "One-on-one evaluations, transcript reviews, brochure collections, admission fast-track interviews.",
        "order": 1
    },
    {
        "name": "Keynote & Leadership Auditorium",
        "tagline": "World-Class Seminars & Academic Vision",
        "hall": "Auditorium A",
        "badge": "Conference Hall",
        "icon": "ti-presentation",
        "color": "#7c3aed",
        "desc": "Daily keynote presentations from distinguished university rectors, deans, and higher education policymakers.",
        "activities": "Keynote masterclasses, visa frameworks, industry ROI presentations, panel discussions.",
        "order": 2
    },
    {
        "name": "STEM & Artificial Intelligence Arena",
        "tagline": "Robotics, Computing & Applied Sciences",
        "hall": "Hall 2 East",
        "badge": "Tech Pavilion",
        "icon": "ti-cpu",
        "color": "#0ea5e9",
        "desc": "Showcase of cutting-edge research in robotics, generative AI, aerospace engineering, and clean energy.",
        "activities": "Live robotic demos, AI curriculum breakdowns, research laboratory overviews, project showcases.",
        "order": 3
    },
    {
        "name": "Scholarship & Financial Aid Atrium",
        "tagline": "Funding Grants & Merit Fee Waivers",
        "hall": "Central Concourse",
        "badge": "$5M+ Aid Hub",
        "icon": "ti-coin",
        "color": "#10b981",
        "desc": "Dedicated counselors helping students qualify for full-ride fellowships, government scholarships, and tuition waivers.",
        "activities": "Merit eligibility pre-screening, financial documentation assistance, government grant guidance.",
        "order": 4
    },
    {
        "name": "One-on-One Dean Counselling Lounge",
        "tagline": "Personalized Academic Strategy",
        "hall": "Hall 1 North Suite",
        "badge": "Advisory Suite",
        "icon": "ti-users",
        "color": "#f59e0b",
        "desc": "Private 15-minute consultations with university deans to evaluate academic portfolios and career trajectories.",
        "activities": "Personal statement critique, grade conversion guidance, collegiate selection advisory.",
        "order": 5
    },
    {
        "name": "Language & Diagnostic Examination Hub",
        "tagline": "IELTS, TOEFL, Duolingo & CBT Testing",
        "hall": "Hall 2 West",
        "badge": "Testing Center",
        "icon": "ti-certificate",
        "color": "#ec4899",
        "desc": "Official testing partners providing free diagnostic assessments, mock exam terminals, and score report advice.",
        "activities": "Live CBT aptitude testing, English diagnostic exams, scoring rubrics consultations.",
        "order": 6
    },
    {
        "name": "Visa & Student Mobility Pavilion",
        "tagline": "Consular & Immigration Compliance",
        "hall": "Pavilion Concourse",
        "badge": "Embassy Clinic",
        "icon": "ti-passport",
        "color": "#6366f1",
        "desc": "Direct workshops from certified international mobility advisors on study visas, work permits, and accommodation.",
        "activities": "UK Tier-4 briefings, US F-1 visa preparation, Schengen mobility advisory, banking proof workshops.",
        "order": 7
    },
    {
        "name": "Graduate & MBA Executive Suite",
        "tagline": "Postgraduate & Executive Education",
        "hall": "VIP Executive Lounge",
        "badge": "Executive Center",
        "icon": "ti-briefcase",
        "color": "#8b5cf6",
        "desc": "Specialized wing for working professionals exploring executive MBA, master's degrees, and corporate fellowships.",
        "activities": "GMAT & GRE waiver assessments, employer sponsorship strategies, career acceleration panels.",
        "order": 8
    },
    {
        "name": "Document Vault & Fast-Track Verification",
        "tagline": "Instant Credential Authentication",
        "hall": "Registration Foyer",
        "badge": "Fast-Track Pass",
        "icon": "ti-file-check",
        "color": "#14b8a6",
        "desc": "Official KNOVA digital badge punch station, transcript notarization, and priority booth fast-pass issuance.",
        "activities": "Digital badge QR verification, transcript scanning, passport stamp issuance.",
        "order": 9
    },
    {
        "name": "Student Innovation & Pitch Arena",
        "tagline": "Undergraduate Inventions & Startups",
        "hall": "Central Plaza",
        "badge": "Startup Arena",
        "icon": "ti-sparkles",
        "color": "#f97316",
        "desc": "Dynamic stage where aspiring young inventors pitch research concepts to university innovation incubators.",
        "activities": "Student project pitches, university incubator meetings, innovation prize ceremonies.",
        "order": 10
    }
]

created_zones = []
for z_data in zones_data:
    zone = FloorActivityZone.objects.create(
        name=z_data["name"],
        tagline=z_data["tagline"],
        hall_location=z_data["hall"],
        badge_label=z_data["badge"],
        icon_class=z_data["icon"],
        color_accent=z_data["color"],
        description=z_data["desc"],
        activities=z_data["activities"],
        order=z_data["order"],
        is_active=True
    )
    created_zones.append(zone)

print(f"Created {len(created_zones)} FloorActivityZone records.")
print("\n=== SUCCESS: All 10-item datasets seeded cleanly into the database! ===")
