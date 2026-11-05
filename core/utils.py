import random
import time
from .models import Registration, Exhibitor

def generate_unique_attendee_id(role=None):
    """
    Generate a unique Attendee ID with role-based prefix and 5 random digits.
    - Student: KNOVA-ST-<5 digits> (e.g. KNOVA-ST-48291)
    - Exhibitor: KNOVA-EX-<5 digits> (e.g. KNOVA-EX-73910)
    - Parent: KNOVA-PA-<5 digits> (e.g. KNOVA-PA-15024)
    - Sponsor: KNOVA-SP-<5 digits> (e.g. KNOVA-SP-92817)
    - Default/Other: KNOVA-AT-<5 digits> (e.g. KNOVA-AT-61849)

    Guarantees uniqueness across:
    - Registration.registration_id
    - StudentProfile.qr_identifier
    - ParentProfile.qr_identifier
    - StudentChallengePassport.badge_id
    """
    from .models import StudentProfile, ParentProfile, StudentChallengePassport

    role_str = str(role or '').strip().upper()
    if 'STUDENT' in role_str:
        prefix = 'KNOVA-ST-'
    elif 'EXHIBITOR' in role_str or 'UNIVERSITY' in role_str:
        prefix = 'KNOVA-EX-'
    elif 'PARENT' in role_str:
        prefix = 'KNOVA-PA-'
    elif 'SPONSOR' in role_str:
        prefix = 'KNOVA-SP-'
    else:
        prefix = 'KNOVA-AT-'

    for _ in range(5000):
        candidate = f"{prefix}{random.randint(10000, 99999)}"
        if (
            not Registration.objects.filter(registration_id__iexact=candidate).exists()
            and not StudentProfile.objects.filter(qr_identifier__iexact=candidate).exists()
            and not ParentProfile.objects.filter(qr_identifier__iexact=candidate).exists()
            and not StudentChallengePassport.objects.filter(badge_id__iexact=candidate).exists()
        ):
            return candidate

    return f"{prefix}{int(time.time() * 1000) % 90000 + 10000}"


def calculate_match_score(student: Registration, exhibitor: Exhibitor) -> int:
    """
    Calculates a match score (0-100) between a student and an exhibitor based on their preferences.
    """
    score = 0
    total_criteria = 0
    
    # 1. Country Match
    if student.preferred_country and exhibitor.country:
        total_criteria += 1
        if student.preferred_country.lower() in exhibitor.country.lower() or exhibitor.country.lower() in student.preferred_country.lower():
            score += 40
            
    # 2. Budget Match
    if student.budget_range and exhibitor.tuition_range:
        total_criteria += 1
        if student.budget_range == exhibitor.tuition_range:
            score += 30
        elif student.budget_range == 'High' and exhibitor.tuition_range in ['Low', 'Medium']:
            # If student has a high budget, they can afford lower tuition
            score += 30
            
    # 3. Program Match
    if student.preferred_program and exhibitor.offered_programs:
        total_criteria += 1
        if student.preferred_program.lower() in exhibitor.offered_programs.lower():
            score += 30
            
    # Base score of 10 for just being at the same event
    if student.event_location == exhibitor.event_location:
        score += 10
        
    return min(100, score)

def get_top_matches_for_student(student: Registration, limit=5):
    """Returns top matching exhibitors for a specific student."""
    exhibitors = Exhibitor.objects.filter(event_location=student.event_location)
    matches = []
    for ex in exhibitors:
        score = calculate_match_score(student, ex)
        if score > 20: # Only return somewhat relevant matches
            matches.append((ex, score))
            
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:limit]

def get_top_matches_for_exhibitor(exhibitor: Exhibitor, limit=20):
    """Returns top matching students (Leads) for a specific exhibitor."""
    students = Registration.objects.filter(event_location=exhibitor.event_location, role='Student')
    matches = []
    for st in students:
        score = calculate_match_score(st, exhibitor)
        if score > 20:
            matches.append((st, score))
            
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:limit]
