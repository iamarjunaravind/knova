from .models import SiteConfiguration, ChatbotFAQ

def site_config(request):
    return {
        'site_config': SiteConfiguration.get_solo(),
        'chatbot_faqs': ChatbotFAQ.objects.filter(is_active=True).order_by('order', 'id'),
    }

def base_template(request):
    if hasattr(request, 'user') and request.user.is_authenticated:
        if hasattr(request.user, 'parent_profile'):
            return {'base_template': 'dashboard/base_parent.html'}
    return {'base_template': 'dashboard/base.html'}

def active_student(request):
    """
    Context processor providing the currently managed child student for parent users.
    """
    student = None
    if hasattr(request, 'user') and request.user.is_authenticated:
        if hasattr(request.user, 'parent_profile'):
            profile = request.user.parent_profile
            linked = profile.linked_students.select_related('user').all()
            active_id = request.session.get('active_student_id')
            if active_id:
                student = linked.filter(id=active_id).first()
            if not student and linked.exists():
                student = linked.first()
                request.session['active_student_id'] = student.id
    return {
        'active_student': student
    }

def user_university(request):
    uni = None
    if hasattr(request, 'user') and request.user.is_authenticated:
        if hasattr(request.user, 'university_staff') and request.user.university_staff:
            uni = request.user.university_staff.university
        elif hasattr(request.user, 'exhibitor_profile') and request.user.exhibitor_profile:
            from .models import University
            uni = University.objects.filter(name__iexact=request.user.exhibitor_profile.company_name).first()
        elif hasattr(request.user, 'exhibitor_staff_profile') and request.user.exhibitor_staff_profile:
            from .models import University
            uni = University.objects.filter(name__iexact=request.user.exhibitor_staff_profile.exhibitor.company_name).first()
        elif request.user.is_superuser or request.user.is_staff:
            from .models import University
            uni = University.objects.first()
    return {
        'user_university': uni
    }

def user_notifications(request):
    """
    Context processor supplying live notifications and unread count for the active user.
    Auto-seeds realistic onboarding notifications for active demo accounts if empty.
    """
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {
            'user_notifications': [],
            'unread_notifications_count': 0
        }
    
    from .models import Notification
    from django.utils import timezone
    from datetime import timedelta
    
    user = request.user
    existing_count = Notification.objects.filter(user=user).count()
    if existing_count == 0:
        role = getattr(user, 'role', '') or ('admin' if (user.is_superuser or user.is_staff) else 'student')
        if hasattr(user, 'parent_profile'):
            role = 'parent'
        elif hasattr(user, 'exhibitor_profile') or hasattr(user, 'exhibitor_staff_profile'):
            role = 'exhibitor'
        
        now = timezone.now()
        if role == 'student':
            items = [
                Notification(
                    user=user,
                    title="Welcome to KNOVA 2027 Expo!",
                    message="Your Digital ID Pass is ready. Present your QR code at the entrance fast-track gate for instant entry.",
                    is_read=False
                ),
                Notification(
                    user=user,
                    title="AI Matchmaker Suggestions Ready",
                    message="We found 4 high-match university undergraduate programs matching your profile preferences.",
                    is_read=False
                ),
                Notification(
                    user=user,
                    title="Masterclass Seminar Confirmed",
                    message="You are registered for 'Admissions Masterclass: Securing Full-Ride Scholarships' at Auditorium B.",
                    is_read=False
                ),
                Notification(
                    user=user,
                    title="KNOVA Challenge Quest Active",
                    message="Visit 3 partner university booths to earn bonus merit points and unlock the VIP Swag Bag.",
                    is_read=True
                ),
            ]
        elif role == 'parent':
            items = [
                Notification(
                    user=user,
                    title="Family Pass Connected",
                    message="Your parent account is successfully linked to your student's expo itinerary and live progress tracker.",
                    is_read=False
                ),
                Notification(
                    user=user,
                    title="Scholarship Advisory Briefing",
                    message="Reserved seat confirmed for the Parent Financial Aid & Global Scholarship Briefing at 2:00 PM.",
                    is_read=False
                ),
                Notification(
                    user=user,
                    title="University Comparison Guide",
                    message="Download your curated tuition & living cost comparison guide for UK and US institutions.",
                    is_read=True
                ),
            ]
        elif role == 'exhibitor':
            items = [
                Notification(
                    user=user,
                    title="Booth Setup Confirmed",
                    message="Your university booth allocation and digital QR lead scanner are fully configured and ready.",
                    is_read=False
                ),
                Notification(
                    user=user,
                    title="New Student Inquiries",
                    message="5 registered attendees added your university courses to their shortlist today.",
                    is_read=False
                ),
                Notification(
                    user=user,
                    title="Lead Export Ready",
                    message="Daily attendee lead report and scan log summary can now be downloaded in CSV or Excel.",
                    is_read=True
                ),
            ]
        else: # admin / staff / coordinator
            items = [
                Notification(
                    user=user,
                    title="System Health & Attendance OK",
                    message="Expo badge verification gateways and lead scanners are operating normally across all halls.",
                    is_read=False
                ),
                Notification(
                    user=user,
                    title="New Registrations Surge",
                    message="Over 120 new attendees registered today across Dubai and Abu Dhabi expo sessions.",
                    is_read=False
                ),
                Notification(
                    user=user,
                    title="Sponsor Materials Verified",
                    message="All Tier 1 and Tier 2 partner exhibitor banners and branding placements are active.",
                    is_read=True
                ),
            ]
        
        created_objs = Notification.objects.bulk_create(items)
        time_offsets = [timedelta(minutes=15), timedelta(hours=2), timedelta(hours=5), timedelta(days=1)]
        for i, obj in enumerate(created_objs):
            if i < len(time_offsets):
                Notification.objects.filter(id=obj.id).update(created_at=now - time_offsets[i])

    notifications = Notification.objects.filter(user=user).order_by('-created_at')[:20]
    unread_count = Notification.objects.filter(user=user, is_read=False).count()
    
    return {
        'user_notifications': notifications,
        'unread_notifications_count': unread_count
    }

