import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import django
import datetime
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knova_backend.settings')
django.setup()

from core.models import EventLocation, Speaker, ProgrammeSession

def run():
    locations = EventLocation.objects.all()
    if not locations.exists():
        print("No event locations found!")
        return

    # Ensure speakers exist
    speakers_data = [
        {
            "name": "Dr. Jane Smith",
            "title": "Director of STEM & Emerging Tech",
            "organization": "Imperial College London",
            "profile": "Leading researcher in artificial intelligence, robotics, and future-forward university pathways for international students.",
            "is_verified": True
        },
        {
            "name": "Prof. Marcus Vance",
            "title": "Senior Dean of Global Admissions",
            "organization": "University of Toronto",
            "profile": "Expert on international merit scholarships, admissions evaluation, and transcript assessments across GCC institutions.",
            "is_verified": True
        },
        {
            "name": "Sarah Al-Hashimi",
            "title": "International Student Mobility & Visa Advisor",
            "organization": "GCC Global Education Council",
            "profile": "Specialist in study permit pathways, post-graduation work opportunities, and visa interview preparation.",
            "is_verified": True
        },
        {
            "name": "Dr. David Chen",
            "title": "Chair of Medical & Life Sciences",
            "organization": "Johns Hopkins Medicine",
            "profile": "Renowned academic counselor for competitive medicine, biotechnology, and healthcare degree entry.",
            "is_verified": True
        },
        {
            "name": "Elena Rostova",
            "title": "Head of Entrepreneurship & Business",
            "organization": "Stanford Graduate School of Business Alumni",
            "profile": "Advising prospective undergrads and postgrads on tech entrepreneurship, incubators, and dual-degree business models.",
            "is_verified": True
        }
    ]

    speakers = []
    for s_info in speakers_data:
        speaker, _ = Speaker.objects.get_or_create(
            name=s_info["name"],
            defaults={
                "title": s_info["title"],
                "organization": s_info["organization"],
                "profile": s_info["profile"],
                "is_verified": s_info["is_verified"]
            }
        )
        speakers.append(speaker)

    # Base sessions to populate across locations
    session_templates = [
        {
            "title": "Keynote: Artificial Intelligence & Future of Global STEM Degrees",
            "speaker": speakers[0],
            "start_time": datetime.time(9, 30),
            "end_time": datetime.time(10, 30),
            "hall_name": "Main Auditorium Alpha",
            "description": "Discover which engineering, computer science, and data careers will dominate the next decade and how top universities are adapting curricula."
        },
        {
            "title": "Masterclass: How to Win $5M+ Full-Ride & Merit Scholarships",
            "speaker": speakers[1],
            "start_time": datetime.time(10, 45),
            "end_time": datetime.time(11, 45),
            "hall_name": "Keynote Hall B",
            "description": "Actionable tactics for acing standardized tests, showcasing extracurricular leadership, and securing financial aid from premier global universities."
        },
        {
            "title": "Panel: Navigating Study Visas & Post-Study Work Permits in US, UK & Canada",
            "speaker": speakers[2],
            "start_time": datetime.time(12, 00),
            "end_time": datetime.time(13, 00),
            "hall_name": "Workshop Pavilion 3",
            "description": "Essential updates on student visa regulations, work-study allowances, application deadlines, and post-study residency pathways."
        },
        {
            "title": "Seminar: Medical, Dental & Healthcare Degree Pathways Abroad",
            "speaker": speakers[3],
            "start_time": datetime.time(14, 00),
            "end_time": datetime.time(15, 00),
            "hall_name": "Health Sciences Theatre",
            "description": "A comprehensive breakdown of international medical school admissions, clinical rotations, UCAT/MCAT prerequisites, and residency matches."
        },
        {
            "title": "Workshop: Crafting a Standout Personal Statement & Portfolio",
            "speaker": speakers[0],
            "start_time": datetime.time(15, 15),
            "end_time": datetime.time(16, 15),
            "hall_name": "Career Hub Lab",
            "description": "Interactive live review of winning essays, research resumes, and recommendation letters that grab admission committee attention."
        },
        {
            "title": "Fireside Chat: Business, Fintech & Silicon Valley Entrepreneurship",
            "speaker": speakers[4],
            "start_time": datetime.time(16, 30),
            "end_time": datetime.time(17, 30),
            "hall_name": "Executive Innovation Hall",
            "description": "Explore top undergraduate business, finance, and startup incubators abroad, with insider tips on campus venture funds."
        }
    ]

    total_created = 0
    for loc in locations:
        session_date = loc.start_date
        for s in session_templates:
            obj, created = ProgrammeSession.objects.get_or_create(
                title=s["title"],
                event_location=loc,
                date=session_date,
                defaults={
                    "start_time": s["start_time"],
                    "end_time": s["end_time"],
                    "hall_name": s["hall_name"],
                    "speaker": s["speaker"],
                    "description": s["description"]
                }
            )
            if created:
                total_created += 1

    print(f"Successfully seeded {total_created} ProgrammeSession records across {locations.count()} locations.")

if __name__ == '__main__':
    run()
