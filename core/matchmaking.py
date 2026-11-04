from .models import Course, University
from django.db.models import Q

def calculate_matches(student_profile):
    """
    Calculates match scores for Universities and Courses based on the StudentProfile.
    """
    # Base query for all approved universities
    universities = University.objects.filter(is_approved=True)
    courses = Course.objects.filter(is_active=True, status='Approved')
    
    # 1. Budget Matching
    student_budget = student_profile.budget_range
    budget_map = {
        'Low': ['Under $10k'],
        'Medium': ['Under $10k', '$10k-$30k'],
        'High': ['Under $10k', '$10k-$30k', 'Over $30k']
    }
    
    matched_courses = []
    for course in courses:
        score = 0
        reasons = []
        
        # Budget Score (Assuming course.fees has similar text or can be mapped)
        if student_budget and student_budget in budget_map:
            # Simple substring matching for MVP
            if any(b_level.lower() in course.fees.lower() for b_level in budget_map[student_budget]):
                score += 30
                reasons.append("Matches your budget")
        
        # Country Matching
        if student_profile.preferred_country:
            preferred_countries = [c.strip().lower() for c in student_profile.preferred_country.split(',')]
            
            if hasattr(course.university, 'profile') and course.university.profile.location_state_country:
                uni_location = course.university.profile.location_state_country.lower()
                if any(pc in uni_location for pc in preferred_countries):
                    score += 40
                    reasons.append("In your preferred location")
                
        # Program Matching
        if student_profile.preferred_program:
            preferred_programs = [p.strip().lower() for p in student_profile.preferred_program.split(',')]
            course_name = course.name.lower()
            if any(pp in course_name for pp in preferred_programs):
                score += 30
                reasons.append("Matches your program of interest")
                
        if score > 0:
            matched_courses.append({
                'course': course,
                'score': score,
                'reasons': reasons
            })
            
    # Sort by score descending
    matched_courses.sort(key=lambda x: x['score'], reverse=True)
    
    return matched_courses[:10] # Return top 10 matches
