from django import template
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()

# Official user types in the system:
# 1. Admin
# 2. Exhibitor (exhibitor and university are same)
# 3. Student
# 4. Parent
# 5. Sponsor
# 6. Seminar Coordinator
# 7. Education Expert (Academic Counsellor)

@register.filter
def has_role(user, role_name):
    if not user or not user.is_authenticated:
        return False

    is_admin = (
        user.is_superuser or 
        user.is_staff or 
        user.groups.filter(name='Admin').exists() or 
        user.username.lower() == 'admin'
    )

    if is_admin:
        return role_name == 'admin'

    role_name = (role_name or '').lower()

    try:
        # 1. Admin
        if role_name == 'admin':
            return is_admin

        # 2. University / Exhibitor (Both are the same role)
        elif role_name in ('university', 'exhibitor', 'university_exhibitor', 'uni_exhibitor'):
            return bool(
                hasattr(user, 'university_staff') or 
                hasattr(user, 'university_profile') or 
                hasattr(user, 'exhibitor_profile') or 
                hasattr(user, 'exhibitor_staff_profile')
            )

        # 3. Student
        elif role_name == 'student':
            if (
                hasattr(user, 'university_staff') or 
                hasattr(user, 'university_profile') or 
                hasattr(user, 'exhibitor_profile') or 
                hasattr(user, 'exhibitor_staff_profile') or 
                hasattr(user, 'parent_profile') or 
                hasattr(user, 'sponsor_profile') or 
                hasattr(user, 'seminar_staff') or 
                hasattr(user, 'education_expert') or 
                is_admin
            ):
                return False
            return hasattr(user, 'student_profile')

        # 4. Parent
        elif role_name == 'parent':
            return hasattr(user, 'parent_profile')

        # 5. Sponsor
        elif role_name == 'sponsor':
            return hasattr(user, 'sponsor_profile')

        # 6. Seminar Coordinator
        elif role_name in ('seminar', 'seminar_coordinator'):
            return hasattr(user, 'seminar_staff')

        # 7. Education Expert / Academic Counsellor
        elif role_name in ('education_expert', 'expert', 'academic_counsellor', 'counsellor'):
            return hasattr(user, 'education_expert')

    except ObjectDoesNotExist:
        return False
        
    return False


@register.filter
def user_display_role(user):
    """
    Returns human-friendly display label for official user roles.
    """
    if not user or not user.is_authenticated:
        return "Guest Attendee"
    if user.is_superuser or user.is_staff or user.groups.filter(name='Admin').exists() or user.username.lower() == 'admin':
        return "Administrator"
    if hasattr(user, 'university_staff') or hasattr(user, 'university_profile') or hasattr(user, 'exhibitor_profile') or hasattr(user, 'exhibitor_staff_profile'):
        return "Exhibitor"
    if hasattr(user, 'education_expert'):
        return "Education Expert"
    if hasattr(user, 'seminar_staff'):
        return "Seminar Coordinator"
    if hasattr(user, 'student_profile'):
        return "Student"
    if hasattr(user, 'parent_profile'):
        return "Parent"
    if hasattr(user, 'sponsor_profile'):
        return "Sponsor"
    return "Student"
