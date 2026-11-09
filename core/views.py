from django.shortcuts import render

from django.db.models import Count, Q

from .models import (
    CustomSection,
    EventLocation, Speaker, ProgrammeSession, University, Sponsor,
    UniversityProfile, Course, FloorActivityZone, Scholarship, Exhibitor, Registration

)


def index(request):

    # Collect countries from both UniversityProfile and Exhibitor

    uni_countries = list(UniversityProfile.objects.filter(university__is_approved=True).exclude(location_state_country='').values_list('location_state_country', flat=True))

    ex_countries = list(Exhibitor.objects.filter(is_verified=True).exclude(country='').values_list('country', flat=True))

    countries = sorted(list(set(uni_countries + ex_countries)))

    hero_universities = list(University.objects.filter(
        is_approved=True,
        hero_priority__gte=1
    ).select_related('profile').annotate(
        courses_count=Count('courses', distinct=True),
        scholarships_count=Count('scholarships', distinct=True)
    ).order_by('hero_priority')[:15])

    if len(hero_universities) < 15:
        existing_ids = [u.id for u in hero_universities]
        extra_unis = University.objects.filter(
            is_approved=True
        ).exclude(id__in=existing_ids).select_related('profile').annotate(
            courses_count=Count('courses', distinct=True),
            scholarships_count=Count('scholarships', distinct=True)
        ).order_by('id')[:(15 - len(hero_universities))]
        hero_universities = list(hero_universities) + list(extra_unis)

    # Fallback: If no universities are explicitly marked approved yet, still populate hero cards
    if not hero_universities:
        hero_universities = list(University.objects.select_related('profile').annotate(
            courses_count=Count('courses', distinct=True),
            scholarships_count=Count('scholarships', distinct=True)
        ).order_by('hero_priority', 'id')[:15])

    hero_courses = Course.objects.filter(is_active=True, status='Approved').filter(Q(university__isnull=True) | Q(university__is_approved=True)).select_related('university', 'university__profile')[:6]

    floor_zones = FloorActivityZone.objects.filter(is_active=True).order_by('order')

    scholarship_universities = University.objects.filter(is_approved=True, scholarships__isnull=False).distinct().order_by('name')[:60]

    featured_scholarships = Scholarship.objects.filter(Q(university__isnull=True) | Q(university__is_approved=True)).select_related('university', 'university__profile').order_by('-id')[:3]

    all_fields = [
        'Computer Science & AI',
        'Engineering & Technology',
        'Business & Finance',
        'Health & Medicine',
        'Arts & Humanities',
        'Law & Policy',
        'General Merit',
    ]

    all_levels = [
        ('Undergraduate', 'Undergraduate (UG)'),
        ('Postgraduate', 'Postgraduate (PG)'),
        ('PhD', 'PhD / Doctoral'),
        ('All Levels', 'All Levels / General'),
    ]

    all_coverages = [
        ('Full', 'Full Tuition (100%)'),
        ('Partial', 'Partial Fee Waiver'),
        ('Grant', 'Direct Grant Award'),
    ]

    all_deadlines = [
        ('upcoming', 'All Upcoming Deadlines'),
        ('30_days', 'Closing in 30 Days'),
        ('60_days', 'Closing in 60 Days'),
        ('90_days', 'Closing in 90 Days'),
    ]

    # Exhibitors from database: check Exhibitor model first, then University model

    exhibitor_qs = list(Exhibitor.objects.filter(is_verified=True).select_related('event_location')[:12])

    if not exhibitor_qs:

        exhibitor_qs = list(University.objects.filter(is_approved=True).select_related('profile')[:12])

    featured_exhibitors = exhibitor_qs

    # Programme sessions from database

    programme_sessions = list(ProgrammeSession.objects.filter(event_location__is_upcoming=True).select_related('event_location', 'speaker').order_by('date', 'start_time')[:24])

    if not programme_sessions:

        programme_sessions = list(ProgrammeSession.objects.all().select_related('event_location', 'speaker').order_by('date', 'start_time')[:24])

    # Dynamic counts strictly from database

    total_exhibitors = Exhibitor.objects.filter(is_verified=True).count() + University.objects.filter(is_approved=True).count()

    total_courses = Course.objects.filter(is_active=True, status='Approved').filter(Q(university__isnull=True) | Q(university__is_approved=True)).count()

    total_scholarships = Scholarship.objects.filter(Q(university__isnull=True) | Q(university__is_approved=True)).count()

    total_speakers = Speaker.objects.count()

    total_sessions = ProgrammeSession.objects.count()

    total_sponsors = Sponsor.objects.count()

    total_registrations = Registration.objects.count()

    total_countries = len(countries)

    context = {
        'custom_sections': CustomSection.objects.filter(is_active=True).order_by('order'),
        'events': EventLocation.objects.filter(is_active=True).order_by('start_date'),
        'upcoming_event': EventLocation.objects.filter(is_active=True, is_upcoming=True).first(),
        'featured_exhibitors': featured_exhibitors,
        'featured_speakers': Speaker.objects.all()[:12],
        'programme_sessions': programme_sessions,
        'universities': University.objects.filter(is_approved=True).select_related('profile').only('id', 'name', 'slug', 'profile__id', 'profile__location_city')[:150],
        'hero_universities': hero_universities,
        'hero_courses': hero_courses,
        'sponsors': Sponsor.objects.all(),
        'countries': countries,
        'floor_zones': floor_zones,
        'scholarship_universities': scholarship_universities,
        'featured_scholarships': featured_scholarships,
        'total_exhibitors': total_exhibitors,
        'total_courses': total_courses,
        'total_scholarships': total_scholarships,
        'total_speakers': total_speakers,
        'total_sessions': total_sessions,
        'total_sponsors': total_sponsors,
        'total_registrations': total_registrations,
        'total_countries': total_countries,
        'all_fields': all_fields,
        'all_levels': all_levels,
        'all_coverages': all_coverages,
        'all_deadlines': all_deadlines,
    }

    return render(request, 'core/index.html', context)
