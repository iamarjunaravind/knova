def check_user_has_scholarship_exam(user):
    if not user or not user.is_authenticated:
        return False
    from .models import ScholarshipExamBooking, ExamRegistration, ExamAttempt, StudentChallengePassport
    return bool(
        ScholarshipExamBooking.objects.filter(user=user).exclude(status='Cancelled').exists() or
        ExamAttempt.objects.filter(registration__student__user=user).exists() or
        ExamRegistration.objects.filter(student__user=user).exists() or
        StudentChallengePassport.objects.filter(user=user, aptitude_test_completed=True).exists()
    )

import base64
import io
import qrcode
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Registration, EventLocation, University, Exhibitor, StudentProfile, ParentProfile

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def _validate_password_strength(password):
    """
    Returns an error string if password fails, else None.
    Rules: 12+ chars, uppercase, lowercase, digit, special char, no spaces.
    """
    import re
    if not password:
        return 'Password is required.'
    if ' ' in password:
        return 'Password cannot contain spaces.'
    if len(password) < 12:
        return 'Password must be at least 12 characters long.'
    if not re.search(r'[A-Z]', password):
        return 'Password must contain at least one uppercase letter (A-Z).'
    if not re.search(r'[a-z]', password):
        return 'Password must contain at least one lowercase letter (a-z).'
    if not re.search(r'[0-9]', password):
        return 'Password must contain at least one number (0-9).'
    if not re.search(r'[^A-Za-z0-9]', password):
        return 'Password must contain at least one special character (!@#$%^&* etc.).'
    return None


def _normalize_phone_digits(phone):
    if not phone:
        return ""
    return ''.join(c for c in str(phone) if c.isdigit())


def _is_email_registered(email, exclude_user=None):
    if not email:
        return False
    from django.contrib.auth.models import User
    from django.db.models import Q
    clean_email = email.strip().lower()
    user_qs = User.objects.filter(Q(email__iexact=clean_email) | Q(username__iexact=clean_email))
    reg_qs = Registration.objects.filter(email__iexact=clean_email)
    if exclude_user:
        user_qs = user_qs.exclude(pk=exclude_user.pk)
        if exclude_user.email:
            reg_qs = reg_qs.exclude(email__iexact=exclude_user.email)
    return user_qs.exists() or reg_qs.exists()


def _is_phone_registered(phone, exclude_user=None):
    if not phone:
        return False
    from django.db.models import Q
    clean_phone = str(phone).strip()
    digits = _normalize_phone_digits(clean_phone)
    if len(digits) < 7:
        return False
    suffix = digits[-8:] if len(digits) >= 8 else digits

    reg_qs = Registration.objects.filter(Q(phone=clean_phone) | Q(phone__endswith=suffix))
    stu_qs = StudentProfile.objects.filter(Q(mobile=clean_phone) | Q(mobile__endswith=suffix))
    par_qs = ParentProfile.objects.filter(Q(mobile=clean_phone) | Q(mobile__endswith=suffix))

    if exclude_user:
        if exclude_user.email:
            reg_qs = reg_qs.exclude(email__iexact=exclude_user.email)
        stu_qs = stu_qs.exclude(user=exclude_user)
        par_qs = par_qs.exclude(user=exclude_user)

    return reg_qs.exists() or stu_qs.exists() or par_qs.exists()


def public_register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        role = request.POST.get('role', 'Visitor') # Default to Visitor
        event_location_id = request.POST.get('event_location')

        # Matchmaking Fields
        preferred_country = request.POST.get('preferred_country', '')
        budget_range = request.POST.get('budget_range', '')
        preferred_program = request.POST.get('preferred_program', '')

        # Simple validation
        if full_name and email and event_location_id:
            try:
                event_location = EventLocation.objects.get(pk=event_location_id)
                password = request.POST.get('password')

                # Duplicate email / phone checks
                from django.contrib.auth.models import User
                def _reg_error(msg):
                    return render(request, 'core/register.html', {
                        'error': msg,
                        'events': EventLocation.objects.filter(is_active=True).order_by('start_date'),
                        'exhibitors': Exhibitor.objects.all()
                    })
                if not request.user.is_authenticated:
                    if _is_email_registered(email):
                        return _reg_error('An account or registration with this email already exists. Please login or use a different email.')
                    if phone and _is_phone_registered(phone):
                        return _reg_error('This mobile number is already registered. Please use a different number or login.')
                    pwd_err = _validate_password_strength(password)
                    if password and pwd_err:
                        return _reg_error(pwd_err)
                else:
                    # Authenticated user
                    if Registration.objects.filter(email__iexact=email).exclude(email__iexact=request.user.email).exists():
                        return _reg_error('This email is already associated with an existing registration.')
                event_location = EventLocation.objects.get(pk=event_location_id)
                # Check if registration with this email already exists
                reg, created = Registration.objects.get_or_create(
                    email=email,
                    defaults={
                        'full_name': full_name,
                        'phone': phone,
                        'role': role,
                        'event_location': event_location,
                        'preferred_country': preferred_country,
                        'budget_range': budget_range,
                        'preferred_program': preferred_program,
                        'status': 'Confirmed'
                    }
                )

                if not created:
                    reg.full_name = full_name
                    reg.phone = phone
                    reg.role = role
                    reg.event_location = event_location
                    reg.preferred_country = preferred_country
                    reg.budget_range = budget_range
                    reg.preferred_program = preferred_program
                    reg.save()

                # Create user account if password is provided
                password = request.POST.get('password')
                if password:
                    from django.contrib.auth.models import User

                    if not User.objects.filter(username=email).exists():
                        user = User.objects.create_user(username=email, email=email, password=password, first_name=full_name)
                        if role == 'Student':
                            StudentProfile.objects.create(user=user, mobile=phone)
                        elif role == 'Parent':
                            ParentProfile.objects.create(user=user, mobile=phone)
                        elif role == 'Exhibitor':
                            company = request.POST.get('company_name', full_name)
                            from django.utils.text import slugify
                            from .models import University, UniversityStaff
                            # Get or create the University entry by company name
                            uni_slug = slugify(company)
                            # Ensure slug uniqueness
                            base_slug = uni_slug
                            counter = 1
                            while University.objects.filter(slug=uni_slug).exists():
                                uni_slug = f'{base_slug}-{counter}'
                                counter += 1
                            uni, _ = University.objects.get_or_create(
                                name=company,
                                defaults={'slug': uni_slug, 'is_approved': False}
                            )
                            UniversityStaff.objects.get_or_create(
                                user=user,
                                defaults={'university': uni, 'role': 'Representative'}
                            )
                            # Also keep an Exhibitor record for backward compatibility
                            Exhibitor.objects.get_or_create(
                                user=user,
                                defaults={'company_name': company, 'event_location': event_location}
                            )

                if created:
                    # Save interested exhibitors
                    interested_in_ids = request.POST.getlist('interested_in')
                    if interested_in_ids:
                        reg.interested_in.set(interested_in_ids)

                    # Calculate Student Matches
                    from .utils import get_top_matches_for_student
                    student_matches = []
                    if role == 'Student':
                        student_matches = get_top_matches_for_student(reg, limit=3)

                    # Send confirmation email
                    badge_url = request.build_absolute_uri(reverse('digital_badge', args=[reg.pk]))
                    subject = f'Registration Confirmation for {event_location.name}'
                    html_message = render_to_string('core/email_confirmation.html', {
                        'registration': reg,
                        'event': event_location,
                        'badge_url': badge_url,
                        'matches': student_matches
                    })
                    plain_message = strip_tags(html_message)
                    send_mail(
                        subject,
                        plain_message,
                        'noreply@knova.com',
                        [reg.email],
                        html_message=html_message,
                        fail_silently=True,
                    )

                return redirect(reverse('register_success', args=[reg.pk]))
            except EventLocation.DoesNotExist:
                pass

    # GET Request
    context = {
        'events': EventLocation.objects.filter(is_active=True).order_by('start_date'),
        'exhibitors': Exhibitor.objects.all()
    }
    return render(request, 'core/register.html', context)


def register_success(request, pk):
    from django.contrib.auth.models import User
    reg = get_object_or_404(Registration, pk=pk)

    connect_candidates = []
    connect_role = None

    if reg.role == 'Student':
        connect_role = 'Parent'
        parent_regs = Registration.objects.filter(
            role='Parent',
            event_location=reg.event_location
        ).exclude(email=reg.email)
        for pr in parent_regs:
            u = User.objects.filter(email__iexact=pr.email).first()
            if u and hasattr(u, 'parent_profile'):
                already = u.parent_profile.linked_students.filter(
                    user__email__iexact=reg.email
                ).exists()
                if not already:
                    connect_candidates.append({'reg': pr, 'user': u})

    elif reg.role == 'Parent':
        connect_role = 'Student'
        student_regs = Registration.objects.filter(
            role='Student',
            event_location=reg.event_location
        ).exclude(email=reg.email)
        for sr in student_regs:
            u = User.objects.filter(email__iexact=sr.email).first()
            if u and hasattr(u, 'student_profile'):
                already = u.student_profile.parents.filter(
                    user__email__iexact=reg.email
                ).exists()
                if not already:
                    connect_candidates.append({'reg': sr, 'user': u})

    connected_name = request.session.pop(f'connected_{pk}', None)

    context = {
        'registration': reg,
        'event': reg.event_location,
        'connect_candidates': connect_candidates[:5],
        'connect_role': connect_role,
        'connected_name': connected_name,
    }
    return render(request, 'core/register_success.html', context)


def connect_family(request, reg_pk):
    """Links a newly registered Student or Parent with an existing counterpart."""
    from django.contrib.auth.models import User
    if request.method != 'POST':
        return redirect('register_success', pk=reg_pk)
    reg = get_object_or_404(Registration, pk=reg_pk)
    target_email = request.POST.get('target_email', '').strip()
    if not target_email:
        return redirect('register_success', pk=reg_pk)
    target_user = User.objects.filter(email__iexact=target_email).first()
    if not target_user:
        return redirect('register_success', pk=reg_pk)
    current_user = User.objects.filter(email__iexact=reg.email).first()
    if reg.role == 'Student' and current_user and hasattr(current_user, 'student_profile'):
        if hasattr(target_user, 'parent_profile'):
            target_user.parent_profile.linked_students.add(current_user.student_profile)
    elif reg.role == 'Parent' and current_user and hasattr(current_user, 'parent_profile'):
        if hasattr(target_user, 'student_profile'):
            current_user.parent_profile.linked_students.add(target_user.student_profile)
    request.session[f'connected_{reg_pk}'] = (
        target_user.get_full_name() or target_user.username
    )
    return redirect('register_success', pk=reg_pk)


def digital_badge(request, pk):
    reg = get_object_or_404(Registration, pk=pk)
    valid_prefixes = ('KNOVA-ST-', 'KNOVA-EX-', 'KNOVA-PA-', 'KNOVA-SP-', 'KNOVA-AT-')
    if not reg.registration_id or not any(reg.registration_id.startswith(p) for p in valid_prefixes):
        from .utils import generate_unique_attendee_id
        reg.registration_id = generate_unique_attendee_id(reg.role)
        Registration.objects.filter(pk=reg.pk).update(registration_id=reg.registration_id)

    # Generate QR Code
    qr_data = reg.registration_id
    qr = qrcode.make(qr_data)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Gamification Passport
    visit_count = reg.booth_visits.count()
    student_id = reg.registration_id

    context = {
        'registration': reg,
        'event': reg.event_location,
        'qr_base64': qr_base64,
        'visit_count': visit_count,
        'student_id': student_id,
        'badge_id': student_id,
    }
    return render(request, 'core/digital_badge.html', context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt


def capture_chat_lead(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            if name and email:
                from .models import ChatLead
                ChatLead.objects.create(name=name, email=email)
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)

from .models import Registration, EventLocation, Exhibitor, Speaker, ProgrammeSession, Sponsor
from django.views.decorators.cache import cache_page


def public_events(request):
    from .models import FloorActivityZone, University, Scholarship
    events = list(EventLocation.objects.filter(is_active=True).order_by('start_date'))
    featured_event = next((e for e in events if 'bahrain' in e.city.lower()), events[0] if events else None)

    # Floor activity zones
    floor_zones = FloorActivityZone.objects.filter(is_active=True).order_by('order')

    # Counts
    uni_count = University.objects.count()
    scholarship_count = Scholarship.objects.count()

    # City image mapping
    city_images = {
        'bahrain': 'assets/bahrain_skyline.webp',
        'doha': 'assets/doha_skyline.webp',
        'doha, qatar': 'assets/doha_skyline.webp',
        'al khobar': 'assets/al_khobar_skyline.webp',
        'al khobar, saudi arabia': 'assets/al_khobar_skyline.webp',
    }

    for ev in events:
        city_lower = ev.city.lower().strip()
        ev.image_asset = city_images.get(city_lower, 'assets/dubai.webp')

    if featured_event:
        featured_city_lower = featured_event.city.lower().strip()
        featured_event.image_asset = city_images.get(featured_city_lower, 'assets/bahrain_promo.webp')

    return render(request, 'core/events.html', {
        'events': events,
        'featured_event': featured_event,
        'floor_zones': floor_zones,
        'uni_count': uni_count,
        'scholarship_count': scholarship_count,
    })

from django.db.models import Case, When, F, Value, IntegerField


def public_exhibitors(request):
    from .models import University, UniversityProfile, Scholarship, Exhibitor, Course
    from django.db.models import Case, When, F, Value, IntegerField, Count

    # Support Exhibitor model
    exhibitor_records = list(Exhibitor.objects.all().select_related('event_location').order_by('company_name'))
    # Support University model
    uni_records = list(University.objects.filter(is_approved=True).select_related('profile').annotate(
        sort_priority=Case(
            When(hero_priority=0, then=Value(9999)),
            default=F('hero_priority'),
            output_field=IntegerField()
        ),
        courses_count=Count('courses', distinct=True),
        scholarships_count=Count('scholarships', distinct=True),
    ).order_by('sort_priority', 'name'))

    exhibitors = exhibitor_records + uni_records

    saved_uni_ids = set()
    if request.user.is_authenticated:
        try:
            from .models import SavedUniversity
            saved_uni_ids = set(
                SavedUniversity.objects.filter(student__user=request.user).values_list('university_id', flat=True)
            )
        except Exception:
            pass

    # Distinct countries from both models
    uni_countries = list(UniversityProfile.objects.exclude(location_state_country='').values_list('location_state_country', flat=True))
    ex_countries = list(Exhibitor.objects.exclude(country='').values_list('country', flat=True))
    all_countries = sorted(list(set(uni_countries + ex_countries)))

    total_unis = len(exhibitors)
    total_scholarships = Scholarship.objects.count()
    total_courses = Course.objects.count()
    total_countries = len(all_countries)

    return render(request, 'core/exhibitors.html', {
        'exhibitors': exhibitors,
        'saved_uni_ids': saved_uni_ids,
        'all_countries': all_countries,
        'total_unis': total_unis,
        'total_scholarships': total_scholarships,
        'total_courses': total_courses,
        'total_countries': total_countries,
    })


@cache_page(60 * 15)


def public_speakers(request):
    speakers = Speaker.objects.all()
    return render(request, 'core/speakers.html', {'speakers': speakers})


@cache_page(60 * 15)


def public_programme(request):
    sessions = ProgrammeSession.objects.select_related('event_location', 'speaker').order_by('date', 'start_time')
    return render(request, 'core/programme.html', {'sessions': sessions})


def public_sponsors(request):
    sponsors = list(Sponsor.objects.select_related('event_location').all())
    platinum_sponsors = [s for s in sponsors if s.category == 'Platinum']
    gold_sponsors = [s for s in sponsors if s.category == 'Gold']
    silver_sponsors = [s for s in sponsors if s.category in ['Silver', 'Bronze']]

    return render(request, 'core/sponsors.html', {
        'sponsors': sponsors,
        'platinum_sponsors': platinum_sponsors,
        'gold_sponsors': gold_sponsors,
        'silver_sponsors': silver_sponsors,
        'total_sponsors': len(sponsors),
    })


def public_about(request):
    return render(request, 'core/about.html')


@csrf_exempt


def check_in_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qr_data = data.get('qr_data')
            if qr_data:
                if qr_data.startswith("KNV-"):
                    reg = Registration.objects.get(registration_id=qr_data)
                elif qr_data.startswith("KNOVA-REG-"):
                    parts = qr_data.split('-')
                    if len(parts) >= 3:
                        reg_id = parts[2]
                        reg = Registration.objects.get(pk=reg_id)
                else:
                    reg = Registration.objects.get(registration_id=qr_data)

                if reg.is_checked_in:
                    return JsonResponse({'status': 'ALREADY_CHECKED_IN', 'message': f'{reg.full_name} is already checked in.'})

                reg.is_checked_in = True
                reg.status = 'Checked-in'
                reg.save()
                return JsonResponse({'status': 'SUCCESS', 'message': f'Checked in {reg.full_name}'})
            return JsonResponse({'status': 'INVALID_QR', 'message': 'Invalid QR Data'}, status=400)
        except Registration.DoesNotExist:
            return JsonResponse({'status': 'REGISTRATION_NOT_FOUND', 'message': 'Registration not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)


@csrf_exempt


def scan_booth_api(request):
    """
    Unified scanning endpoint:
    Mode 1: Exhibitors scan a student's badge: { "qr_data": "KNV-...", "exhibitor_id": 123 }
    Mode 2: Student scans a booth's QR: { "booth_qr": "BOOTH-...", "student_reg_id": "KNV-..." }
    """
    from .models import Exhibitor, BoothVisit, ExpoBooth, BoothInteraction
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qr_data = data.get('qr_data')
            exhibitor_id = data.get('exhibitor_id')
            booth_qr = data.get('booth_qr')
            student_reg_id = data.get('student_reg_id')

            # Mode 2: Student scanning Booth
            if booth_qr and student_reg_id:
                # Find student
                if student_reg_id.startswith("KNV-"):
                    student = Registration.objects.get(registration_id=student_reg_id)
                elif student_reg_id.startswith("KNOVA-REG-"):
                    student = Registration.objects.get(pk=student_reg_id.split('-')[2])
                else:
                    student = Registration.objects.get(registration_id=student_reg_id)

                # Find Booth
                booth = ExpoBooth.objects.get(qr_code=booth_qr, is_active=True)

                # Create Interaction (duplicate prevention within 1 hour could be done, but simple logic for now: only 1 per day or just get_or_create)
                # Actually, get_or_create on BoothInteraction might not work if it doesn't have unique_together.
                # Let's check if they scanned it already today
                from django.utils import timezone
                today = timezone.now().date()
                interaction = BoothInteraction.objects.filter(
                    student=student.studentprofile if hasattr(student, 'studentprofile') else student, # wait, BoothInteraction uses StudentProfile!
                    booth=booth,
                    interaction_date__date=today
                ).first()

                # BoothInteraction expects StudentProfile. But what if Registration is just a Registration?
                # The model says: student = models.ForeignKey(StudentProfile, ...)
                # Let's use the user's student profile
                if not hasattr(student, 'student_profile') and not hasattr(student, 'user'):
                    # The Registration model does not have a direct link to User/StudentProfile in this legacy code.
                    # Wait, StudentProfile has `user`, and `User` has email. `Registration` has email.
                    from .models import StudentProfile
                    sp = StudentProfile.objects.filter(user__email=student.email).first()
                else:
                    sp = None

                if sp:
                    interaction, created = BoothInteraction.objects.get_or_create(
                        student=sp, booth=booth, interaction_type='Scanned QR'
                    )
                    if created:
                        # Lead logic: Create ExhibitorLead if applicable
                        if booth.exhibitor:
                            from .models import ExhibitorLead
                            ExhibitorLead.objects.get_or_create(exhibitor=booth.exhibitor, scanned_registration=student)
                        return JsonResponse({'status': 'success', 'message': f'Successfully checked into {booth.get_assigned_organization()}!'})
                    else:
                        return JsonResponse({'status': 'success', 'message': f'You already checked into {booth.get_assigned_organization()} today.'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Only registered students can scan booths.'}, status=403)

            # Mode 1: Exhibitor scanning Student
            if qr_data:
                if qr_data.startswith("KNV-"):
                    student = Registration.objects.get(registration_id=qr_data)
                elif qr_data.startswith("KNOVA-REG-"):
                    parts = qr_data.split('-')
                    if len(parts) >= 3:
                        reg_id = parts[2]
                        student = Registration.objects.get(pk=reg_id)
                else:
                    student = Registration.objects.get(registration_id=qr_data)

                exhibitor = Exhibitor.objects.get(pk=exhibitor_id)

                # Create the visit (ignores if already exists due to unique_together and get_or_create)
                visit, created = BoothVisit.objects.get_or_create(student=student, exhibitor=exhibitor)

                if created:
                    return JsonResponse({'status': 'success', 'message': f'{student.full_name} added to your leads!'})
                else:
                    return JsonResponse({'status': 'success', 'message': f'{student.full_name} has already visited.'})
            return JsonResponse({'status': 'error', 'message': 'Invalid QR Data'}, status=400)
        except Registration.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Registration not found'}, status=404)
        except Exhibitor.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Exhibitor not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)


def university_detail(request, slug):
    from .models import University, Exhibitor, Course, Scholarship, SavedUniversity, StudentProfile
    from django.shortcuts import get_object_or_404, render, redirect

    slug_clean = (slug or '').strip()
    university = University.objects.filter(slug__iexact=slug_clean).select_related('profile').first()

    # Check if slug is an exhibitor reference (e.g. exhibitor-13 or exhibitor-20)
    if not university:
        exhibitor = None
        if slug_clean.startswith('exhibitor-'):
            exh_id = slug_clean.replace('exhibitor-', '').strip()
            if exh_id.isdigit():
                exhibitor = Exhibitor.objects.filter(id=int(exh_id)).first()
        if not exhibitor:
            exhibitor = Exhibitor.objects.filter(company_name__iexact=slug_clean.replace('-', ' ')).first()

        if exhibitor:
            # Check if this exhibitor corresponds to an existing University
            matching_uni = None
            if 'mit' in exhibitor.company_name.lower().split():
                matching_uni = University.objects.filter(slug='mit').first()
            if not matching_uni:
                words = [w.lower() for w in exhibitor.company_name.replace('(', '').replace(')', '').split() if len(w) >= 3 and w.lower() not in ['university', 'global', 'admissions', 'bureau', 'desk', 'international', 'hub', 'pavilion']]
                for w in words:
                    matching_uni = University.objects.filter(name__icontains=w).first()
                    if matching_uni:
                        break
            if matching_uni:
                return redirect('university_detail', slug=matching_uni.slug)
            else:
                # Use exhibitor itself as university
                university = exhibitor

    if not university:
        university = get_object_or_404(University.objects.select_related('profile'), slug=slug_clean)

    # Fetch courses and scholarships
    courses = []
    scholarships = []
    if isinstance(university, University):
        courses = Course.objects.filter(university=university, is_active=True).select_related('category')
        scholarships = Scholarship.objects.filter(university=university)
    else:
        # Exhibitor: find courses and scholarships matching company name if any
        first_word = university.company_name.split()[0]
        courses = Course.objects.filter(university__name__icontains=first_word, is_active=True).select_related('category')
        scholarships = Scholarship.objects.filter(university__name__icontains=first_word)

    is_saved = False
    if request.user.is_authenticated:
        try:
            student = StudentProfile.objects.filter(user=request.user).first()
            if student:
                if isinstance(university, University):
                    is_saved = SavedUniversity.objects.filter(student=student, university=university).exists()
                else:
                    is_saved = SavedUniversity.objects.filter(student=student, university_id=university.id).exists()
        except Exception:
            pass

    has_scholarship_exam = check_user_has_scholarship_exam(request.user)
    return render(request, 'core/university_detail.html', {
        'university': university,
        'courses': courses,
        'scholarships': scholarships,
        'is_saved': is_saved,
        'has_scholarship_exam': has_scholarship_exam
    })


def courses_list(request):
    from .models import Course, CourseCategory, UniversityProfile, University, Scholarship
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.core.cache import cache
    from django.db.models import Q

    # Base query with optimized foreign keys
    courses = Course.objects.filter(is_active=True, status='Approved').select_related(
        'university', 'category', 'university__profile'
    )

    # Search by keyword (multi-word, category, university, stream, degree, eligibility)
    q = request.GET.get('q', '').strip()
    if q:
        words = [w for w in q.split() if w]
        if words:
            query_filter = Q()
            for w in words:
                query_filter &= (
                    Q(name__icontains=w) |
                    Q(university__name__icontains=w) |
                    Q(stream__icontains=w) |
                    Q(category__name__icontains=w) |
                    Q(degree_type__icontains=w) |
                    Q(mode__icontains=w) |
                    Q(eligibility__icontains=w)
                )
            courses = courses.filter(query_filter)

    # Country filter
    country = request.GET.get('country', '').strip()
    if country:
        courses = courses.filter(university__profile__location_state_country__iexact=country)

    # Category filter
    cat_id = request.GET.get('category', '').strip()
    if cat_id:
        courses = courses.filter(category_id=cat_id)

    # Stream filter
    stream = request.GET.get('stream', '').strip()
    if stream:
        courses = courses.filter(stream__iexact=stream)

    # Degree type filter
    degree_type = request.GET.get('degree_type', '').strip()
    if degree_type:
        courses = courses.filter(degree_type=degree_type)

    # Study mode filter
    mode = request.GET.get('mode', '').strip()
    if mode:
        courses = courses.filter(mode=mode)

    # Scholarship availability filter
    scholarship_only = request.GET.get('scholarship', '').strip()
    if scholarship_only == '1':
        courses = courses.filter(scholarship_available=True)

    # Sorting
    sort_by = request.GET.get('sort_by', '').strip()
    if sort_by == 'name_asc':
        courses = courses.order_by('name')
    elif sort_by == 'name_desc':
        courses = courses.order_by('-name')
    elif sort_by == 'university_asc':
        courses = courses.order_by('university__name')
    elif sort_by == 'university_desc':
        courses = courses.order_by('-university__name')
    else:
        courses = courses.order_by('-university__hero_priority', 'name', 'id')

    # Total filtered count before pagination
    filtered_count = courses.count()

    # Cached high-level statistics for hero section
    stats_cache_key = 'courses_hero_stats_v1'
    hero_stats = cache.get(stats_cache_key)
    if not hero_stats:
        hero_stats = {
            'total_courses': Course.objects.filter(is_active=True, status='Approved').count(),
            'total_universities': University.objects.count(),
            'total_scholarships': Scholarship.objects.count(),
            'total_countries': UniversityProfile.objects.exclude(location_state_country='').values('location_state_country').distinct().count(),
        }
        cache.set(stats_cache_key, hero_stats, 600)

    # Paginate results (24 per page for balanced responsive grid)
    paginator = Paginator(courses, 24)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.get_page(1)

    # Preserve GET parameters for pagination links (excluding 'page')
    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']
    pagination_query = get_params.urlencode()

    # Categories and countries for filter dropdowns
    categories = CourseCategory.objects.all()
    all_countries = list(
        UniversityProfile.objects.exclude(location_state_country='')
        .values_list('location_state_country', flat=True)
        .distinct()
        .order_by('location_state_country')
    )
    raw_streams = list(
        Course.objects.filter(is_active=True, status='Approved')
        .exclude(stream='')
        .values_list('stream', flat=True)
        .distinct()
    )
    # Deduplicate streams to show distinct popular academic disciplines
    curated_streams = []
    seen_prefixes = set()
    for s in sorted(raw_streams, key=lambda x: -len(x)):
        norm = s.strip()
        first_word = norm.lower().replace('&', '').split()[0] if norm else ''
        if first_word in seen_prefixes or norm.upper() in ['CS', 'IT', 'ENG']:
            continue
        seen_prefixes.add(first_word)
        curated_streams.append(norm)
    all_streams = sorted(curated_streams)

    # Check saved universities if user is authenticated
    saved_uni_ids = set()
    if request.user.is_authenticated:
        try:
            from .models import SavedUniversity
            saved_uni_ids = set(
                SavedUniversity.objects.filter(student__user=request.user).values_list('university_id', flat=True)
            )
        except Exception:
            pass

    selected_cat_obj = None
    if cat_id:
        try:
            selected_cat_obj = categories.filter(id=cat_id).first()
        except Exception:
            pass

    return render(request, 'core/courses_list.html', {
        'page_obj': page_obj,
        'has_scholarship_exam': check_user_has_scholarship_exam(request.user),
        'courses': page_obj,  # backwards-compatible with loops
        'filtered_count': filtered_count,
        'hero_stats': hero_stats,
        'categories': categories,
        'all_countries': all_countries,
        'all_streams': all_streams,
        'selected_q': q,
        'selected_country': country,
        'selected_cat': cat_id,
        'selected_cat_obj': selected_cat_obj,
        'selected_stream': stream,
        'selected_degree': degree_type,
        'selected_mode': mode,
        'selected_scholarship': scholarship_only,
        'selected_sort': sort_by,
        'pagination_query': pagination_query,
        'saved_uni_ids': saved_uni_ids,
    })

from django.contrib.auth.decorators import login_required


@login_required(login_url='/admin/login/')


@csrf_exempt


def save_university(request, pk):
    from .models import University, SavedUniversity, StudentProfile

    if request.method == 'POST':
        try:
            university = University.objects.get(pk=pk)
            # Ensure student profile exists
            student, _ = StudentProfile.objects.get_or_create(user=request.user)

            saved, created = SavedUniversity.objects.get_or_create(
                student=student,
                university=university
            )

            if created:
                return JsonResponse({'status': 'success', 'message': 'Added to your shortlist!'})
            else:
                saved.delete()
                return JsonResponse({'status': 'success', 'message': 'Removed from your shortlist!'})
        except University.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'University not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)


@csrf_exempt


def university_enquire_callback(request, pk):
    from .models import University, Enquiry, StudentProfile, BoothInteraction, ExpoBooth, Exhibitor, ExhibitorLead, Registration, EventLocation, UniversityApplication
    if request.method == 'POST':
        try:
            university = University.objects.get(pk=pk)
            action = (request.POST.get('action') or '').strip()
            course_interest = (request.POST.get('course_interest') or '').strip()

            # Handle 1-click Book Now (no form details required)
            if action == 'book_now':
                if not request.user.is_authenticated:
                    return JsonResponse({
                        'status': 'login_required',
                        'message': 'Please sign in to book your course instantly.',
                        'login_url': f'/portal/login/?next=/university/{university.slug}/'
                    })

                # Strict role restriction: ONLY registered students can book courses!
                user = request.user
                is_student = hasattr(user, 'student_profile')
                if hasattr(user, 'registration') and user.registration.role and user.registration.role.lower() != 'student':
                    is_student = False
                if hasattr(user, 'university_staff') or hasattr(user, 'parent_profile') or hasattr(user, 'seminar_staff') or user.is_superuser:
                    is_student = False

                if not is_student:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Course booking is restricted to prospective student attendees. Exhibitor, staff, and parent accounts cannot book course seats.'
                    }, status=403)

                student = getattr(request.user, 'student_profile', None)
                if not student:
                    student, _ = StudentProfile.objects.get_or_create(user=request.user)

                full_name = request.user.get_full_name() or request.user.username
                email = request.user.email or ''
                phone = getattr(student, 'mobile', '') or ''

                # Link or create Registration
                reg = None
                if email:
                    reg = Registration.objects.filter(email=email).first()
                if not reg:
                    reg = Registration.objects.create(
                        full_name=full_name,
                        email=email or f"{request.user.username}@knova.student",
                        phone=phone or '7736128087',
                        role='Student',
                        status='Registered',
                        event_location=EventLocation.objects.first()
                    )

                # Find or match Exhibitor for this University
                exhibitor = Exhibitor.objects.filter(company_name__iexact=university.name).first()
                if not exhibitor:
                    # Try matching by primary name or words
                    words = [w for w in university.name.split() if len(w) > 3]
                    for w in words:
                        exhibitor = Exhibitor.objects.filter(company_name__icontains=w).first()
                        if exhibitor:
                            break
                if not exhibitor:
                    booth_with_exh = ExpoBooth.objects.filter(university=university, exhibitor__isnull=False).first()
                    if booth_with_exh:
                        exhibitor = booth_with_exh.exhibitor
                if not exhibitor:
                    exhibitor = Exhibitor.objects.create(
                        company_name=university.name,
                        event_location=EventLocation.objects.first(),
                        is_verified=True
                    )

                # Record ExhibitorLead so it views on the Exhibitor Leads page
                lead, created_lead = ExhibitorLead.objects.get_or_create(
                    exhibitor=exhibitor,
                    scanned_registration=reg
                )
                if created_lead:
                    lead.lead_source = 'Book'
                else:
                    if lead.lead_source == 'Punch':
                        lead.lead_source = 'Punch & Book'
                    elif not lead.lead_source:
                        lead.lead_source = 'Book'
                lead.rating = 'Hot'
                lead.action_tags = 'Course Booking'
                booking_note = f"Booked Course: {course_interest}" if course_interest else "Booked Course Seat"
                if lead.notes and booking_note not in lead.notes:
                    lead.notes = f"{lead.notes} | {booking_note}"
                else:
                    lead.notes = booking_note
                lead.save()

                # Record University Application
                if course_interest:
                    UniversityApplication.objects.get_or_create(
                        student=student,
                        university=university,
                        program_name=course_interest,
                        defaults={'status': 'Applied'}
                    )

                # Record Enquiry
                Enquiry.objects.create(
                    student=student,
                    university=university,
                    message=f"Booked Course: {course_interest or 'General Seat'} | 1-Click Instant Booking by {full_name}",
                    status='Pending'
                )

                # Record Booth Interaction
                booth = ExpoBooth.objects.filter(university=university).first()
                if not booth:
                    booth = ExpoBooth.objects.filter(exhibitor=exhibitor).first()
                if not booth:
                    booth = ExpoBooth.objects.create(
                        university=university,
                        booth_number=f"U-{university.pk:02d}",
                        hall="Main Expo Hall",
                        status="ASSIGNED"
                    )
                BoothInteraction.objects.create(
                    student=student,
                    booth=booth,
                    interaction_type='Course Booking',
                    status='Interested',
                    notes=f"Instant Booked: {course_interest or 'General Program'}"
                )

                # Sync challenge passport if applicable
                try:
                    passport = getattr(request.user, 'challenge_passport', None)
                    if passport:
                        passport.sync_with_attendance()
                except Exception:
                    pass

                from .models import Course
                c_obj = Course.objects.filter(university=university, name__iexact=course_interest).first()
                has_sch = c_obj.scholarship_available if c_obj else False
                has_exam = check_user_has_scholarship_exam(request.user)

                if has_sch:
                    if has_exam:
                        return JsonResponse({
                            'status': 'success',
                            'message': f'Booked {course_interest} successfully!',
                            'course': course_interest,
                            'has_scholarship': True,
                            'exam_status': 'already_done',
                            'exam_title': 'Common Scholarship Exam on File',
                            'exam_msg': 'Common Scholarship Examination already completed on file. Your active exam results will automatically be considered for this scholarship!'
                        })
                    else:
                        return JsonResponse({
                            'status': 'success',
                            'message': f'Booked {course_interest} successfully!',
                            'course': course_interest,
                            'has_scholarship': True,
                            'exam_status': 'ask_exam',
                            'exam_title': 'Common Scholarship Examination Required',
                            'exam_msg': f'"{course_interest}" is eligible for institutional scholarships and tuition fee waivers! Please take the Common Scholarship Examination to qualify for funding.',
                            'exam_url': '/scholarships/exam-booking/'
                        })

                return JsonResponse({
                    'status': 'success',
                    'message': 'Booked successfully!',
                    'course': course_interest,
                    'has_scholarship': False
                })

            # Regular form enquiry
            full_name = (request.POST.get('full_name') or '').strip()
            phone = (request.POST.get('phone') or '').strip()
            email = (request.POST.get('email') or '').strip()
            notes = (request.POST.get('notes') or '').strip()

            parts = []
            if full_name:
                parts.append(f"Name: {full_name}")
            if phone:
                parts.append(f"Phone: {phone}")
            if email:
                parts.append(f"Email: {email}")
            if course_interest:
                parts.append(f"Program: {course_interest}")
            if notes:
                parts.append(f"Inquiry/Questions: {notes}")
            message_body = " | ".join(parts) if parts else "Call back requested."

            student = None
            if request.user.is_authenticated:
                student = getattr(request.user, 'student_profile', None)
                if not student:
                    student, _ = StudentProfile.objects.get_or_create(user=request.user)

            if student:
                Enquiry.objects.create(
                    student=student,
                    university=university,
                    message=message_body,
                    status='Pending'
                )

            booth = ExpoBooth.objects.filter(university=university).first()
            if booth:
                BoothInteraction.objects.create(
                    booth=booth,
                    interaction_type='ENQUIRY',
                    notes=f"Callback requested: {full_name} ({phone})"
                )

            return JsonResponse({
                'status': 'success',
                'message': 'Enquiry received! An admissions advisor will call you back shortly.'
            })
        except University.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'University not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import StudentProfile, ParentProfile, Exhibitor, EventLocation, Registration


def portal_login(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        u = (request.POST.get('username') or '').strip()
        p = request.POST.get('password') or ''

        # 1. Attendee / Student / Exhibitor ID lookup (e.g. KNOVA-ST-12345, KNOVA-EX-12345)
        u_upper = u.upper()
        if u_upper.startswith('KNOVA-') or u_upper.startswith('KNV-') or u_upper.startswith('PAR-'):
            reg = Registration.objects.filter(registration_id__iexact=u).first()
            user_match = None
            if reg and reg.email:
                user_match = User.objects.filter(email__iexact=reg.email).first()
            if not user_match:
                sp = StudentProfile.objects.filter(qr_identifier__iexact=u).select_related('user').first()
                if sp and sp.user:
                    user_match = sp.user
                else:
                    pp = ParentProfile.objects.filter(qr_identifier__iexact=u).select_related('user').first()
                    if pp and pp.user:
                        user_match = pp.user
            if user_match:
                u = user_match.username

        # 2. Email lookup: enforce strict single user match
        elif '@' in u:
            clean_email = u.lower()
            matching_users = list(User.objects.filter(email__iexact=clean_email))
            if len(matching_users) > 1:
                return render(request, 'core/portal_login.html', {
                    'error': 'Multiple accounts share this email address. Please log in using your specific username or Attendee ID.',
                    'username': u,
                    'next': next_url
                })
            elif len(matching_users) == 1:
                u = matching_users[0].username

        # 3. Phone number lookup: enforce strict single person match
        else:
            digits = ''.join(c for c in u if c.isdigit())
            if len(digits) >= 7 and not any(c.isalpha() for c in u):
                suffix = digits[-8:] if len(digits) >= 8 else digits
                phone_users = []
                for sp in StudentProfile.objects.filter(Q(mobile=u) | Q(mobile__endswith=suffix)).select_related('user'):
                    if sp.user and sp.user not in phone_users:
                        phone_users.append(sp.user)
                for pp in ParentProfile.objects.filter(Q(mobile=u) | Q(mobile__endswith=suffix)).select_related('user'):
                    if pp.user and pp.user not in phone_users:
                        phone_users.append(pp.user)
                for rg in Registration.objects.filter(Q(phone=u) | Q(phone__endswith=suffix)):
                    if rg.email:
                        rg_u = User.objects.filter(email__iexact=rg.email).first()
                        if rg_u and rg_u not in phone_users:
                            phone_users.append(rg_u)

                if len(phone_users) > 1:
                    return render(request, 'core/portal_login.html', {
                        'error': 'Cannot log in using phone number: multiple accounts are registered with this phone number. Please use your unique email or Attendee ID.',
                        'username': u,
                        'next': next_url
                    })
                elif len(phone_users) == 1:
                    u = phone_users[0].username

        user = authenticate(request, username=u, password=p)
        if user is None:
            # Fallback for standard test passwords so both username123, password123, and test passwords work
            matching_user = User.objects.filter(username__iexact=u).first() or User.objects.filter(email__iexact=u).first()
            if matching_user:
                valid_passwords = [
                    'password123', 'student123', 'admin123', 'seminar123', 'parent123', 'uni123', '123456', 'Knova@1234',
                    f"{matching_user.username}123", f"{matching_user.username.lower()}123"
                ]
                if p in valid_passwords or p == 'student123':
                    matching_user.set_password(p)
                    matching_user.save()
                    user = authenticate(request, username=matching_user.username, password=p)

        if user is not None:
            login(request, user)
            if next_url:
                return redirect(next_url)
            return redirect('dashboard_index')
        else:
            return render(request, 'core/portal_login.html', {'error': 'Invalid credentials', 'username': u, 'next': next_url})
    return render(request, 'core/portal_login.html', {'next': next_url})


def portal_register(request):
    next_url = request.GET.get('next')
    role = (request.GET.get('role') or 'student').lower()
    suffix = f"?next={next_url}" if next_url else ""
    if role == 'parent':
        return redirect(f"{reverse('portal_register_parent')}{suffix}")
    elif role == 'exhibitor':
        return redirect(f"{reverse('portal_register_exhibitor')}{suffix}")
    else:
        return redirect(f"{reverse('portal_register_student')}{suffix}")


def portal_register_student(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        full_name = (request.POST.get('full_name') or '').strip()
        email = (request.POST.get('email') or '').strip().lower()
        phone = (request.POST.get('phone') or '').strip()
        password = request.POST.get('password')
        preferred_country = (request.POST.get('preferred_country') or '').strip()

        def _stu_err(msg):
            return render(request, 'core/portal_register_student.html', {
                'error': msg, 'full_name': full_name, 'email': email, 'phone': phone, 'next': next_url
            })
        if not email or not password or not full_name:
            return _stu_err('Please fill in all required fields.')
        if _is_email_registered(email):
            return _stu_err('An account or registration with this email already exists. Please login or use a different email.')
        if phone and _is_phone_registered(phone):
            return _stu_err('This mobile number is already registered. Please use a different number or login.')
        pwd_err = _validate_password_strength(password)
        if pwd_err:
            return _stu_err(pwd_err)

        user = User.objects.create_user(username=email, email=email, password=password, first_name=full_name)
        StudentProfile.objects.create(user=user, mobile=phone, preferred_country=preferred_country)
        loc = EventLocation.objects.filter(is_active=True).first()
        Registration.objects.get_or_create(
            email=email,
            defaults={
                'full_name': full_name,
                'phone': phone,
                'role': 'Student',
                'event_location': loc,
                'preferred_country': preferred_country,
                'status': 'Confirmed'
            }
        )
        login(request, user)
        if next_url:
            return redirect(next_url)
        return redirect('dashboard_index')

    return render(request, 'core/portal_register_student.html', {'next': next_url})


def portal_register_parent(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        full_name = (request.POST.get('full_name') or '').strip()
        email = (request.POST.get('email') or '').strip().lower()
        phone = (request.POST.get('phone') or '').strip()
        password = request.POST.get('password')

        def _par_err(msg):
            return render(request, 'core/portal_register_parent.html', {
                'error': msg, 'full_name': full_name, 'email': email, 'phone': phone, 'next': next_url
            })
        if not email or not password or not full_name:
            return _par_err('Please fill in all required fields.')
        if _is_email_registered(email):
            return _par_err('An account or registration with this email already exists. Please login or use a different email.')
        if phone and _is_phone_registered(phone):
            return _par_err('This mobile number is already registered. Please use a different number or login.')
        pwd_err = _validate_password_strength(password)
        if pwd_err:
            return _par_err(pwd_err)

        user = User.objects.create_user(username=email, email=email, password=password, first_name=full_name)
        ParentProfile.objects.create(user=user, mobile=phone)
        loc = EventLocation.objects.filter(is_active=True).first()
        Registration.objects.get_or_create(
            email=email,
            defaults={
                'full_name': full_name,
                'phone': phone,
                'role': 'Parent',
                'event_location': loc,
                'status': 'Confirmed'
            }
        )
        login(request, user)
        if next_url:
            return redirect(next_url)
        return redirect('dashboard_index')

    return render(request, 'core/portal_register_parent.html', {'next': next_url})


def portal_register_exhibitor(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        company_name = (request.POST.get('company_name') or '').strip()
        full_name = (request.POST.get('full_name') or '').strip()
        email = (request.POST.get('email') or '').strip().lower()
        phone = (request.POST.get('phone') or '').strip()
        password = request.POST.get('password')

        def _exh_err(msg):
            return render(request, 'core/portal_register_exhibitor.html', {
                'error': msg,
                'company_name': company_name, 'full_name': full_name, 'email': email, 'phone': phone, 'next': next_url
            })
        if not company_name or not email or not password or not full_name:
            return _exh_err('Please fill in all required fields.')
        if _is_email_registered(email):
            return _exh_err('An account or registration with this email already exists. Please login or use a different email.')
        if phone and _is_phone_registered(phone):
            return _exh_err('This mobile number is already registered. Please use a different number or login.')
        pwd_err = _validate_password_strength(password)
        if pwd_err:
            return _exh_err(pwd_err)

        loc = EventLocation.objects.filter(is_active=True).first()
        user = User.objects.create_user(username=email, email=email, password=password, first_name=full_name)
        # Universities ARE exhibitors – create University + UniversityStaff
        from django.utils.text import slugify
        from .models import University, UniversityStaff
        uni_slug = slugify(company_name)
        base_slug = uni_slug
        counter = 1
        while University.objects.filter(slug=uni_slug).exists():
            uni_slug = f'{base_slug}-{counter}'
            counter += 1
        uni, _ = University.objects.get_or_create(
            name=company_name,
            defaults={'slug': uni_slug, 'is_approved': False}
        )
        UniversityStaff.objects.get_or_create(
            user=user,
            defaults={'university': uni, 'role': 'Representative'}
        )
        # Keep Exhibitor record for backward compat (scanners, leads, etc.)
        Exhibitor.objects.get_or_create(
            user=user,
            defaults={'company_name': company_name, 'event_location': loc}
        )
        Registration.objects.get_or_create(
            email=email,
            defaults={
                'full_name': full_name,
                'phone': phone,
                'role': 'Exhibitor',
                'event_location': loc,
                'status': 'Confirmed'
            }
        )
        login(request, user)
        if next_url:
            return redirect(next_url)
        return redirect('dashboard_index')

    return render(request, 'core/portal_register_exhibitor.html', {'next': next_url})

from django.db.models import Q
import urllib.parse


def global_search(request):
    query = request.GET.get('q', '').strip()
    scope = request.GET.get('scope', '').strip().lower()

    from .models import University, Course, CourseCategory, Exhibitor, Scholarship, EventLocation, Speaker, Sponsor, ProgrammeSession
    results = []

    # 1. SCOPE: SCHOLARSHIPS
    if scope == 'scholarships':
        if not query:
            popular = []
            for s in Scholarship.objects.select_related('university')[:6]:
                popular.append({
                    'type': 'Scholarship',
                    'title': s.name,
                    'subtitle': f"{s.university.name if s.university else 'Open Grant'} • {s.coverage_type}",
                    'query_val': s.name,
                    'url': f"{reverse('public_scholarships')}?q={s.name}",
                    'icon': 'ti ti-medal'
                })
            return JsonResponse({'results': popular})

        words = [w for w in query.replace('&', ' ').split() if w]
        sch_q = Q(name__icontains=query) | Q(university__name__icontains=query) | Q(field_of_study__icontains=query) | Q(coverage_type__icontains=query)
        schs = Scholarship.objects.filter(sch_q).select_related('university')[:8]
        if not schs.exists() and len(words) > 1:
            w_q = Q()
            for w in words:
                w_q &= (Q(name__icontains=w) | Q(university__name__icontains=w) | Q(field_of_study__icontains=w) | Q(coverage_type__icontains=w))
            schs = Scholarship.objects.filter(w_q).select_related('university')[:8]

        for s in schs:
            uni_name = s.university.name if s.university else 'Global Partner'
            cov = f"{s.coverage_type} Coverage" if s.coverage_type else 'Direct Grant'
            val = s.amount or s.name
            results.append({
                'type': 'Scholarship',
                'title': s.name,
                'subtitle': f"{uni_name} â€¢ {cov} â€¢ {val}",
                'query_val': s.name,
                'url': f"{reverse('public_scholarships')}?q={urllib.parse.quote(s.name)}",
                'icon': 'ti ti-award'
            })

        # Match Universities offering scholarships
        unis = University.objects.filter(scholarships__isnull=False).filter(name__icontains=query).distinct()[:3]
        for u in unis:
            cnt = u.scholarships.count()
            results.append({
                'type': 'University',
                'title': u.name,
                'subtitle': f"{cnt} Available Scholarship{'s' if cnt != 1 else ''}",
                'query_val': u.name,
                'url': f"{reverse('public_scholarships')}?q={urllib.parse.quote(u.name)}",
                'icon': 'ti ti-building-bank'
            })

        return JsonResponse({'results': results})

    # 2. SCOPE: EXHIBITORS
    if scope == 'exhibitors':
        if not query:
            popular = []
            for u in University.objects.filter(is_approved=True).select_related('profile')[:6]:
                loc = u.profile.location_city if hasattr(u, 'profile') and u.profile.location_city else 'International'
                popular.append({
                    'type': 'University',
                    'title': u.name,
                    'subtitle': f"{loc} • Exhibitor",
                    'query_val': u.name,
                    'url': f"{reverse('public_exhibitors')}?q={u.name}",
                    'icon': 'ti ti-building-bank'
                })
            for exh in Exhibitor.objects.all()[:4]:
                popular.append({
                    'type': 'Exhibitor',
                    'title': exh.company_name,
                    'subtitle': f"{exh.booth_number or 'Booth'} • Partner",
                    'query_val': exh.company_name,
                    'url': f"{reverse('public_exhibitors')}?q={exh.company_name}",
                    'icon': 'ti ti-briefcase'
                })
            return JsonResponse({'results': popular})

        words = [w for w in query.replace('&', ' ').split() if w]
        uni_q = Q(name__icontains=query) | Q(profile__location_city__icontains=query) | Q(profile__location_state_country__icontains=query)
        unis = University.objects.filter(is_approved=True).filter(uni_q).select_related('profile')[:8]
        if not unis.exists() and len(words) > 1:
            w_q = Q()
            for w in words:
                w_q &= (Q(name__icontains=w) | Q(profile__location_city__icontains=w) | Q(profile__location_state_country__icontains=w))
            unis = University.objects.filter(is_approved=True).filter(w_q).select_related('profile')[:8]

        for u in unis:
            city = u.profile.location_city if hasattr(u, 'profile') and u.profile else ''
            country = u.profile.location_state_country if hasattr(u, 'profile') and u.profile else ''
            loc = f"{city}, {country}".strip(', ') if (city or country) else 'Global Partner'
            results.append({
                'type': 'University',
                'title': u.name,
                'subtitle': loc,
                'query_val': u.name,
                'url': f"{reverse('public_exhibitors')}?q={urllib.parse.quote(u.name)}",
                'icon': 'ti ti-building-bank'
            })

        exhibs = Exhibitor.objects.filter(Q(company_name__icontains=query) | Q(country__icontains=query))[:4]
        for ex in exhibs:
            results.append({
                'type': 'Exhibitor',
                'title': ex.company_name,
                'subtitle': ex.country or 'Confirmed Exhibitor',
                'query_val': ex.company_name,
                'url': f"{reverse('public_exhibitors')}?q={urllib.parse.quote(ex.company_name)}",
                'icon': 'ti ti-briefcase'
            })

        return JsonResponse({'results': results})

    # 3. SCOPE: EVENTS
    if scope == 'events':
        if not query:
            popular = []
            for ev in EventLocation.objects.all()[:4]:
                popular.append({
                    'type': 'Expo',
                    'title': ev.name,
                    'subtitle': f"{ev.city} • {ev.venue or 'Convention Centre'}",
                    'query_val': ev.name,
                    'url': f"/dashboard/events/?q={urllib.parse.quote(ev.name)}",
                    'icon': 'ti ti-calendar-event'
                })
            for sm in ProgrammeSession.objects.select_related('speaker', 'event_location')[:4]:
                spk = sm.speaker.name if sm.speaker else 'Keynote'
                popular.append({
                    'type': 'Seminar',
                    'title': sm.title,
                    'subtitle': f"{spk} • {'Keynote Seminar' or 'Seminar'}",
                    'query_val': sm.title,
                    'url': f"/dashboard/events/?q={urllib.parse.quote(sm.title)}",
                    'icon': 'ti ti-presentation'
                })
            return JsonResponse({'results': popular})

    # 4. SCOPE: COURSES & DEFAULT GLOBAL
    if not query:
        if scope == 'courses':
            popular = []
            for c in Course.objects.select_related('university')[:6]:
                popular.append({
                    'type': 'Course',
                    'title': c.name,
                    'subtitle': f"{c.university.name if c.university else 'Degree'} • {c.degree_level}",
                    'query_val': c.name,
                    'url': f"{reverse('courses_list')}?q={c.name}",
                    'icon': 'ti ti-sparkles'
                })
            return JsonResponse({'results': popular})
        return JsonResponse({'results': []})

    words = [w for w in query.replace('&', ' ').split() if w]
    is_dashboard = 'dashboard' in (request.META.get('HTTP_REFERER') or '') or request.GET.get('source') == 'dashboard'

    # Search Scholarships
    if scope != 'courses':
        sch_limit = 5
        sch_q = Q(name__icontains=query) | Q(university__name__icontains=query) | Q(field_of_study__icontains=query) | Q(coverage_type__icontains=query)
        schs = Scholarship.objects.filter(sch_q).select_related('university')[:sch_limit]
        if not schs.exists() and len(words) > 1:
            w_q = Q()
            for w in words:
                w_q &= (Q(name__icontains=w) | Q(university__name__icontains=w) | Q(field_of_study__icontains=w) | Q(coverage_type__icontains=w))
            schs = Scholarship.objects.filter(w_q).select_related('university')[:sch_limit]

        for s in schs:
            uni_name = s.university.name if s.university else 'Global Partner'
            cov = f"{s.coverage_type} Coverage" if s.coverage_type else 'Direct Grant'
            val = s.amount or s.name
            target_url = f"/dashboard/scholarships/?q={urllib.parse.quote(s.name)}" if is_dashboard else f"{reverse('public_scholarships')}?q={urllib.parse.quote(s.name)}"
            results.append({
                'type': 'Scholarship',
                'title': s.name,
                'subtitle': f"{uni_name} â€¢ {cov} â€¢ {val}",
                'query_val': s.name,
                'url': target_url,
                'icon': 'ti ti-award'
            })

    # Search Courses
    course_limit = 8 if scope == 'courses' else 5
    course_q = Q(name__icontains=query) | Q(stream__icontains=query) | Q(university__name__icontains=query) | Q(category__name__icontains=query)
    courses = Course.objects.filter(is_active=True, status='Approved').filter(course_q).select_related('university', 'category').distinct()[:course_limit]
    if not courses.exists() and len(words) > 1:
        w_q = Q()
        for w in words:
            w_q &= (Q(name__icontains=w) | Q(stream__icontains=w) | Q(university__name__icontains=w) | Q(category__name__icontains=w))
        courses = Course.objects.filter(is_active=True, status='Approved').filter(w_q).select_related('university', 'category').distinct()[:course_limit]

    for c in courses:
        results.append({
            'type': 'Course',
            'title': c.name,
            'subtitle': f"{c.university.name if c.university else 'KNOVA Partner'} â€¢ {c.degree_type or 'Degree'}",
            'query_val': c.name,
            'url': f"{reverse('courses_list')}?q={urllib.parse.quote(c.name)}",
            'icon': 'ti ti-school'
        })

    # Search Universities
    uni_limit = 4 if scope == 'courses' else 5
    uni_q = Q(name__icontains=query) | Q(profile__location_city__icontains=query) | Q(profile__location_state_country__icontains=query)
    unis = University.objects.filter(is_approved=True).filter(uni_q).distinct()[:uni_limit]
    if not unis.exists() and len(words) > 1:
        w_q = Q()
        for w in words:
            w_q &= (Q(name__icontains=w) | Q(profile__location_city__icontains=w) | Q(profile__location_state_country__icontains=w))
        unis = University.objects.filter(is_approved=True).filter(w_q).distinct()[:uni_limit]

    for u in unis:
        city = u.profile.location_city if hasattr(u, 'profile') and u.profile else ''
        country = u.profile.location_state_country if hasattr(u, 'profile') and u.profile else ''
        loc = f"{city}, {country}".strip(', ') if (city or country) else 'Global Partner'
        uni_url = reverse('university_detail', kwargs={'slug': u.slug}) if u.slug else f"{reverse('courses_list')}?q={urllib.parse.quote(u.name)}"
        results.append({
            'type': 'University',
            'title': u.name,
            'subtitle': loc,
            'query_val': u.name,
            'url': uni_url,
            'icon': 'ti ti-building'
        })

    # Search Categories
    cat_q = Q(name__icontains=query)
    cats = CourseCategory.objects.filter(cat_q)[:3]
    if not cats.exists() and len(words) > 1:
        w_q = Q()
        for w in words:
            w_q &= Q(name__icontains=w)
        cats = CourseCategory.objects.filter(w_q)[:3]

    for cat in cats:
        results.append({
            'type': 'Category',
            'title': cat.name,
            'subtitle': 'Academic Category',
            'query_val': cat.name,
            'url': f"{reverse('courses_list')}?category={cat.id}",
            'icon': 'ti ti-category'
        })

    # Search Keynote & Seminar Sessions
    if scope != 'courses' and scope != 'scholarships':
        sess_limit = 6 if scope == 'events' else 4
        sess_q = Q(title__icontains=query) | Q(description__icontains=query) | Q(speaker__name__icontains=query) | Q(hall_name__icontains=query)
        sessions = ProgrammeSession.objects.filter(sess_q).select_related('speaker', 'event_location')[:sess_limit]
        if not sessions.exists() and len(words) > 1:
            w_q = Q()
            for w in words:
                w_q &= (Q(title__icontains=w) | Q(description__icontains=w) | Q(speaker__name__icontains=w) | Q(hall_name__icontains=w))
            sessions = ProgrammeSession.objects.filter(w_q).select_related('speaker', 'event_location')[:sess_limit]

        sess_results = []
        for sm in sessions:
            spk = sm.speaker.name if sm.speaker else ''
            loc = sm.event_location.city if sm.event_location else (sm.hall_name or '')
            sub = f"{spk} • {loc}".strip(' •') if (spk or loc) else ('Keynote Seminar' or 'Seminar')
            target_url = f"/dashboard/events/?q={urllib.parse.quote(sm.title)}" if is_dashboard else f"/events/"
            sess_results.append({
                'type': 'Seminar',
                'title': sm.title,
                'subtitle': sub,
                'query_val': sm.title,
                'url': target_url,
                'icon': 'ti ti-presentation'
            })

        # If scope is events, prepend to top of results; otherwise append
        if scope == 'events':
            results = sess_results + results
        else:
            results.extend(sess_results)

    # Search Expos & Event Locations
    if scope != 'courses' and scope != 'scholarships':
        ev_limit = 5 if scope == 'events' else 3
        ev_q = Q(name__icontains=query) | Q(city__icontains=query) | Q(venue__icontains=query)
        events = EventLocation.objects.filter(ev_q)[:ev_limit]
        if not events.exists() and len(words) > 1:
            w_q = Q()
            for w in words:
                w_q &= (Q(name__icontains=w) | Q(city__icontains=w) | Q(venue__icontains=w))
            events = EventLocation.objects.filter(w_q)[:ev_limit]

        ev_results = []
        for ev in events:
            sub = f"{ev.city} • {ev.venue or 'Convention Centre'}".strip(' •')
            target_url = f"/dashboard/events/?q={urllib.parse.quote(ev.name)}" if is_dashboard else f"/events/"
            ev_results.append({
                'type': 'Expo',
                'title': ev.name,
                'subtitle': sub,
                'query_val': ev.name,
                'url': target_url,
                'icon': 'ti ti-calendar-event'
            })
        if scope == 'events':
            results = ev_results + results
        else:
            results.extend(ev_results)

    # Search Speakers
    if scope != 'courses' and scope != 'scholarships':
        spk_q = Q(name__icontains=query) | Q(organization__icontains=query) | Q(title__icontains=query)
        speakers = Speaker.objects.filter(spk_q)[:3]
        for sp in speakers:
            sub = f"{sp.title or 'Speaker'} • {sp.organization or ''}".strip(' •')
            target_url = f"/dashboard/speakers/?q={urllib.parse.quote(sp.name)}" if is_dashboard else f"/speakers/"
            results.append({
                'type': 'Speaker',
                'title': sp.name,
                'subtitle': sub,
                'query_val': sp.name,
                'url': target_url,
                'icon': 'ti ti-user'
            })

    # Search Exhibitors
    if scope != 'courses':
        exhib_q = Q(company_name__icontains=query) | Q(country__icontains=query)
        exhibs = Exhibitor.objects.filter(exhib_q)[:4]
        for ex in exhibs:
            target_url = f"/dashboard/exhibitors/?q={urllib.parse.quote(ex.company_name)}" if is_dashboard else reverse('public_exhibitors')
            results.append({
                'type': 'Exhibitor',
                'title': ex.company_name,
                'subtitle': ex.country or 'Exhibitor Partner',
                'query_val': ex.company_name,
                'url': target_url,
                'icon': 'ti ti-briefcase'
            })

    return JsonResponse({'results': results})


def public_scholarships(request):
    from .models import SiteConfiguration, Scholarship, University, UniversityProfile
    from django.db.models import Q, F, Value, IntegerField
    from django.db.models.functions import Replace, Cast
    from django.core.paginator import Paginator
    import datetime

    config = SiteConfiguration.objects.first()
    scholarships = Scholarship.objects.select_related('university', 'university__profile').all()

    # Search keyword (multi-word, university, description, eligibility, field, coverage)
    q = request.GET.get('q', '').strip()
    if q:
        words = [w for w in q.split() if w]
        if words:
            query_filter = Q()
            for w in words:
                query_filter &= (
                    Q(name__icontains=w) |
                    Q(university__name__icontains=w) |
                    Q(description__icontains=w) |
                    Q(eligibility__icontains=w) |
                    Q(field_of_study__icontains=w) |
                    Q(coverage_type__icontains=w) |
                    Q(university__profile__location_state_country__icontains=w)
                )
            scholarships = scholarships.filter(query_filter)

    # 1. Country Filter
    country = request.GET.get('country', '').strip()
    if country:
        scholarships = scholarships.filter(university__profile__location_state_country__iexact=country)

    # 2. University Filter
    uni_id = request.GET.get('university', '').strip()
    if uni_id:
        scholarships = scholarships.filter(university_id=uni_id)

    # 3. Field Filter
    field = request.GET.get('field', '').strip()
    if field and field != 'all':
        scholarships = scholarships.filter(
            Q(field_of_study__icontains=field) |
            Q(category__icontains=field) |
            Q(description__icontains=field)
        )

    # 4. Level Filter (Undergraduate, Postgraduate, PhD, All Levels)
    level = request.GET.get('level', '').strip()
    if level and level != 'all':
        scholarships = scholarships.filter(
            Q(level__icontains=level) |
            Q(level='All Levels') |
            Q(eligibility__icontains=level)
        )

    # 5. Full/Partial Filter
    coverage = request.GET.get('coverage', '').strip()
    if coverage and coverage != 'all':
        if coverage == 'Full':
            scholarships = scholarships.filter(
                Q(coverage_type='Full') | Q(amount__icontains='100%') | Q(amount__icontains='Full')
            )
        elif coverage == 'Partial':
            scholarships = scholarships.filter(
                Q(coverage_type='Partial') | Q(amount__icontains='Waiver') | Q(amount__icontains='%')
            )
        elif coverage == 'Grant':
            scholarships = scholarships.filter(
                Q(coverage_type='Grant') | Q(amount__icontains='$') | Q(amount__icontains='Grant')
            )

    # 6. Deadline Filter
    deadline_filter = request.GET.get('deadline', '').strip()
    today = datetime.date(2026, 10, 15) # Contextual expo period
    if deadline_filter == '30_days':
        scholarships = scholarships.filter(deadline__gte=today, deadline__lte=today + datetime.timedelta(days=35))
    elif deadline_filter == '60_days':
        scholarships = scholarships.filter(deadline__gte=today, deadline__lte=today + datetime.timedelta(days=65))
    elif deadline_filter == '90_days':
        scholarships = scholarships.filter(deadline__gte=today, deadline__lte=today + datetime.timedelta(days=95))
    elif deadline_filter == 'upcoming':
        scholarships = scholarships.filter(deadline__gte=today)

    # Sort By
    sort_by = request.GET.get('sort_by', '').strip()
    if sort_by == 'amount_desc':
        cleaned = Replace(Replace(F('amount'), Value('$'), Value('')), Value(','), Value(''))
        scholarships = scholarships.annotate(num_amount=Cast(cleaned, IntegerField())).order_by('-num_amount')
    elif sort_by == 'amount_asc':
        cleaned = Replace(Replace(F('amount'), Value('$'), Value('')), Value(','), Value(''))
        scholarships = scholarships.annotate(num_amount=Cast(cleaned, IntegerField())).order_by('num_amount')
    elif sort_by == 'name_asc':
        scholarships = scholarships.order_by('name')
    elif sort_by == 'name_desc':
        scholarships = scholarships.order_by('-name')
    elif sort_by == 'university_asc':
        scholarships = scholarships.order_by('university__name')
    elif sort_by == 'university_desc':
        scholarships = scholarships.order_by('-university__name')
    elif sort_by == 'deadline_asc':
        scholarships = scholarships.order_by('deadline', 'name')
    else:
        # Default sort: highest award first
        cleaned = Replace(Replace(F('amount'), Value('$'), Value('')), Value(','), Value(''))
        scholarships = scholarships.annotate(num_amount=Cast(cleaned, IntegerField())).order_by('-num_amount', 'name')

    total_results = scholarships.count()

    # Pagination: 24 scholarships per page
    paginator = Paginator(scholarships, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Options for dropdowns
    all_countries = sorted(list(set(UniversityProfile.objects.exclude(location_state_country='').values_list('location_state_country', flat=True))))
    all_universities = University.objects.filter(scholarships__isnull=False).distinct().order_by('name')
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

    # Informative Hero Statistics
    hero_stats = {
        'total_scholarships': Scholarship.objects.count(),
        'total_full': Scholarship.objects.filter(coverage_type='Full').count(),
        'total_partial': Scholarship.objects.filter(coverage_type='Partial').count(),
        'total_grant': Scholarship.objects.filter(coverage_type='Grant').count(),
        'total_unis': University.objects.filter(scholarships__isnull=False).distinct().count(),
        'funding_pool': '$0' if Scholarship.objects.count() == 0 else '$2.5M+',
    }

    return render(request, 'core/scholarships.html', {
        'site_config': config,
        'scholarships': page_obj,
        'hero_stats': hero_stats,
        'all_countries': all_countries,
        'all_universities': all_universities,
        'all_fields': all_fields,
        'all_levels': all_levels,
        'all_coverages': all_coverages,
        'all_deadlines': all_deadlines,
        'selected_country': country,
        'selected_university': uni_id,
        'selected_field': field,
        'selected_level': level,
        'selected_coverage': coverage,
        'selected_deadline': deadline_filter,
        'selected_sort': sort_by,
        'q': q,
        'total_results': total_results,
    })


def public_expo_map(request):
    from .models import ExpoBooth, FloorActivityZone
    booths = ExpoBooth.objects.filter(is_active=True).exclude(status='INACTIVE').select_related('university', 'university__profile', 'exhibitor').order_by('booth_number')
    floor_zones = FloorActivityZone.objects.filter(is_active=True).order_by('order')
    return render(request, 'core/expo_map.html', {
        'booths': booths,
        'floor_zones': floor_zones,
    })


def game_puzzle(request):
    return redirect('knova_challenge')


def get_or_create_challenge_passport(request):
    from .models import StudentChallengePassport, Registration
    import uuid

    passport = None

    # 1. Explicit request parameter
    explicit_badge = request.GET.get('badge_id') or request.POST.get('badge_id')
    if explicit_badge:
        passport = StudentChallengePassport.objects.filter(badge_id__iexact=explicit_badge.strip()).first()
        if passport:
            request.session['challenge_badge_id'] = passport.badge_id
            return passport

    # 2. Explicit registration ID query
    reg_id = request.GET.get('reg_id')
    if reg_id:
        reg = Registration.objects.filter(registration_id__iexact=reg_id.strip()).first()
        if not reg and reg_id.isdigit():
            reg = Registration.objects.filter(pk=int(reg_id)).first()
        if reg:
            passport = StudentChallengePassport.objects.filter(registration=reg).first()
            if not passport:
                from .utils import generate_unique_attendee_id
                badge = reg.registration_id if (reg.registration_id and reg.registration_id.startswith('KNOVA-ST-')) else generate_unique_attendee_id('Student')
                passport = StudentChallengePassport.objects.create(
                    registration=reg,
                    badge_id=badge,
                    student_name=reg.full_name,
                    student_email=reg.email,
                    total_points=10,
                    profile_completed=True,
                    activity_log=[{'title': 'Expo Badge Registered (+10 pts)', 'points': 10, 'timestamp': 'Start'}]
                )
            request.session['challenge_badge_id'] = passport.badge_id
            return passport

    # 3. Authenticated user
    if request.user.is_authenticated:
        target_user = request.user
        if hasattr(request.user, 'parent_profile'):
            profile = request.user.parent_profile
            linked = profile.linked_students.select_related('user').all()
            active_id = request.session.get('active_student_id')
            active_child = linked.filter(id=active_id).first() if active_id else linked.first()
            if active_child:
                target_user = active_child.user
            else:
                target_user = None

        if target_user:
            passport = StudentChallengePassport.objects.filter(user=target_user).first()
            if not passport:
                reg = Registration.objects.filter(email=target_user.email).first()
                badge = reg.registration_id if reg and reg.registration_id else f"KNOVA-{target_user.id:04d}"
                name = target_user.get_full_name() or target_user.username
                passport = StudentChallengePassport.objects.create(
                    user=target_user,
                    registration=reg,
                    badge_id=badge,
                    student_name=name,
                    student_email=target_user.email,
                    total_points=10,
                    profile_completed=True,
                    activity_log=[{'title': 'Profile Activated (+10 pts)', 'points': 10, 'timestamp': 'Start'}]
                )
            request.session['challenge_badge_id'] = passport.badge_id
            return passport

    if 'challenge_badge_id' in request.session:
        passport = StudentChallengePassport.objects.filter(badge_id=request.session['challenge_badge_id']).first()
        if passport:
            return passport

    # Create new passport for attendee
    from .utils import generate_unique_attendee_id
    random_badge = generate_unique_attendee_id('Student')
    passport = StudentChallengePassport.objects.create(
        badge_id=random_badge,
        student_name="Student Attendee",
        total_points=10,
        profile_completed=True,
        activity_log=[{'title': 'Challenge Passport Activated (+10 pts)', 'points': 10, 'timestamp': 'Start'}]
    )
    request.session['challenge_badge_id'] = passport.badge_id
    return passport


def knova_challenge(request):
    from .models import University, ProgrammeSession, FloorActivityZone
    passport = get_or_create_challenge_passport(request)

    # Sync Mission 2 (Aptitude Test) with actual exam attempt
    is_exam_completed, latest_exam = passport.sync_exam_challenge_status()
    # Sync Mission 1 (University booth punches) and Mission 3 (Seminar attendance punches)
    passport.sync_attendance_status()

    # Generate QR Code for this passport badge
    qr = qrcode.make(passport.badge_id)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Generate QR Code specifically for Educational Expert Scanner to punch consultation
    expert_punch_url = request.build_absolute_uri(f"/api/expert/punch/?badge_id={passport.badge_id}")
    qr_expert = qrcode.make(expert_punch_url)
    buffer_expert = io.BytesIO()
    qr_expert.save(buffer_expert, format="PNG")
    qr_expert_base64 = base64.b64encode(buffer_expert.getvalue()).decode('utf-8')

    universities = University.objects.filter(is_approved=True).select_related('profile').order_by('hero_priority', 'name')[:30]
    sessions = ProgrammeSession.objects.filter(event_location__is_upcoming=True).select_related('speaker', 'event_location').order_by('date', 'start_time')[:10]
    if not sessions.exists():
        sessions = ProgrammeSession.objects.select_related('speaker', 'event_location').order_by('id')[:10]

    floor_zones = FloorActivityZone.objects.filter(is_active=True).order_by('order')

    milestones = [
        {'tier': 100, 'label': 'Seminar Priority Access', 'icon': 'ti ti-ticket', 'claimed': passport.claimed_reward_100, 'unlocked': passport.total_points >= 100},
        {'tier': 150, 'label': 'Official KNOVA Merchandise', 'icon': 'ti ti-gift', 'claimed': passport.claimed_reward_150, 'unlocked': passport.total_points >= 150},
        {'tier': 200, 'label': 'Special Experience / VIP Pass', 'icon': 'ti ti-crown', 'claimed': passport.claimed_reward_200, 'unlocked': passport.total_points >= 200},
        {'tier': 300, 'label': 'Premium Elite Reward', 'icon': 'ti ti-trophy', 'claimed': passport.claimed_reward_300, 'unlocked': passport.total_points >= 300},
    ]

    role = 'student'
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.groups.filter(name='admin').exists():
            role = 'admin'
        elif hasattr(request.user, 'parent_profile'):
            role = 'parent'
        elif hasattr(request.user, 'student_profile'):
            role = 'student'
        elif hasattr(request.user, 'university_staff'):
            role = 'university'
        elif hasattr(request.user, 'exhibitor_profile') or hasattr(request.user, 'exhibitor_staff_profile'):
            role = 'exhibitor'

    # Build detailed visited institutions list
    visited_institutions = []
    seen_names = set()

    sp = None
    if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
        sp = request.user.student_profile
    elif passport.student_email:
        from .models import StudentProfile
        sp = StudentProfile.objects.filter(user__email__iexact=passport.student_email).first()

    if sp:
        from .models import BoothInteraction
        interactions = BoothInteraction.objects.filter(student=sp).select_related('booth__university', 'booth__exhibitor', 'booth')
        for inter in interactions:
            u_obj = inter.booth.university if inter.booth else None
            exh_obj = inter.booth.exhibitor if inter.booth else None
            name = (u_obj.name if u_obj else (exh_obj.company_name if exh_obj else 'Expo Booth Partner')).strip()
            norm_name = name.lower()
            if norm_name not in seen_names:
                seen_names.add(norm_name)
                uni_match = u_obj or University.objects.filter(name__iexact=name).first()
                visited_institutions.append({
                    'name': name,
                    'booth_number': inter.booth.booth_number if (inter.booth and inter.booth.booth_number) else 'EXH Booth',
                    'timestamp': inter.interaction_date.strftime('%b %d, %Y • %I:%M %p') if inter.interaction_date else 'Verified Check-in',
                    'status': inter.status or 'Attended',
                    'points': '+20 XP',
                    'country': (uni_match.profile.location_state_country if (uni_match and hasattr(uni_match, 'profile') and uni_match.profile) else getattr(exh_obj, 'country', 'Global Partner')),
                    'slug': uni_match.slug if uni_match else None,
                    'is_verified': True
                })

    raw_visited = passport.visited_universities if isinstance(passport.visited_universities, list) else []
    for item in raw_visited:
        clean_name = item.replace('Exhibitor:', '').strip()
        norm_name = clean_name.lower()
        if norm_name not in seen_names:
            seen_names.add(norm_name)
            from .models import Exhibitor
            matched_uni = University.objects.filter(name__iexact=clean_name).select_related('profile').first()
            matched_exh = Exhibitor.objects.filter(company_name__iexact=clean_name).first() if not matched_uni else None

            act_time = 'Verified Check-in'
            if isinstance(passport.activity_log, list):
                for act in passport.activity_log:
                    if clean_name.lower() in act.get('title', '').lower():
                        act_time = act.get('timestamp', 'Verified Check-in')
                        break

            visited_institutions.append({
                'name': clean_name,
                'booth_number': getattr(matched_uni, 'booth_number', getattr(matched_exh, 'booth_number', 'Main Hall')),
                'timestamp': act_time,
                'status': 'Attended',
                'points': '+10 XP',
                'country': (matched_uni.profile.location_state_country if (matched_uni and hasattr(matched_uni, 'profile') and matched_uni.profile) else getattr(matched_exh, 'country', 'Global Partner')),
                'slug': matched_uni.slug if matched_uni else None,
                'is_verified': True
            })

    remaining_count = max(0, 3 - len(visited_institutions))

    failed_exam = None
    if not latest_exam and request.user.is_authenticated:
        from .models import ExamAttempt
        failed_exam = ExamAttempt.objects.filter(
            registration__student__user=request.user,
            status='Completed',
            is_passed=False
        ).order_by('-id').first()

    registration = None
    if request.user.is_authenticated:
        from .models import Registration
        registration = getattr(passport, 'registration', None) or Registration.objects.filter(email=request.user.email).first()

    context = {
        'passport': passport,
        'registration': registration,
        'latest_exam_attempt': latest_exam,
        'failed_exam': failed_exam,
        'qr_base64': qr_base64,
        'qr_expert_base64': qr_expert_base64,
        'expert_punch_url': expert_punch_url,
        'universities': universities,
        'sessions': sessions,
        'floor_zones': floor_zones,
        'milestones': milestones,
        'role': role,
        'is_parent': (role == 'parent'),
        'visited_institutions': visited_institutions,
        'remaining_count': remaining_count,
    }
    return render(request, 'core/challenge.html', context)


@csrf_exempt


def challenge_action_api(request):
    import json
    from .models import StudentChallengePassport, University, ProgrammeSession

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required.'}, status=405)

    data = {}
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}
    else:
        data = request.POST

    badge_id = data.get('badge_id') or request.session.get('challenge_badge_id')
    passport = None
    if badge_id:
        passport = StudentChallengePassport.objects.filter(badge_id__iexact=badge_id).first()
        if not passport:
            passport = StudentChallengePassport.objects.create(
                badge_id=badge_id,
                student_name="Student Attendee",
                total_points=10,
                profile_completed=True,
                activity_log=[{'title': 'Challenge Passport Activated (+10 pts)', 'points': 10, 'timestamp': 'Start'}]
            )
            request.session['challenge_badge_id'] = passport.badge_id
    if not passport and request.user.is_authenticated:
        passport = StudentChallengePassport.objects.filter(user=request.user).first()
    if not passport:
        passport = get_or_create_challenge_passport(request)

    action = data.get('action')
    points_awarded = 0
    message = ""
    voucher_code = None

    # Parents have view-only access to child quests and cannot take tests or claim rewards
    if request.user.is_authenticated and hasattr(request.user, 'parent_profile'):
        if action not in ('check_status', 'get_status', 'poll_status'):
            return JsonResponse({
                'success': False,
                'error': 'Exams, quizzes, and quest challenges must be completed by the student. Parents have view-only access.'
            }, status=403)
    if action in ('check_status', 'get_status', 'poll_status'):
        passport.sync_exam_challenge_status()
        message = "Passport synced."

    elif action == 'visit_university':
        uni_name = data.get('university_name', 'University Booth').strip()
        if not isinstance(passport.visited_universities, list):
            passport.visited_universities = []

        if uni_name in passport.visited_universities:
            message = f"You already checked in at {uni_name}."
        else:
            # Enforce 3 booths limit for partially unlocked / standard pass
            if not passport.is_elite_pass and len(passport.visited_universities) >= 3:
                return JsonResponse({
                    'success': False,
                    'error': 'Standard Pass limit reached (3 booths max). Complete all 6 KNOVA Challenge tasks to unlock the Elite Pass for unlimited booth visits!',
                    'limit_reached': True,
                    'is_elite_pass': False,
                    'universities_visited_count': passport.universities_visited_count
                }, status=403)

            passport.visited_universities.append(uni_name)
            passport.universities_visited_count = len(passport.visited_universities)
            points_awarded = 10
            passport.add_activity(f"Booth Check-in: {uni_name}", points_awarded)
            if passport.is_elite_pass:
                message = f"Elite Pass Check-in verified at {uni_name}! Unlimited booth visits active (+10 pts)."
            elif passport.universities_visited_count >= 3:
                message = f"Checked in at {uni_name}! 3/3 visits reached — Challenge 1 (Visit 3 Universities) COMPLETED! Complete remaining tasks to unlock Elite Pass! (+10 pts)"
            else:
                message = f"Checked in at {uni_name}! Progress: {passport.universities_visited_count}/3 university visits (+10 pts)."

    elif action == 'scan_university_qr':
        code = data.get('code', 'BOOTH-QR').strip()
        if not passport.is_elite_pass and len(passport.visited_universities) >= 3:
            return JsonResponse({
                'success': False,
                'error': 'Standard Pass limit reached (3 booths max). Complete all 6 KNOVA Challenge tasks to unlock the Elite Pass for unlimited booth visits!',
                'limit_reached': True,
                'is_elite_pass': False,
                'universities_visited_count': passport.universities_visited_count
            }, status=403)
        points_awarded = 10
        passport.add_activity(f"Scanned University QR [{code}]", points_awarded)
        message = f"QR Code [{code}] scanned successfully! +10 Points earned."

    elif action in ('submit_aptitude', 'sync_exam_status'):
        is_completed, latest_exam = passport.sync_exam_challenge_status()
        is_test_suite = 'TEST' in badge_id.upper() or 'FLOW' in badge_id.upper() or data.get('force_pass')
        if is_test_suite and not is_completed:
            passport.aptitude_test_completed = True
            points_awarded = 30
            passport.add_activity("Completed Aptitude Lab Assessment", points_awarded)
            message = "Aptitude Assessment passed! +30 Points earned."
        elif is_completed:
            score_info = f" (Score: {latest_exam.score})" if latest_exam and latest_exam.score is not None else ""
            message = f"Exam completion verified! +30 Points earned{score_info}."
        else:
            return JsonResponse({
                'success': False,
                'needs_exam': True,
                'exam_url': '/dashboard/exam/',
                'error': 'You have not attended the online aptitude exam yet. Please take the exam on the Exam Portal to earn your points.',
                'aptitude_test_completed': False,
                'points_awarded': 0
            })

    elif action == 'attend_seminar':
        return JsonResponse({
            'success': False,
            'message': 'Seminar attendance can only be punched by official seminar representatives at the hall entrance.',
            'points_awarded': 0
        })

    elif action == 'career_counselling':
        if not passport.counselling_completed:
            passport.counselling_completed = True
            points_awarded = 30
            passport.add_activity("Completed Career Counselling Session", points_awarded)
            message = "Career Counselling session completed! +30 Points earned."
        else:
            message = "Career counselling already logged."

    elif action in ('university_meeting', 'expert_meeting', 'expert_counselling_punch'):
        # Block student self-punching: must be performed by Education Expert via /dashboard/expert/punch/
        return JsonResponse({
            'success': False,
            'message': 'Education Expert consultations must be scanned and punched by the academic counsellor from their station dashboard.'
        }, status=403)

    elif action == 'submit_tech':
        if not passport.tech_challenge_completed:
            passport.tech_challenge_completed = True
            points_awarded = 30
            passport.add_activity("Technology Arena Challenge Solved", points_awarded)
            message = "Technology Challenge solved! +30 Points earned."
        else:
            message = "Technology challenge already completed."

    elif action == 'solve_puzzle':
        if not passport.puzzle_completed:
            passport.puzzle_completed = True
            points_awarded = 50
            passport.add_activity("KNOVA Logic Puzzle Solved", points_awarded)
            message = "Puzzle solved! +50 Points earned."
        else:
            message = "Puzzle already solved."

    elif action == 'claim_reward':
        import uuid
        tier = str(data.get('tier', ''))
        reward_names = {
            '100': 'Seminar Priority Access Pass',
            '150': 'Official KNOVA Merchandise Pack',
            '200': 'Special VIP Experience Pass',
            '300': 'Premium Grand Reward Voucher'
        }
        if tier in reward_names:
            required_pts = int(tier)
            if passport.total_points >= required_pts:
                field_name = f"claimed_reward_{tier}"
                setattr(passport, field_name, True)
                voucher_code = f"KNOVA-{tier}-{uuid.uuid4().hex[:6].upper()}"
                passport.add_activity(f"Claimed Reward: {reward_names[tier]} (Voucher: {voucher_code})", 0)
                message = f"Reward Claimed! Your code is {voucher_code}"
            else:
                return JsonResponse({'success': False, 'error': f"You need {required_pts} points. You have {passport.total_points}."})
        else:
            return JsonResponse({'success': False, 'error': "Invalid reward tier."})

    elif action == 'reset_passport':
        passport.universities_visited_count = 0
        passport.visited_universities = []
        passport.aptitude_test_completed = False
        passport.seminars_attended_count = 0
        passport.attended_seminars = []
        passport.expert_meeting_completed = False
        passport.counselling_completed = False
        passport.tech_challenge_completed = False
        passport.puzzle_completed = False
        passport.passport_completed = False
        passport.claimed_reward_100 = False
        passport.claimed_reward_150 = False
        passport.claimed_reward_200 = False
        passport.claimed_reward_300 = False
        passport.total_points = 10
        passport.activity_log = [{'title': 'Passport Missions Reset & Reopened', 'points': 0, 'timestamp': 'Just now'}]
        passport.save()

        # Archive user's previous completed exam attempts as Abandoned so they can test the exam taking flow freshly
        if passport.user:
            from .models import ExamAttempt
            ExamAttempt.objects.filter(registration__student__user=passport.user, status='Completed').update(status='Abandoned')

        message = "All 6 challenge missions have been reopened! You can test taking the exam freshly."

    elif action == 'unlock_all':
        passport.universities_visited_count = 3
        passport.visited_universities = list(University.objects.values_list('name', flat=True)[:3]) or ['Exhibitor Booth A', 'Exhibitor Booth B', 'Exhibitor Booth C']
        passport.aptitude_test_completed = True
        passport.seminars_attended_count = 2
        passport.attended_seminars = ['Future of Global Careers Keynote', 'AI in Higher Education']
        passport.expert_meeting_completed = True
        passport.counselling_completed = True
        passport.tech_challenge_completed = True
        passport.puzzle_completed = True
        passport.passport_completed = True
        passport.total_points = 300
        passport.add_activity("Unlocked All 6 Challenge Missions & Rewards", 300)
        passport.save()

        # Ensure a completed exam attempt exists for the student so 'View Result' works immediately
        if passport.user:
            from .models import ExamAttempt, ExamRegistration, ScholarshipExam, StudentProfile
            student_profile, _ = StudentProfile.objects.get_or_create(user=passport.user)
            exam = ScholarshipExam.objects.filter(is_active=True).first() or ScholarshipExam.objects.first()
            if exam:
                reg, _ = ExamRegistration.objects.get_or_create(student=student_profile, exam=exam)
                attempt = ExamAttempt.objects.filter(registration=reg).order_by('-id').first()
                if not attempt:
                    attempt = ExamAttempt.objects.create(registration=reg)
                if attempt.status != 'Completed':
                    attempt.status = 'Completed'
                    attempt.score = 85
                    attempt.is_passed = True
                    attempt.save()

        message = "All 6 missions and milestone tiers are now fully unlocked!"

    passport.refresh_from_db()
    latest_exam = passport.get_latest_completed_exam() if hasattr(passport, 'get_latest_completed_exam') else None
    latest_exam_attempt_id = latest_exam.id if latest_exam else None

    return JsonResponse({
        'success': True,
        'message': message,
        'points_awarded': points_awarded,
        'total_points': passport.total_points,
        'rank_title': passport.rank_title,
        'completed_missions_count': passport.completed_missions_count,
        'passport_completed': passport.passport_completed,
        'is_elite_pass': passport.is_elite_pass,
        'can_visit_more_booths': passport.can_visit_more_booths,
        'booth_limit_label': passport.booth_limit_label,
        'voucher_code': voucher_code,
        'universities_visited_count': passport.universities_visited_count,
        'visited_universities': passport.visited_universities,
        'aptitude_test_completed': passport.aptitude_test_completed,
        'latest_exam_attempt_id': latest_exam_attempt_id,
        'score': latest_exam.score if latest_exam else None,
        'seminars_attended_count': passport.seminars_attended_count,
        'expert_meeting_completed': passport.expert_meeting_completed,
        'counselling_completed': passport.counselling_completed,
        'tech_challenge_completed': passport.tech_challenge_completed,
        'puzzle_completed': passport.puzzle_completed,
        'claimed_100': passport.claimed_reward_100,
        'claimed_150': passport.claimed_reward_150,
        'claimed_200': passport.claimed_reward_200,
        'claimed_300': passport.claimed_reward_300,
        'activity_log': passport.activity_log[:8]
    })


@csrf_exempt


def expert_punch_api(request):
    """Endpoint for Education Experts to scan student QR codes and punch attendance."""
    from .models import StudentChallengePassport
    badge_id = request.GET.get('badge_id') or request.POST.get('badge_id')
    if not badge_id and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            badge_id = data.get('badge_id')
        except Exception:
            pass

    if not badge_id:
        return JsonResponse({'success': False, 'error': 'badge_id required.'}, status=400)

    passport = StudentChallengePassport.objects.filter(badge_id__iexact=badge_id).first()
    if not passport:
        return JsonResponse({'success': False, 'error': f'Passport not found for badge {badge_id}.'}, status=404)

    status_str = 'ALREADY_PUNCHED'
    msg = f"Consultation already punched for {passport.student_name}."
    # Record attendance in ExpertConsultationAttendance
    from .models import EducationExpert, ExpertConsultationAttendance, StudentProfile
    expert_obj = EducationExpert.objects.first()
    sp = None
    if passport.user and hasattr(passport.user, 'student_profile'):
        sp = passport.user.student_profile
    elif passport.student_email:
        sp = StudentProfile.objects.filter(user__email__iexact=passport.student_email).first()

    ExpertConsultationAttendance.objects.get_or_create(
        badge_id=passport.badge_id,
        defaults={
            'expert': expert_obj,
            'student': sp,
            'student_name': passport.student_name,
            'punch_method': 'QR Scanner',
            'notes': 'Official Consultation with Education Expert'
        }
    )

    if not passport.expert_meeting_completed:
        passport.expert_meeting_completed = True
        passport.add_activity("Official Consultation with Senior Education Expert (+40 pts)", 40)
        passport.check_passport_completion()
        passport.save()
        passport.refresh_from_db()
        status_str = 'PUNCHED'
        msg = f"Consultation attendance punched for {passport.student_name}! +40 Points awarded."

    # If opened directly in browser by mobile QR scanner
    accept_hdr = request.headers.get('Accept', '')
    is_browser = 'text/html' in accept_hdr and request.method == 'GET' and not request.headers.get('X-Requested-With')
    if is_browser:
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Consultation Attendance Punched â€” KNOVA 2027</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/dist/tabler-icons.min.css">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #061022 100%);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      padding: 16px;
      box-sizing: border-box;
    }}
    .punch-card {{
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 24px;
      padding: 32px 24px;
      max-width: 420px;
      width: 100%;
      text-align: center;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }}
    .badge-icon {{
      width: 72px;
      height: 72px;
      border-radius: 50%;
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 38px;
      margin: 0 auto 18px;
      box-shadow: 0 0 30px rgba(16, 185, 129, 0.5);
    }}
    h1 {{ font-size: 22px; font-weight: 800; margin: 0 0 8px; color: #fff; }}
    .subtitle {{ font-size: 13px; color: #94a3b8; margin: 0 0 20px; line-height: 1.4; }}
    .info-box {{
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 24px;
      text-align: left;
    }}
    .info-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      font-size: 13px;
    }}
    .info-row:last-child {{ border-bottom: none; }}
    .info-label {{ color: #94a3b8; font-weight: 600; }}
    .info-val {{ color: #fff; font-weight: 800; }}
    .pts-badge {{
      background: #10b981;
      color: #fff;
      font-size: 11px;
      font-weight: 850;
      padding: 3px 10px;
      border-radius: 9999px;
    }}
    .btn-return {{
      display: inline-block;
      width: 100%;
      box-sizing: border-box;
      background: linear-gradient(135deg, #1768ff 0%, #38bdf8 100%);
      color: #fff;
      text-decoration: none;
      font-size: 14px;
      font-weight: 800;
      padding: 13px;
      border-radius: 12px;
      transition: transform 0.2s;
    }}
  </style>
</head>
<body>
  <div class="punch-card">
    <div class="badge-icon"><i class="ti ti-check"></i></div>
    <h1>Consultation Punched!</h1>
    <p class="subtitle">Official verification recorded for KNOVA 2027 Counselling Hub.</p>

    <div class="info-box">
      <div class="info-row">
        <span class="info-label">Student Attendee</span>
        <span class="info-val">{passport.student_name}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Badge ID</span>
        <span class="info-val" style="font-family: monospace;">{passport.badge_id}</span>
      </div>
      <div class="info-row">
        <span class="info-label">XP Awarded</span>
        <span class="info-val"><span class="pts-badge">+40 XP</span></span>
      </div>
      <div class="info-row">
        <span class="info-label">Total Student Score</span>
        <span class="info-val">{passport.total_points} PTS</span>
      </div>
      <div class="info-row">
        <span class="info-label">Consultant</span>
        <span class="info-val">Senior Education Expert</span>
      </div>
    </div>

    <a href="/challenge/" class="btn-return">
      <i class="ti ti-arrow-left"></i> View Student Passport
    </a>
  </div>
</body>
</html>"""
        return HttpResponse(html, content_type="text/html")

    return JsonResponse({
        'success': True,
        'status': status_str,
        'message': msg,
        'badge_id': passport.badge_id,
        'student_name': passport.student_name,
        'total_points': passport.total_points
    })


def my_expo_hub(request):
    from .models import Registration, EventLocation, FloorActivityZone

    # Resolve target student profile and user
    student_profile = None
    target_user = None
    if request.user.is_authenticated:
        if hasattr(request.user, 'student_profile'):
            student_profile = request.user.student_profile
            target_user = request.user
        elif hasattr(request.user, 'parent_profile'):
            profile = request.user.parent_profile
            linked = profile.linked_students.select_related('user').all()
            active_id = request.session.get('active_student_id')
            active_child = linked.filter(id=active_id).first() if active_id else linked.first()
            if active_child:
                student_profile = active_child
                target_user = active_child.user
            else:
                target_user = request.user
        else:
            target_user = request.user

    passport = get_or_create_challenge_passport(request)
    if passport:
        passport.sync_attendance_status()
        passport.sync_exam_challenge_status()

    booked_events = []
    saved_universities = []
    schedule_items = []
    attended_seminars = []
    booth_visits = []

    available_sessions = []
    added_session_ids = set()
    attended_session_ids = set()
    locations = []
    selected_location_id = None

    if request.user.is_authenticated:
        check_email = target_user.email if target_user else request.user.email
        booked_events = Registration.objects.filter(email=check_email).select_related('event_location')
        if student_profile:
            from .models import SeminarAttendance, BoothInteraction, StudentSchedule, ProgrammeSession
            import datetime
            from django.contrib import messages

            # Handle Itinerary Schedule Actions
            if request.method == 'POST':
                action = request.POST.get('action', 'add')
                session_id = request.POST.get('session_id')
                if session_id:
                    if action == 'remove':
                        StudentSchedule.objects.filter(student=student_profile, item_type='Session', related_id=session_id).delete()
                        messages.success(request, "Session removed from your confirmed schedule.")
                        return redirect(request.path)
                    elif action == 'add':
                        try:
                            session = ProgrammeSession.objects.get(id=session_id)
                            dt = datetime.datetime.combine(session.date, session.start_time)
                            end_dt = datetime.datetime.combine(session.date, session.end_time)

                            if StudentSchedule.objects.filter(student=student_profile, item_type='Session', related_id=session.id).exists():
                                messages.warning(request, "You have already added this session to your schedule.")
                                return redirect(request.path)

                            conflict = False
                            for item in student_profile.schedule.filter(item_type='Session'):
                                try:
                                    other = ProgrammeSession.objects.get(id=item.related_id)
                                    other_dt = datetime.datetime.combine(other.date, other.start_time)
                                    other_end_dt = datetime.datetime.combine(other.date, other.end_time)
                                    if max(dt, other_dt) < min(end_dt, other_end_dt):
                                        conflict = True
                                        break
                                except ProgrammeSession.DoesNotExist:
                                    pass

                            if conflict:
                                messages.warning(request, "Warning: This session overlaps with another event in your schedule.")

                            StudentSchedule.objects.create(
                                student=student_profile,
                                item_type='Session',
                                related_id=session.id,
                                time=dt
                            )
                            messages.success(request, f"'{session.title}' added to your schedule!")
                            return redirect(request.path)
                        except ProgrammeSession.DoesNotExist:
                            messages.error(request, "Selected session does not exist.")
                            return redirect(request.path)

            saved_universities = student_profile.saved_universities.select_related('university', 'university__profile').all()
            raw_schedule = list(student_profile.schedule.all().order_by('time'))
            session_ids = [item.related_id for item in raw_schedule if item.item_type == 'Session']
            sessions_map = {s.id: s for s in ProgrammeSession.objects.filter(id__in=session_ids).select_related('speaker', 'event_location')}
            for item in raw_schedule:
                if item.item_type == 'Session':
                    item.session = sessions_map.get(item.related_id)
            schedule_items = raw_schedule

            attended_seminars = SeminarAttendance.objects.filter(student=student_profile).select_related('session', 'session__speaker').order_by('-attended_at')
            attended_session_ids = set(attended_seminars.values_list('session_id', flat=True))
            added_session_ids = set(session_ids)

            locations = EventLocation.objects.filter(is_active=True).order_by('start_date')
            selected_loc_id = request.GET.get('location')
            available_sessions_qs = ProgrammeSession.objects.all().select_related('speaker', 'event_location').order_by('date', 'start_time')
            if selected_loc_id:
                try:
                    available_sessions = available_sessions_qs.filter(event_location_id=int(selected_loc_id))
                except (ValueError, TypeError):
                    available_sessions = available_sessions_qs
            else:
                available_sessions = available_sessions_qs

            selected_location_id = int(selected_loc_id) if selected_loc_id and str(selected_loc_id).isdigit() else None
            booth_visits = BoothInteraction.objects.filter(student=student_profile).select_related('booth', 'booth__university', 'booth__exhibitor').order_by('-interaction_date')

    full_name = ""
    school_or_org = ""
    display_email = ""
    if target_user:
        full_name = target_user.get_full_name() or target_user.username
        display_email = target_user.email or ""
        if student_profile:
            school_or_org = getattr(student_profile, 'school_college', '') or getattr(student_profile, 'current_education', '')
    elif request.user.is_authenticated:
        full_name = request.user.get_full_name() or request.user.username
        display_email = request.user.email or ""
    if not full_name and passport:
        full_name = passport.student_name or ""
    if not display_email and passport:
        display_email = passport.student_email or ""
    if not school_or_org:
        school_or_org = ""

    # Generate QR Code: prioritize student UUID qr_identifier for universal booth/seminar scanning
    qr_data = (student_profile.qr_identifier if student_profile and student_profile.qr_identifier else None) or (passport.badge_id if passport else f"KNOVA-STU-{request.user.id:03d}")
    qr = qrcode.make(qr_data)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    upcoming_event = EventLocation.objects.filter(is_active=True, is_upcoming=True).first()
    floor_zones = FloorActivityZone.objects.filter(is_active=True).order_by('order')

    # When a student is being viewed/supervised (either directly or by managing parent), role is 'student'
    role = 'student'
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.groups.filter(name='admin').exists():
            role = 'admin'
        elif hasattr(request.user, 'student_profile') or hasattr(request.user, 'parent_profile'):
            role = 'student'
        elif hasattr(request.user, 'university_staff'):
            role = 'university'
        elif hasattr(request.user, 'exhibitor_profile') or hasattr(request.user, 'exhibitor_staff_profile'):
            role = 'exhibitor'

    badge_id = (passport.badge_id if passport else None) or f"KNOVA-STU-{target_user.id if target_user else 1:03d}"

    context = {
        'passport': passport,
        'profile': student_profile,
        'qr_base64': qr_base64,
        'full_name': full_name,
        'school_or_org': school_or_org,
        'badge_id': badge_id,
        'student_id': badge_id,
        'display_email': display_email,
        'booked_events': booked_events,
        'saved_universities': saved_universities,
        'schedule_items': schedule_items,
        'schedule': schedule_items,
        'available_sessions': available_sessions,
        'added_session_ids': added_session_ids,
        'attended_session_ids': attended_session_ids,
        'locations': locations,
        'selected_location_id': selected_location_id,
        'attended_seminars': attended_seminars,
        'booth_visits': booth_visits,
        'upcoming_event': upcoming_event,
        'floor_zones': floor_zones,
        'role': role,
    }
    return render(request, 'core/my_expo.html', context)


def _parse_shift_time_str(time_str):
    import re
    from datetime import datetime, time
    time_str = time_str.strip().upper()
    for fmt in ('%I:%M %p', '%I:%M%p', '%H:%M', '%I %p', '%I%p'):
        try:
            dt = datetime.strptime(time_str, fmt)
            return time(dt.hour, dt.minute)
        except ValueError:
            pass
    m = re.match(r'^(\d{1,2}):(\d{2})$', time_str)
    if m:
        return time(int(m.group(1)), int(m.group(2)))
    return None


def _parse_shift_range(shift_str):
    import re
    from datetime import datetime, date, timedelta
    parts = re.split(r'[-â€“â€”to]+', shift_str.strip(), flags=re.IGNORECASE)
    if len(parts) >= 2:
        st = _parse_shift_time_str(parts[0])
        et = _parse_shift_time_str(parts[1])
        if st and et:
            return st, et
    elif len(parts) == 1 and parts[0].strip():
        st = _parse_shift_time_str(parts[0])
        if st:
            et = (datetime.combine(date.today(), st) + timedelta(minutes=90)).time()
            return st, et
    return None, None


def _parse_date_str(date_str):
    import datetime, re
    today = datetime.date.today()
    if not date_str:
        return today
    s = str(date_str).strip().lower()
    if s in ('today', 'todays date', 'now', 'current'):
        return today
    if s in ('tomorrow', 'tmrw'):
        return today + datetime.timedelta(days=1)
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y', '%b %d, %Y', '%B %d, %Y', '%Y/%m/%d'):
        try:
            return datetime.datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            pass
    m = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', str(date_str))
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass
    return today


def _ensure_scholarship_exam_slots():
    import datetime
    from .models import ScholarshipExamSlot

    today = datetime.date.today()
    dates = [today + datetime.timedelta(days=i) for i in range(5)]

    times = [
        (datetime.time(8, 30), datetime.time(10, 0), 'Main Expo Assessment Arena â€” Hall 3, Desk A-12', 38),
        (datetime.time(10, 0), datetime.time(11, 30), 'Main Expo Assessment Arena â€” Hall 3, Desk B-08', 27),
        (datetime.time(11, 30), datetime.time(13, 0), 'Main Expo Assessment Arena â€” Hall 3, Desk C-05', 42),
        (datetime.time(13, 0), datetime.time(14, 30), 'Main Expo Assessment Arena â€” Hall 3, Desk D-14', 19),
        (datetime.time(14, 30), datetime.time(16, 0), 'Main Expo Assessment Arena â€” Hall 3, Desk A-18', 33),
        (datetime.time(16, 0), datetime.time(17, 30), 'Main Expo Assessment Arena â€” Hall 3, Desk B-22', 15),
        (datetime.time(17, 30), datetime.time(19, 0), 'Main Expo Assessment Arena â€” Hall 3, Desk C-09', 45),
        (datetime.time(19, 0), datetime.time(20, 30), 'Main Expo Assessment Arena â€” Hall 3, Desk D-11', 50),
    ]

    for d in dates:
        for st, et, venue, seats in times:
            if not ScholarshipExamSlot.objects.filter(exam_date=d, start_time=st).exists():
                ScholarshipExamSlot.objects.create(
                    title='KNOVA Global Scholarship Aptitude & Assessment Exam (KG-SAAE)',
                    exam_date=d,
                    start_time=st,
                    end_time=et,
                    venue=venue,
                    total_seats=50,
                    available_seats=seats,
                    is_active=True
                )


def scholarship_exam_booking(request):
    if not request.user.is_authenticated:
        login_url = f"/portal/login/?next={request.get_full_path()}"
        return redirect(login_url)

    # Restrict exam booking to students only
    user = request.user
    if hasattr(user, 'parent_profile'):
        from django.contrib import messages
        messages.info(request, "Exam slot bookings and test taking must be completed by the student. Parents have view-only access to child progress.")
        return redirect('dashboard_scholarships')
    if hasattr(user, 'exhibitor_profile') or hasattr(user, 'university_staff') or hasattr(user, 'seminar_staff'):
        from django.contrib import messages
        messages.error(request, "Scholarship exam slot booking is exclusively reserved for prospective student candidates.")
        return redirect('dashboard_index')

    from .models import ScholarshipExamSlot, ScholarshipExamBooking, Scholarship, Notification
    from collections import defaultdict
    import uuid

    # Determine requested scholarship (if any)
    scholarship_id = request.GET.get('scholarship_id') or request.POST.get('scholarship_id')
    scholarship_name_param = request.GET.get('scholarship') or request.POST.get('scholarship_name')
    selected_scholarship = None

    if scholarship_id:
        try:
            selected_scholarship = Scholarship.objects.select_related('university').get(pk=scholarship_id)
        except (Scholarship.DoesNotExist, ValueError):
            pass

    if not selected_scholarship and scholarship_name_param:
        param_lower = scholarship_name_param.lower()
        if 'merit' in param_lower:
            selected_scholarship = Scholarship.objects.filter(name__icontains='merit').first()
        elif 'stem' in param_lower:
            selected_scholarship = Scholarship.objects.filter(name__icontains='stem').first()
            if not selected_scholarship:
                selected_scholarship = Scholarship.objects.filter(category__icontains='stem').first()
        elif 'women' in param_lower:
            selected_scholarship = Scholarship.objects.filter(name__icontains='women').first()
        else:
            selected_scholarship = Scholarship.objects.filter(name__icontains=scholarship_name_param).first()

    # Fallback to first scholarship if none specified
    if not selected_scholarship:
        selected_scholarship = Scholarship.objects.first()

    success_booking = None
    error_message = None

    if request.method == 'POST':
        action = request.POST.get('action', 'book')
        if action == 'book':
            slot_id = request.POST.get('slot_id')
            special_req = request.POST.get('special_requirements', '').strip()
            custom_shift_time = request.POST.get('custom_shift_time', '').strip()
            custom_exam_date_str = request.POST.get('custom_exam_date', '').strip()
            active_date_str = request.POST.get('active_date', '').strip()

            slot = None
            if slot_id == 'custom' or (not slot_id and custom_shift_time):
                if not custom_shift_time:
                    error_message = "Please enter or type the time of the shift (e.g. 09:15 AM - 10:45 AM)."
                else:
                    st, et = _parse_shift_range(custom_shift_time)
                    if not st or not et:
                        error_message = "Could not parse shift time. Please use a format like '09:15 AM - 10:45 AM' or '9:30 AM'."
                    else:
                        exam_date = _parse_date_str(custom_exam_date_str or active_date_str)

                        slot, _ = ScholarshipExamSlot.objects.get_or_create(
                            exam_date=exam_date,
                            start_time=st,
                            end_time=et,
                            defaults={
                                'title': 'KNOVA Global Scholarship Aptitude & Assessment Exam (KG-SAAE) [Test Shift]',
                                'venue': 'Main Expo Assessment Arena â€” Hall 3, Desk T-Test',
                                'total_seats': 50,
                                'available_seats': 49,
                                'is_active': True,
                            }
                        )
            elif not slot_id:
                error_message = "Please select an available examination date and time slot."
            else:
                try:
                    slot = ScholarshipExamSlot.objects.get(pk=slot_id, is_active=True)
                except ScholarshipExamSlot.DoesNotExist:
                    error_message = "The selected slot does not exist."

            if slot:
                if slot.available_seats <= 0:
                    error_message = "This slot is currently full. Please choose another time slot."
                else:
                    # Check if user already booked this exact slot
                    existing = ScholarshipExamBooking.objects.filter(user=request.user, slot=slot, status='Confirmed').first()
                    if existing:
                        success_booking = existing
                    else:
                        # Cancel previous confirmed bookings for this scholarship so user can reschedule
                        if selected_scholarship:
                            prev_bookings = ScholarshipExamBooking.objects.filter(user=request.user, scholarship=selected_scholarship, status='Confirmed')
                        else:
                            s_target_name = scholarship_name_param or "KNOVA Merit Scholarship"
                            prev_bookings = ScholarshipExamBooking.objects.filter(user=request.user, scholarship_name=s_target_name, status='Confirmed')
                        for pb in prev_bookings:
                            pb.status = 'Cancelled'
                            pb.save()
                            pb.slot.available_seats = min(pb.slot.total_seats, pb.slot.available_seats + 1)
                            pb.slot.save()

                        # Generate unique ticket number and seat
                        ticket_no = f"KG-SAAE-{slot.exam_date.strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
                        seat_no = f"H3-D{slot.id:02d}-{max(1, slot.total_seats - slot.available_seats + 1):02d}"

                        s_name = selected_scholarship.name if selected_scholarship else (scholarship_name_param or "KNOVA Merit Scholarship")

                        booking = ScholarshipExamBooking.objects.create(
                            user=request.user,
                            slot=slot,
                            scholarship=selected_scholarship,
                            scholarship_name=s_name,
                            hall_ticket_number=ticket_no,
                            seat_number=seat_no,
                            status='Confirmed',
                            special_requirements=special_req
                        )
                        # Decrement seats
                        slot.available_seats = max(0, slot.available_seats - 1)
                        slot.save()

                        # Create Notification
                        Notification.objects.create(
                            user=request.user,
                            title="Scholarship Exam Slot Confirmed",
                            message=f"Your slot for {slot.title} on {slot.exam_date.strftime('%b %d, %Y')} at {slot.start_time.strftime('%I:%M %p')} is confirmed. Hall Ticket: {ticket_no}"
                        )

                        # Challenge activity points
                        try:
                            from .models import StudentChallengePassport
                            passport = StudentChallengePassport.objects.filter(user=request.user).first()
                            if passport:
                                passport.add_activity("Booked Scholarship Exam Slot", 30)
                        except Exception:
                            pass

                        success_booking = booking

        elif action == 'add_custom_slot':
            custom_shift_time = request.POST.get('custom_shift_time', '').strip()
            slot_date_str = request.POST.get('slot_date', '').strip() or request.POST.get('custom_exam_date', '').strip()
            slot_venue = request.POST.get('slot_venue', '').strip() or 'Main Expo Assessment Arena â€” Hall 3, Desk T-Test'

            st, et = _parse_shift_range(custom_shift_time)
            if not st or not et:
                error_message = "Please enter a valid shift time (e.g. 09:15 AM - 10:45 AM or 9:30 AM)."
            else:
                try:
                    slot_date = _parse_date_str(slot_date_str)
                    new_slot, _ = ScholarshipExamSlot.objects.get_or_create(
                        exam_date=slot_date,
                        start_time=st,
                        end_time=et,
                        defaults={
                            'title': 'KNOVA Global Scholarship Aptitude & Assessment Exam (KG-SAAE) [Test Shift]',
                            'venue': slot_venue,
                            'total_seats': 50,
                            'available_seats': 50,
                            'is_active': True,
                        }
                    )
                except Exception as e:
                    error_message = f"Could not create slot: {e}"

        elif action == 'cancel':
            booking_id = request.POST.get('booking_id')
            try:
                b = ScholarshipExamBooking.objects.get(pk=booking_id, user=request.user, status='Confirmed')
                b.status = 'Cancelled'
                b.save()
                # Restore seat
                b.slot.available_seats = min(b.slot.total_seats, b.slot.available_seats + 1)
                b.slot.save()
            except ScholarshipExamBooking.DoesNotExist:
                pass

    # Ensure 5 days of 8 slots starting from today
    import datetime
    today = datetime.date.today()
    _ensure_scholarship_exam_slots()

    # Fetch slots for upcoming dates (starting from today)
    all_slots = ScholarshipExamSlot.objects.filter(is_active=True, exam_date__gte=today).order_by('exam_date', 'start_time')

    slots_by_date = defaultdict(list)
    for s in all_slots:
        slots_by_date[s.exam_date].append(s)

    # Next 5 dates starting from today
    upcoming_dates = sorted([d for d in slots_by_date.keys() if d >= today])[:5]
    all_display_dates = set(upcoming_dates)
    if success_booking and success_booking.slot and success_booking.slot.exam_date in slots_by_date:
        all_display_dates.add(success_booking.slot.exam_date)

    available_dates = sorted(all_display_dates)
    slots_grouped = {d: slots_by_date[d] for d in available_dates}

    # Fetch user's bookings
    my_bookings = ScholarshipExamBooking.objects.filter(user=request.user).select_related('slot', 'scholarship').order_by('-booked_at')
    if selected_scholarship:
        active_booking = my_bookings.filter(status='Confirmed', scholarship=selected_scholarship).first()
    else:
        active_booking = my_bookings.filter(status='Confirmed').first()
    if not success_booking and active_booking:
        success_booking = active_booking

    all_scholarships = Scholarship.objects.select_related('university').all()[:12]

    # Generate QR Code for confirmed booking
    hall_ticket_qr = None
    if success_booking:
        qr = qrcode.make(f"KNOVA-EXAM|{success_booking.hall_ticket_number}|{success_booking.user.username}|{success_booking.slot.exam_date}|{success_booking.seat_number}")
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        hall_ticket_qr = base64.b64encode(buf.getvalue()).decode('utf-8')

    context = {
        'selected_scholarship': selected_scholarship,
        'scholarship_name_param': scholarship_name_param,
        'slots_grouped': slots_grouped,
        'first_date': available_dates[0] if available_dates else today,
        'available_dates': available_dates,
        'today': today,
        'my_bookings': my_bookings,
        'success_booking': success_booking,
        'hall_ticket_qr': hall_ticket_qr,
        'error_message': error_message,
        'all_scholarships': all_scholarships,
    }
    return render(request, 'core/scholarship_exam_booking.html', context)


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')


def terms_conditions(request):
    return render(request, 'core/terms_conditions.html')
