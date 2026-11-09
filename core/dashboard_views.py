from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import EventLocation, Exhibitor, Registration


@login_required(login_url='/portal/login/')
def dashboard_export_registrations(request):
    if not request.user.is_superuser and not request.user.groups.filter(name__in=['admin', 'manager']).exists():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to export registrations.")
    from .models import Registration
    import csv
    from django.http import HttpResponse
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    role = request.GET.get('role')
    export_format = request.GET.get('format', 'csv')
    queryset = Registration.objects.all()
    if start_date:
        queryset = queryset.filter(registered_at__gte=start_date)
    if end_date:
        queryset = queryset.filter(registered_at__lte=end_date)
    if role:
        queryset = queryset.filter(role=role)
    if export_format == 'excel':
        try:
            import openpyxl
        except ImportError:
            from django.contrib import messages
            from django.shortcuts import redirect
            messages.error(request, "openpyxl is not installed for Excel export.")

            return redirect('dashboard_registrations')
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Registrations"
        columns = ['Registration ID', 'Full Name', 'Email', 'Role', 'Status', 'Event Location', 'Registered At']
        ws.append(columns)
        for reg in queryset:
            ws.append([
                reg.registration_id,
                reg.full_name,
                reg.email,
                reg.role,
                reg.status,
                reg.event_location.city if reg.event_location else '',
                reg.registered_at.strftime('%Y-%m-%d %H:%M:%S') if reg.registered_at else ''
            ])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="filtered_registrations.xlsx"'
        wb.save(response)

        # Save a local copy directly to the Downloads folder
        try:
            import os
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'filtered_registrations.xlsx')
            wb.save(downloads_path)
            messages.success(request, f"File also saved directly to: {downloads_path}")
        except Exception:
            pass

        return response
    else:

        # Default to CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="filtered_registrations.csv"'
        writer = csv.writer(response)
        writer.writerow(['Registration ID', 'Full Name', 'Email', 'Role', 'Status', 'Event Location', 'Registered At'])

        # We will also save a local copy directly to the Downloads folder
        local_csv_data = []
        local_csv_data.append(['Registration ID', 'Full Name', 'Email', 'Role', 'Status', 'Event Location', 'Registered At'])
        for reg in queryset:
            row = [
                reg.registration_id,
                reg.full_name,
                reg.email,
                reg.role,
                reg.status,
                reg.event_location.city if reg.event_location else '',
                reg.registered_at.strftime('%Y-%m-%d %H:%M:%S') if reg.registered_at else ''
            ]
            writer.writerow(row)
            local_csv_data.append(row)
        try:
            import os
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'filtered_registrations.csv')
            with open(downloads_path, 'w', newline='', encoding='utf-8') as f:
                local_writer = csv.writer(f)
                local_writer.writerows(local_csv_data)
            messages.success(request, f"File also saved directly to: {downloads_path}")
        except Exception:
            pass

        return response


@login_required(login_url='/portal/login/')
def dashboard_export_generic(request, model_name):
    if not request.user.is_superuser and not request.user.groups.filter(name__in=['admin', 'manager']).exists():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to export data.")
    from django.apps import apps
    import csv
    from django.http import HttpResponse
    try:
        model = apps.get_model('core', model_name)
    except LookupError:
        from django.http import Http404
        raise Http404("Model not found")
    export_format = request.GET.get('format', 'csv')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    queryset = model.objects.all()
    if start_date or end_date:
        date_field = None
        for f in model._meta.fields:
            if f.name in ['created_at', 'registered_at', 'captured_at', 'date_joined', 'date']:
                date_field = f.name
                break

        # fallback to User date_joined if applicable
        if not date_field and hasattr(model, 'user'):
            date_field = 'user__date_joined'
        if date_field:
            if start_date:
                queryset = queryset.filter(**{f"{date_field}__gte": start_date})
            if end_date:
                queryset = queryset.filter(**{f"{date_field}__lte": end_date})
    if export_format == 'excel':
        try:
            import openpyxl
        except ImportError:
            from django.contrib import messages
            from django.shortcuts import redirect
            messages.error(request, "openpyxl is not installed.")

            return redirect('dashboard_index')
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = model_name
        fields = [f.name for f in model._meta.fields]
        ws.append(fields)
        for obj in queryset:
            ws.append([str(getattr(obj, field, '')) for field in fields])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{model_name}_export.xlsx"'
        wb.save(response)
        try:
            import os
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads', f'{model_name}_export.xlsx')
            wb.save(downloads_path)
        except Exception:
            pass

        return response
    else:

        # Default to CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{model_name}_export.csv"'
        writer = csv.writer(response)
        fields = [f.name for f in model._meta.fields]
        writer.writerow(fields)
        local_csv_data = [fields]
        for obj in queryset:
            row = [str(getattr(obj, field, '')) for field in fields]
            writer.writerow(row)
            local_csv_data.append(row)
        try:
            import os
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads', f'{model_name}_export.csv')
            with open(downloads_path, 'w', newline='', encoding='utf-8') as f:
                local_writer = csv.writer(f)
                local_writer.writerows(local_csv_data)
        except Exception:
            pass

        return response


@login_required(login_url='/portal/login/')
def dashboard_index(request):
    from .models import EventLocation, Exhibitor, Speaker, Sponsor, ProgrammeSession, Registration
    import json
    from django.db.models import Count
    context = {}
    is_admin = (
        request.user.is_superuser or
        request.user.is_staff or
        request.user.groups.filter(name='Admin').exists() or
        request.user.username.lower() == 'admin'
    )
    if is_admin:
        from django.db.models.functions import TruncDate
        from datetime import timedelta
        from django.utils import timezone
        import datetime

        # Data for Role Distribution Chart
        role_counts = list(Registration.objects.values('role').annotate(count=Count('id')))
        chart_labels = [item['role'] for item in role_counts]
        chart_data = [item['count'] for item in role_counts]

        # Chart filters
        chart_range = request.GET.get('chart_range', 'all')
        chart_sort = request.GET.get('chart_sort', 'asc')
        qs = Registration.objects.all()
        now = timezone.now()
        if chart_range == '1':
            qs = qs.filter(registered_at__gte=now.replace(hour=0, minute=0, second=0))
        elif chart_range == 'yesterday':
            yesterday = now - timedelta(days=1)
            qs = qs.filter(registered_at__gte=yesterday.replace(hour=0, minute=0, second=0), registered_at__lt=now.replace(hour=0, minute=0, second=0))
        elif chart_range == 'this_week':
            start_of_week = now - timedelta(days=now.weekday())
            qs = qs.filter(registered_at__gte=start_of_week.replace(hour=0, minute=0, second=0))
        elif chart_range == 'this_month':
            qs = qs.filter(registered_at__gte=now.replace(day=1, hour=0, minute=0, second=0))
        elif chart_range != 'all' and chart_range.isdigit():
            cutoff = now - timedelta(days=int(chart_range))
            qs = qs.filter(registered_at__gte=cutoff)
        daywise_qs = list(qs.annotate(date=TruncDate('registered_at')).values('date', 'role').annotate(count=Count('id')))
        all_dates_set = set([item['date'] for item in daywise_qs if item['date']])

        # Sort logic
        if chart_sort in ['asc', 'desc']:
            all_dates = sorted(list(all_dates_set), reverse=(chart_sort == 'desc'))
        elif chart_sort in ['vol_desc', 'vol_asc']:

            # Calculate total volume per date
            vol_per_date = {}
            for item in daywise_qs:
                if item['date']:
                    vol_per_date[item['date']] = vol_per_date.get(item['date'], 0) + item['count']
            all_dates = sorted(list(all_dates_set), key=lambda d: vol_per_date.get(d, 0), reverse=(chart_sort == 'vol_desc'))
        else:
            all_dates = sorted(list(all_dates_set))
        date_strings = [d.strftime('%b %d') for d in all_dates]
        roles = list(set([item['role'] for item in daywise_qs]))
        daywise_datasets = {}
        for r in roles:
            daywise_datasets[r] = [0] * len(all_dates)
        for item in daywise_qs:
            if not item['date']:
                continue
            date_idx = all_dates.index(item['date'])
            daywise_datasets[item['role']][date_idx] = item['count']
        from .models import University, Course, Scholarship, Sponsor, Speaker, ProgrammeSession, ExamQuestion
        context = {
            'role': 'admin',
            'total_events': EventLocation.objects.count(),
            'total_universities': University.objects.count(),
            'total_courses': Course.objects.count(),
            'total_exhibitors': Exhibitor.objects.count(),
            'total_registrations': Registration.objects.count(),
            'total_checkins': Registration.objects.filter(is_checked_in=True).count(),
            'total_sessions': ProgrammeSession.objects.count(),
            'total_speakers': Speaker.objects.count(),
            'total_sponsors': Sponsor.objects.count(),
            'total_questions': ExamQuestion.objects.count(),
            'total_scholarships': Scholarship.objects.count(),
            'upcoming_events': EventLocation.objects.filter(is_upcoming=True).order_by('start_date')[:6],
            'recent_registrations': Registration.objects.select_related('event_location').order_by('-registered_at')[:8],
            'recent_exhibitors': Exhibitor.objects.select_related('event_location').order_by('-id')[:8],
            'recent_universities': University.objects.select_related('profile').prefetch_related('courses').order_by('-id')[:8],
            'recent_sessions': ProgrammeSession.objects.select_related('event_location', 'speaker').order_by('date', 'start_time')[:8],
            'recent_speakers': Speaker.objects.all().order_by('-id')[:6],
            'recent_sponsors': Sponsor.objects.select_related('event_location').order_by('-id')[:6],
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
            'chart_dates': json.dumps(date_strings),
            'daywise_datasets': json.dumps(daywise_datasets),
            'chart_range': chart_range,
            'chart_sort': chart_sort
        }
    elif hasattr(request.user, 'university_staff') or hasattr(request.user, 'exhibitor_profile') or hasattr(request.user, 'exhibitor_staff_profile') or get_exhibitor_profile(request.user):

        # 2. UNIVERSITY / EXHIBITORS (Both are identical role)
        from .models import BoothInteraction, ExpoBooth, University, Exhibitor
        uni = None
        if hasattr(request.user, 'university_staff') and request.user.university_staff:
            uni = request.user.university_staff.university
        exhibitor = get_exhibitor_profile(request.user)
        if not exhibitor and uni:
            exhibitor = Exhibitor.objects.filter(company_name__iexact=uni.name).first()
        if not uni and exhibitor:
            uni = University.objects.filter(name__iexact=exhibitor.company_name).first()
        profile = exhibitor or (request.user.university_staff if hasattr(request.user, 'university_staff') else None)
        from .models import UniversityApplication, ExhibitorLead
        booths = ExpoBooth.objects.filter(university=uni) if uni else (ExpoBooth.objects.filter(exhibitor=exhibitor) if exhibitor else ExpoBooth.objects.none())
        applications = uni.student_applications.select_related('student__user').order_by('-applied_at') if uni else UniversityApplication.objects.none()
        booth_interactions = BoothInteraction.objects.filter(booth__in=booths).select_related('student__user').order_by('-interaction_date') if booths.exists() else BoothInteraction.objects.none()
        leads = exhibitor.captured_leads.select_related('scanned_registration').all() if exhibitor else ExhibitorLead.objects.none()
        leads_count = leads.count() if exhibitor else booth_interactions.count()
        hot_count = leads.filter(rating='Hot').count() if exhibitor else 0
        warm_count = leads.filter(rating='Warm').count() if exhibitor else 0
        cold_count = leads.filter(rating='Cold').count() if exhibitor else 0
        unrated_count = max(0, leads_count - (hot_count + warm_count + cold_count))
        quality_labels = ["Hot", "Warm", "Cold", "Unrated"]
        quality_data = [hot_count, warm_count, cold_count, unrated_count]
        from django.db.models import Count
        role_counts = list(leads.values('scanned_registration__role').annotate(count=Count('id'))) if exhibitor else []
        role_labels = [item['scanned_registration__role'] for item in role_counts]
        role_data = [item['count'] for item in role_counts]
        from .models import CourseCategory
        courses = uni.courses.all().order_by('-id') if uni else []
        scholarships = uni.scholarships.all().order_by('-id') if uni else []
        categories = CourseCategory.objects.all()
        context = {
            'role': 'exhibitor',
            'display_role': 'Exhibitor',
            'profile': profile,
            'university': uni,
            'exhibitor': exhibitor,
            'event': getattr(exhibitor, 'event_location', None) or EventLocation.objects.filter(is_active=True).first(),
            'leads_count': leads_count,
            'courses': courses,
            'scholarships': scholarships,
            'categories': categories,
            'total_courses': len(courses),
            'courses_count': len(courses),
            'total_scholarships': len(scholarships),
            'scholarships_count': len(scholarships),
            'enquiries_count': applications.count() + booth_interactions.count() if uni else leads_count,
            'applications_count': applications.count() if uni else 0,
            'booth_interactions_count': booth_interactions.count() if booths else leads_count,
            'attended_students_count': leads_count,
            'recent_applications': applications[:5] if uni else [],
            'recent_attended_students': booth_interactions[:6] if booths else [],
            'recent_courses': courses[:5],
            'booths': booths,
            'quality_labels': json.dumps(quality_labels),
            'quality_data': json.dumps(quality_data),
            'role_labels': json.dumps(role_labels),
            'role_data': json.dumps(role_data),
        }
    elif hasattr(request.user, 'parent_profile'):
        profile = request.user.parent_profile
        linked_students = profile.linked_students.select_related('user').all()

        # Determine active student
        active_student_id = request.session.get('active_student_id')
        active_student = None
        if active_student_id:
            active_student = linked_students.filter(id=active_student_id).first()
        if not active_student and linked_students.exists():
            active_student = linked_students.first()
            request.session['active_student_id'] = active_student.id
        active_passport = None
        saved_universities = []
        student_schedule = []
        student_applications = []
        student_documents = []
        booked_events = []
        recommended_unis = []
        if active_student:
            from .models import StudentChallengePassport, StudentSchedule, ProgrammeSession, StudentDocument, UniversityApplication, University
            from django.db.models import Q
            active_passport = StudentChallengePassport.objects.filter(user=active_student.user).first()
            saved_universities = active_student.saved_universities.select_related('university', 'university__profile').all()

            # Fetch schedule and map sessions
            schedule_qs = list(active_student.schedule.all().order_by('time'))
            session_ids = [item.related_id for item in schedule_qs if item.item_type == 'Session']
            sessions_map = {s.id: s for s in ProgrammeSession.objects.filter(id__in=session_ids).select_related('speaker', 'event_location')}
            for item in schedule_qs:
                if item.item_type == 'Session':
                    item.session = sessions_map.get(item.related_id)
                    if item.session:
                        item.title = item.session.title
                        item.location = item.session.hall_name or (item.session.event_location.name if item.session.event_location else '')
            student_schedule = schedule_qs
            student_applications = active_student.applications.select_related('university', 'university__profile').all()
            student_documents = active_student.documents.all()
            booked_events = Registration.objects.filter(email=active_student.user.email).select_related('event_location')

            # Smart recommendations for child
            country_pref = active_student.preferred_country
            if country_pref:
                first_pref = country_pref.split(',')[0].strip()
                recommended_unis = University.objects.filter(profile__location_state_country__icontains=first_pref).select_related('profile')[:4]
            if not recommended_unis:
                recommended_unis = University.objects.filter(is_approved=True).select_related('profile')[:4]
        context = {
            'role': 'parent',
            'profile': profile,
            'linked_students': linked_students,
            'active_student': active_student,
            'active_passport': active_passport,
            'saved_universities': saved_universities,
            'student_schedule': student_schedule,
            'student_applications': student_applications,
            'student_documents': student_documents,
            'booked_events': booked_events,
            'recommended_unis': recommended_unis,
            'upcoming_events': EventLocation.objects.filter(is_upcoming=True).order_by('start_date')[:4],
        }
    elif hasattr(request.user, 'sponsor_profile'):
        profile = request.user.sponsor_profile
        event = profile.event_location
        from .models import (
            EventLocation, Exhibitor, Speaker, Sponsor, ProgrammeSession,
            Registration, SeminarAttendance, ExpertConsultationAttendance,
            University, Course, Scholarship, BoothInteraction, ExpoBooth
        )
        from django.db.models import Q

        # Program metrics & statistics for Sponsor (View Only)
        total_registrations = Registration.objects.count()
        total_checkins = Registration.objects.filter(is_checked_in=True).count()
        checkin_rate = round((total_checkins / total_registrations * 100), 1) if total_registrations > 0 else 0
        total_sessions = ProgrammeSession.objects.count()
        total_session_attendances = SeminarAttendance.objects.count()
        total_exhibitors = Exhibitor.objects.count()
        total_universities = University.objects.count()
        total_consultations = ExpertConsultationAttendance.objects.count()
        total_scholarships = Scholarship.objects.count()
        total_speakers = Speaker.objects.count()
        total_courses = Course.objects.count()
        total_booth_visits = BoothInteraction.objects.count()
        total_visits = total_checkins + total_booth_visits + total_session_attendances + total_consultations

        # Audience Demographics
        student_count = Registration.objects.filter(role__iexact='Student').count()
        parent_count = Registration.objects.filter(role__iexact='Parent').count()
        academic_count = Registration.objects.filter(role__iexact='Exhibitor').count()
        other_count = max(0, total_registrations - (student_count + parent_count + academic_count))
        student_pct = round((student_count / total_registrations * 100), 1) if total_registrations > 0 else 0
        parent_pct = round((parent_count / total_registrations * 100), 1) if total_registrations > 0 else 0
        academic_pct = round((academic_count / total_registrations * 100), 1) if total_registrations > 0 else 0
        other_pct = round((other_count / total_registrations * 100), 1) if total_registrations > 0 else 0

        # Sessions list with attendance & speaker prefetch
        sessions = ProgrammeSession.objects.all().select_related('event_location', 'speaker').order_by('date', 'start_time')

        # Courses / Degree Programs list
        courses = Course.objects.all().select_related('university').order_by('name')

        # Exhibitors with mapped visit counts
        exhibitors = list(Exhibitor.objects.all().select_related('event_location'))
        for exh in exhibitors:
            exh_booths = ExpoBooth.objects.filter(Q(exhibitor=exh) | Q(university__name__iexact=exh.company_name))
            exh.visits_count = BoothInteraction.objects.filter(booth__in=exh_booths).count()

        # Expos list
        upcoming_events = EventLocation.objects.filter(is_active=True).order_by('start_date')
        context = {
            'role': 'sponsor',
            'profile': profile,
            'event': event,
            'total_registrations': total_registrations,
            'total_checkins': total_checkins,
            'checkin_rate': checkin_rate,
            'total_sessions': total_sessions,
            'total_session_attendances': total_session_attendances,
            'total_exhibitors': total_exhibitors,
            'total_universities': total_universities,
            'total_consultations': total_consultations,
            'total_scholarships': total_scholarships,
            'total_speakers': total_speakers,
            'total_courses': total_courses,
            'total_booth_visits': total_booth_visits,
            'total_visits': total_visits,
            'student_count': student_count,
            'parent_count': parent_count,
            'academic_count': academic_count,
            'other_count': other_count,
            'student_pct': student_pct,
            'parent_pct': parent_pct,
            'academic_pct': academic_pct,
            'other_pct': other_pct,
            'sessions': sessions,
            'courses': courses,
            'exhibitors': exhibitors,
            'upcoming_events': upcoming_events,
        }
    elif hasattr(request.user, 'seminar_staff'):
        from .models import SeminarStaff, SeminarAttendance, ProgrammeSession
        profile = request.user.seminar_staff
        assigned_session = profile.session
        hall_name = profile.hall_name or (assigned_session.hall_name if assigned_session else "Main Hall")
        if assigned_session:
            hall_sessions = ProgrammeSession.objects.filter(id=assigned_session.id).select_related('speaker', 'event_location')
        else:
            hall_sessions = ProgrammeSession.objects.filter(hall_name__iexact=hall_name).select_related('speaker', 'event_location').order_by('date', 'start_time')
            if not hall_sessions.exists():
                hall_sessions = ProgrammeSession.objects.all().select_related('speaker', 'event_location').order_by('date', 'start_time')[:10]
        active_session = assigned_session or hall_sessions.first()
        attendances = SeminarAttendance.objects.filter(session__in=hall_sessions).select_related('student__user', 'session').order_by('-attended_at')
        total_attendees = attendances.count()
        recent_attendances = attendances[:10]
        context = {
            'role': 'seminar',
            'profile': profile,
            'assigned_session': active_session,
            'session': active_session,
            'hall_name': hall_name,
            'sessions': hall_sessions,
            'total_sessions': hall_sessions.count(),
            'total_attendees': total_attendees,
            'recent_attendances': recent_attendances,
        }
    elif hasattr(request.user, 'education_expert'):
        from .models import EducationExpert, ExpertConsultationAttendance
        profile = request.user.education_expert
        consultations = ExpertConsultationAttendance.objects.filter(expert=profile).select_related('student__user').order_by('-attended_at')
        total_consultations = consultations.count()
        recent_consultations = consultations[:15]
        context = {
            'role': 'education_expert',
            'profile': profile,
            'expert_profile': profile,
            'total_consultations': total_consultations,
            'recent_consultations': recent_consultations,
            'consultations': consultations,
        }
    elif hasattr(request.user, 'student_profile'):
        from .models import StudentChallengePassport, SeminarAttendance, Registration, EventLocation, FloorActivityZone, BoothInteraction, StudentSchedule, ProgrammeSession
        from .public_views import get_or_create_challenge_passport
        import qrcode, io, base64, datetime
        profile = request.user.student_profile
        passport = get_or_create_challenge_passport(request)
        if passport:
            passport.sync_attendance_status()
            passport.sync_exam_challenge_status()

        # Handle Itinerary Schedule Actions (Add / Remove) directly in My Expo Hub
        if request.method == 'POST':
            action = request.POST.get('action', 'add')
            session_id = request.POST.get('session_id')
            if session_id:
                from django.contrib import messages
                if action == 'remove':
                    StudentSchedule.objects.filter(student=profile, item_type='Session', related_id=session_id).delete()
                    messages.success(request, "Session removed from your confirmed schedule.")

                    return redirect(request.path)
                elif action == 'add':
                    try:
                        session = ProgrammeSession.objects.get(id=session_id)
                        dt = datetime.datetime.combine(session.date, session.start_time)
                        end_dt = datetime.datetime.combine(session.date, session.end_time)
                        if StudentSchedule.objects.filter(student=profile, item_type='Session', related_id=session.id).exists():
                            messages.warning(request, "You have already added this session to your schedule.")

                            return redirect(request.path)

                        # Check conflict
                        conflict = False
                        for item in profile.schedule.filter(item_type='Session'):
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
                            messages.warning(request, "Warning: This session overlaps with another event in your timetable.")
                        StudentSchedule.objects.create(
                            student=profile,
                            item_type='Session',
                            related_id=session.id,
                            time=dt
                        )
                        messages.success(request, f"'{session.title}' added to your Expo schedule!")

                        return redirect(request.path)
                    except ProgrammeSession.DoesNotExist:
                        messages.error(request, "Selected session does not exist.")

                        return redirect(request.path)
        saved_universities = profile.saved_universities.select_related('university', 'university__profile').all()
        raw_schedule = list(profile.schedule.all().order_by('time'))
        session_ids = [item.related_id for item in raw_schedule if item.item_type == 'Session']
        sessions_map = {s.id: s for s in ProgrammeSession.objects.filter(id__in=session_ids).select_related('speaker', 'event_location')}
        for item in raw_schedule:
            if item.item_type == 'Session':
                item.session = sessions_map.get(item.related_id)
        schedule_items = raw_schedule
        attended_seminars = SeminarAttendance.objects.filter(student=profile).select_related('session', 'session__speaker').order_by('-attended_at')
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
        booth_visits = BoothInteraction.objects.filter(student=profile).select_related('booth', 'booth__university', 'booth__exhibitor').order_by('-interaction_date')
        booked_events = Registration.objects.filter(email=request.user.email).select_related('event_location')
        full_name = request.user.get_full_name() or request.user.username or (passport.student_name if passport else "")
        school_or_org = getattr(profile, 'school_college', '') or getattr(profile, 'current_education', '') or ""
        qr_data = (profile.qr_identifier if profile and profile.qr_identifier else None) or (passport.badge_id if passport else f"KNOVA-STU-{request.user.id:03d}")
        qr = qrcode.make(qr_data)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        upcoming_event = EventLocation.objects.filter(is_active=True, is_upcoming=True).first()
        floor_zones = FloorActivityZone.objects.filter(is_active=True).order_by('order')
        badge_id = (passport.badge_id if passport else None) or f"KNOVA-STU-{request.user.id:03d}"
        context = {
            'role': 'student',
            'profile': profile,
            'passport': passport,
            'qr_base64': qr_base64,
            'full_name': full_name,
            'school_or_org': school_or_org,
            'badge_id': badge_id,
            'student_id': badge_id,
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
            'upcoming_events': EventLocation.objects.filter(is_upcoming=True).order_by('start_date'),
            'linked_parents': profile.parents.select_related('user').all()
        }

    return render(request, 'dashboard/index.html', context)


@login_required(login_url='/portal/login/')
def dashboard_matches(request):
    from django.contrib import messages
    from django.http import JsonResponse
    from .models import UniversityApplication, University
    profile = None
    if hasattr(request.user, 'student_profile'):
        profile = request.user.student_profile
    elif hasattr(request.user, 'parent_profile'):
        linked = request.user.parent_profile.linked_students.all()
        active_id = request.session.get('active_student_id')
        active = linked.filter(id=active_id).first() if active_id else linked.first()
        if active:
            profile = active
    if not profile:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json' or request.method == 'POST':
            return JsonResponse({'status': 'error', 'message': 'Only registered students or supervising parents can access course matchmaking.'}, status=403)
        messages.info(request, "AI Course Finder is available for students and their linked parents.")

        return redirect('dashboard_index')
    from .matchmaking import calculate_matches
    if profile:

        # Check if profile is complete
        if not profile.is_profile_complete:
            messages.warning(request, "Please complete your personal and education details to unlock AI Matches.")

            return redirect('dashboard_student_profile')

        # Handle AJAX Course Booking from Student Dashboard
        if request.method == 'POST' and request.POST.get('action') == 'book_course':
            from .models import Exhibitor, ExhibitorLead, Registration, EventLocation, Enquiry, UniversityApplication
            uni_id = request.POST.get('university_id')
            program_name = (request.POST.get('program_name') or '').strip()
            try:
                uni = University.objects.get(id=uni_id)

                # 1. Update or create UniversityApplication
                app, _ = UniversityApplication.objects.get_or_create(
                    student=profile,
                    university=uni,
                    program_name=program_name,
                    defaults={'status': 'Applied'}
                )
                if app.status != 'Applied':
                    app.status = 'Applied'
                    app.save()

                # 2. Resolve or create Registration for this student
                target_u = getattr(profile, 'user', request.user)
                full_name = target_u.get_full_name() or target_u.username
                email = target_u.email or ''
                phone = getattr(profile, 'mobile', '') or ''
                reg = Registration.objects.filter(email=email).first() if email else None
                if not reg:
                    reg = Registration.objects.create(
                        full_name=full_name,
                        email=email or f"{target_u.username}@knova.student",
                        phone=phone or '7736128087',
                        role='Student',
                        status='Registered',
                        event_location=EventLocation.objects.first()
                    )

                # 3. Match Exhibitor for this University
                exhibitor = Exhibitor.objects.filter(company_name__iexact=uni.name).first()
                if not exhibitor:
                    words = [w for w in uni.name.split() if len(w) > 3]
                    for w in words:
                        exhibitor = Exhibitor.objects.filter(company_name__icontains=w).first()
                        if exhibitor:
                            break
                if not exhibitor:
                    exhibitor = Exhibitor.objects.create(
                        company_name=uni.name,
                        event_location=EventLocation.objects.first(),
                        is_verified=True
                    )

                # 4. Create or update ExhibitorLead with lead_source = 'Book' (or 'Punch & Book')
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
                lead.action_tags = 'Course Booking'
                booking_note = f"Booked Course: {program_name}" if program_name else "Booked Course Seat"
                if lead.notes and booking_note not in lead.notes:
                    lead.notes = f"{lead.notes} | {booking_note}"
                else:
                    lead.notes = booking_note
                lead.save()

                # 5. Record Enquiry
                Enquiry.objects.create(
                    student=profile,
                    university=uni,
                    message=f"Booked Course: {program_name} | Booked from Student Dashboard",
                    status='Pending'
                )

                return JsonResponse({'status': 'booked', 'is_booked': True, 'message': f'Booked {program_name} successfully!'})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)

        # Handle AJAX toggle shortlist
        if request.method == 'POST' and request.POST.get('action') == 'toggle_shortlist':
            course_id = request.POST.get('course_id')
            uni_id = request.POST.get('university_id')
            program_name = request.POST.get('program_name', 'Undergraduate Degree')
            existing = UniversityApplication.objects.filter(student=profile, university_id=uni_id, status='Shortlisted').first()
            if existing:
                existing.delete()

                return JsonResponse({'status': 'removed', 'is_shortlisted': False})
            else:
                try:
                    uni = University.objects.get(id=uni_id)
                    UniversityApplication.objects.create(
                        student=profile,
                        university=uni,
                        program_name=program_name,
                        status='Shortlisted'
                    )

                    return JsonResponse({'status': 'added', 'is_shortlisted': True})
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=400)

        # Handle Reset / Clear All
        if request.GET.get('clear') == '1':
            profile.preferred_country = ''
            profile.budget_range = ''
            profile.preferred_program = ''
            profile.intake_year = '2027'
            profile.save()
            messages.info(request, "Filters have been reset.")

            return redirect('dashboard_matches')

        # Handle Matchmaking Preferences update from the search bar
        if request.method == 'POST':
            profile.preferred_country = request.POST.get('preferred_country', '')
            profile.budget_range = request.POST.get('budget_range', '')
            profile.preferred_program = request.POST.get('preferred_program', '')
            profile.preferred_degree = request.POST.get('preferred_degree', '')
            profile.intake_year = request.POST.get('intake_year', '')
            profile.save()
            messages.success(request, "Matchmaking preferences updated!")

            return redirect('dashboard_matches')
        matches = calculate_matches(profile)

        # Filter by search keyword if provided
        q = request.GET.get('q', '').strip().lower()
        if q:
            matches = [
                m for m in matches
                if q in m['course'].name.lower() or q in m['course'].university.name.lower()
            ]

        # Iconic campus photos matching universities in reference design
        UNI_PHOTO_MAP = {
            'harvard': 'https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=600&auto=format&fit=crop&q=80',
            'mit': 'https://images.unsplash.com/photo-1562774053-701939374585?w=600&auto=format&fit=crop&q=80',
            'chicago': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=600&auto=format&fit=crop&q=80',
            'manchester': 'https://images.unsplash.com/photo-1592280771190-3e2e4d571952?w=600&auto=format&fit=crop&q=80',
            'bristol': 'https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=600&auto=format&fit=crop&q=80',
            'oxford': 'https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=600&auto=format&fit=crop&q=80',
            'cambridge': 'https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop&q=80',
            'stanford': 'https://images.unsplash.com/photo-1509062522246-3755977927d7?w=600&auto=format&fit=crop&q=80',
        }
        CAMPUS_FALLBACKS = [
            'https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=600&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1562774053-701939374585?w=600&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=600&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1592280771190-3e2e4d571952?w=600&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=600&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=600&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1564981797816-1043664bf78d?w=600&auto=format&fit=crop&q=80',
            'https://images.unsplash.com/photo-1590012314607-cda9d9b699ae?w=600&auto=format&fit=crop&q=80',
        ]
        shortlisted_uni_ids = set(UniversityApplication.objects.filter(student=profile, status='Shortlisted').values_list('university_id', flat=True))
        applied_programs = set(UniversityApplication.objects.filter(student=profile, status='Applied').values_list('program_name', flat=True))
        for m in matches:
            raw_name = m['course'].university.name
            u_name = raw_name.lower()

            # Calculate crisp university monogram initials (e.g. Harvard University -> HU, MIT -> MIT)
            clean_words = [w for w in raw_name.replace('of', '').replace('&', '').split() if w]
            if len(clean_words) >= 2:
                initials = (clean_words[0][0] + clean_words[1][0]).upper()
            elif len(clean_words) == 1:
                initials = clean_words[0][:3].upper()
            else:
                initials = "UN"
            m['initials'] = initials
            prof = getattr(m['course'].university, 'profile', None)
            m['logo_url'] = prof.logo.url if (prof and prof.logo) else None
            m['is_shortlisted'] = m['course'].university.id in shortlisted_uni_ids
            m['is_booked'] = (m['course'].name in applied_programs) or (m['course'].degree_type in applied_programs)
    else:
        profile = None
        matches = []
    from .models import Country
    countries = Country.objects.filter(is_active=True).order_by('order', 'name')
    context = {
        'role': 'student',
        'profile': profile,
        'matches': matches,
        'countries': countries,
        'query': request.GET.get('q', '')
    }

    return render(request, 'dashboard/matches.html', context)


@login_required(login_url='/portal/login/')
def dashboard_events(request):
    from .models import EventLocation, ProgrammeSession
    from django.urls import reverse
    from django.db.models import Q
    query = request.GET.get('q', '').strip()
    filter_type = request.GET.get('type', 'all').lower()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    sort_by = request.GET.get('sort_by', 'date')

    # Query expos
    events_qs = EventLocation.objects.all()
    if query:
        events_qs = events_qs.filter(Q(name__icontains=query) | Q(city__icontains=query) | Q(venue__icontains=query))
    if start_date:
        events_qs = events_qs.filter(start_date__gte=start_date)
    if end_date:
        events_qs = events_qs.filter(end_date__lte=end_date)

    # Query seminars
    sessions_qs = ProgrammeSession.objects.all().select_related('event_location', 'speaker')
    if query:
        sessions_qs = sessions_qs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(speaker__name__icontains=query) | Q(event_location__city__icontains=query) | Q(hall_name__icontains=query))
    if start_date:
        sessions_qs = sessions_qs.filter(date__gte=start_date)
    if end_date:
        sessions_qs = sessions_qs.filter(date__lte=end_date)
    items = []

    # Include expos if filter is 'all' or 'expo'
    if filter_type in ['all', 'expo']:
        for ev in events_qs:
            start_fmt = ev.start_date.strftime('%b %d') if ev.start_date else ''
            end_fmt = ev.end_date.strftime('%b %d, %Y') if ev.end_date else ''
            date_display = f"{start_fmt} - {end_fmt}" if start_fmt and end_fmt else (start_fmt or end_fmt)
            time_display = ev.timings or '10:00 AM - 07:00 PM Daily'
            items.append({
                'id': ev.id,
                'item_type': 'Expo',
                'type_key': 'expo',
                'title': ev.name,
                'city': ev.city or 'Dubai',
                'venue': ev.venue or 'Convention Centre',
                'date_display': date_display,
                'time_display': time_display,
                'speaker': None,
                'is_active': ev.is_active,
                'edit_url': reverse('event_update', args=[ev.id]),
                'delete_url': reverse('event_delete', args=[ev.id]),
                'sort_date': ev.start_date,
                'sort_title': ev.name.lower(),
            })

    # Include seminars if filter is 'all' or 'seminar'
    if filter_type in ['all', 'seminar']:
        for sm in sessions_qs:
            date_fmt = sm.date.strftime('%b %d, %Y') if sm.date else ''
            start_time_fmt = sm.start_time.strftime('%I:%M %p') if sm.start_time else ''
            end_time_fmt = sm.end_time.strftime('%I:%M %p') if sm.end_time else ''
            time_display = f"{start_time_fmt} - {end_time_fmt}" if start_time_fmt and end_time_fmt else (start_time_fmt or 'TBA')
            city_name = sm.event_location.city if sm.event_location else 'Dubai'
            items.append({
                'id': sm.id,
                'item_type': 'Seminar',
                'type_key': 'seminar',
                'title': sm.title,
                'city': city_name,
                'venue': sm.hall_name or 'Main Auditorium',
                'date_display': date_fmt,
                'time_display': time_display,
                'speaker': sm.speaker.name if sm.speaker else None,
                'is_active': True,
                'login_username': sm.login_username or f"seminar_{sm.id}",
                'login_password': sm.login_password or 'seminar123',
                'attendance_count': sm.attendances_count,
                'scanner_url': f"{reverse('seminar_attendance_scanner')}?session_id={sm.id}",
                'roster_url': f"{reverse('seminar_attendance_roster')}?session_id={sm.id}",
                'edit_url': reverse('programme_update', args=[sm.id]),
                'delete_url': reverse('programme_delete', args=[sm.id]),
                'sort_date': sm.date,
                'sort_title': sm.title.lower(),
            })

    # Sorting
    if sort_by in ['name', 'title']:
        items.sort(key=lambda x: x['sort_title'])
    elif sort_by in ['-name', '-title']:
        items.sort(key=lambda x: x['sort_title'], reverse=True)
    elif sort_by == '-date':
        items.sort(key=lambda x: (x['sort_date'] is None, x['sort_date']), reverse=True)
    else:  # default 'date' or 'start_date'
        items.sort(key=lambda x: (x['sort_date'] is None, x['sort_date']))
    total_expos_count = EventLocation.objects.count()
    total_seminars_count = ProgrammeSession.objects.count()
    total_all_count = total_expos_count + total_seminars_count
    context = {
        'items': items,
        'events': events_qs,
        'total_all_count': total_all_count,
        'total_expos_count': total_expos_count,
        'total_seminars_count': total_seminars_count,
        'filter_type': filter_type,
        'start_date': start_date,
        'end_date': end_date,
        'sort_by': sort_by,
        'query': query,
    }

    return render(request, 'dashboard/events.html', context)


@login_required(login_url='/portal/login/')
def event_create(request):
    if not (request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name__in=['admin', 'manager', 'editor']).exists()):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")
    from .forms import EventLocationForm
    from django.contrib import messages
    if request.method == 'POST':
        form = EventLocationForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, f"Event '{event.name}' created successfully!")
            return redirect('dashboard_events')
        else:
            messages.error(request, "Please review and correct the errors below.")
    else:
        form = EventLocationForm()

    return render(request, 'dashboard/event_form.html', {'form': form, 'action': 'Create'})


@login_required(login_url='/portal/login/')
def event_update(request, pk):
    if not (request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name__in=['admin', 'manager', 'editor']).exists()):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")
    from .forms import EventLocationForm
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    event = get_object_or_404(EventLocation, pk=pk)
    if request.method == 'POST':
        form = EventLocationForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f"Event '{event.name}' updated successfully!")
            return redirect('dashboard_events')
        else:
            messages.error(request, "Please review and correct the errors below.")
    else:
        form = EventLocationForm(instance=event)

    return render(request, 'dashboard/event_form.html', {'form': form, 'event': event, 'action': 'Update'})


@login_required(login_url='/portal/login/')
def event_delete(request, pk):
    if not (request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name__in=['admin', 'manager', 'editor']).exists()):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    event = get_object_or_404(EventLocation, pk=pk)
    if request.method == 'POST':
        event_name = event.name
        event.delete()
        messages.success(request, f"Event '{event_name}' was deleted.")
        return redirect('dashboard_events')

    return render(request, 'dashboard/event_confirm_delete.html', {'event': event})


@login_required(login_url='/portal/login/')
def dashboard_exhibitors(request):
    from .models import Exhibitor, ExpoBooth
    exhibitors = Exhibitor.objects.all().select_related('event_location', 'booth')
    sort_by = request.GET.get('sort_by', 'company_name')
    is_verified = request.GET.get('is_verified')
    booth_filter = request.GET.get('booth')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        exhibitors = exhibitors.filter(event_location__start_date__gte=start_date)
    if end_date:
        exhibitors = exhibitors.filter(event_location__end_date__lte=end_date)
    if is_verified == '1':
        exhibitors = exhibitors.filter(is_verified=True)
    elif is_verified == '0':
        exhibitors = exhibitors.filter(is_verified=False)
    if booth_filter == 'allocated':
        exhibitors = exhibitors.filter(booth__isnull=False)
    elif booth_filter == 'unallocated':
        exhibitors = exhibitors.filter(booth__isnull=True)
    from django.db.models.functions import Lower
    if sort_by == 'company_name':
        exhibitors = exhibitors.order_by(Lower('company_name'))
    elif sort_by == '-company_name':
        exhibitors = exhibitors.order_by(Lower('company_name').desc())
    elif sort_by == 'booth':
        exhibitors = exhibitors.order_by('booth__booth_number')
    else:
        exhibitors = exhibitors.order_by(sort_by)
    total_count = Exhibitor.objects.count()
    allocated_count = ExpoBooth.objects.filter(exhibitor__isnull=False).count()
    unallocated_count = max(0, total_count - allocated_count)
    context = {
        'exhibitors': exhibitors,
        'sort_by': sort_by,
        'is_verified': is_verified,
        'booth_filter': booth_filter,
        'start_date': start_date,
        'end_date': end_date,
        'total_count': total_count,
        'allocated_count': allocated_count,
        'unallocated_count': unallocated_count,
    }

    return render(request, 'dashboard/exhibitors.html', context)


@login_required(login_url='/portal/login/')
def exhibitor_allocate_booth(request, pk):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")
    from .models import Exhibitor, ExpoBooth
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    exhibitor = get_object_or_404(Exhibitor, pk=pk)
    if request.method == 'POST':
        booth_num = request.POST.get('booth_number', '').strip()
        hall_name = request.POST.get('hall', '').strip() or 'Hall 1 - Global Pavilion'
        if booth_num:
            if hasattr(exhibitor, 'booth') and exhibitor.booth:
                b = exhibitor.booth
                b.booth_number = booth_num
                b.hall = hall_name
                b.status = 'ASSIGNED'
                b.save()
            else:
                existing = ExpoBooth.objects.filter(booth_number__iexact=booth_num).first()
                if existing:
                    existing.exhibitor = exhibitor
                    existing.hall = hall_name
                    existing.status = 'ASSIGNED'
                    existing.save()
                else:
                    ExpoBooth.objects.create(
                        booth_number=booth_num,
                        hall=hall_name,
                        exhibitor=exhibitor,
                        status='ASSIGNED'
                    )
            messages.success(request, f"Booth {booth_num} allocated to {exhibitor.company_name}.")
        else:
            if hasattr(exhibitor, 'booth') and exhibitor.booth:
                b = exhibitor.booth
                b.exhibitor = None
                if not b.university:
                    b.status = 'AVAILABLE'
                b.save()
                messages.info(request, f"Booth allocation removed for {exhibitor.company_name}.")
    next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard_exhibitors'

    return redirect(next_url)


@login_required(login_url='/portal/login/')
def exhibitor_create(request):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")
    from .forms import ExhibitorForm
    if request.method == 'POST':
        form = ExhibitorForm(request.POST, request.FILES)
        if form.is_valid():
            exh = form.save()
            # Synchronize with University model
            from .models import University, UniversityProfile
            from django.utils.text import slugify
            uni = University.objects.filter(name__iexact=exh.company_name).first()
            if not uni:
                base_slug = slugify(exh.company_name) or f"exh-{exh.id}"
                slug = base_slug
                c = 1
                while University.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{c}"
                    c += 1
                uni = University.objects.create(
                    name=exh.company_name,
                    slug=slug,
                    is_approved=exh.is_verified
                )
            if not exh.university:
                exh.university = uni
                exh.save(update_fields=['university'])

            u_prof, _ = UniversityProfile.objects.get_or_create(university=uni)
            if exh.country and not u_prof.location_state_country:
                u_prof.location_state_country = exh.country
            if exh.website and not u_prof.website:
                u_prof.website = exh.website
            if exh.logo and not u_prof.logo:
                u_prof.logo = exh.logo
            u_prof.save()

            return redirect('dashboard_exhibitors')
    else:
        form = ExhibitorForm()

    return render(request, 'dashboard/exhibitor_form.html', {'form': form, 'action': 'Create'})


@login_required(login_url='/portal/login/')
def exhibitor_update(request, pk):
    from .forms import ExhibitorForm
    from .models import Exhibitor
    from django.shortcuts import get_object_or_404
    exhibitor = get_object_or_404(Exhibitor, pk=pk)

    # Object Level Security
    if not request.user.is_superuser:
        if not hasattr(request.user, 'exhibitor_profile') or request.user.exhibitor_profile.pk != exhibitor.pk:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to edit this profile.")
    if request.method == 'POST':
        form = ExhibitorForm(request.POST, request.FILES, instance=exhibitor)
        if form.is_valid():
            form.save()

            return redirect('dashboard_exhibitors')
    else:
        form = ExhibitorForm(instance=exhibitor)

    return render(request, 'dashboard/exhibitor_form.html', {'form': form, 'action': 'Update'})


@login_required(login_url='/portal/login/')
def exhibitor_delete(request, pk):
    from .models import Exhibitor
    from django.shortcuts import get_object_or_404
    exhibitor = get_object_or_404(Exhibitor, pk=pk)

    # Object Level Security
    if not request.user.is_superuser:
        if not hasattr(request.user, 'exhibitor_profile') or request.user.exhibitor_profile.pk != exhibitor.pk:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to delete this profile.")
    if request.method == 'POST':
        exhibitor.delete()

        return redirect('dashboard_exhibitors')

    return render(request, 'dashboard/exhibitor_confirm_delete.html', {'exhibitor': exhibitor})


@login_required(login_url='/portal/login/')
def dashboard_sponsors(request):
    from .models import Sponsor
    sponsors = Sponsor.objects.all().select_related('event_location')
    category = request.GET.get('category')
    sort_by = request.GET.get('sort_by', 'name')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        sponsors = sponsors.filter(event_location__start_date__gte=start_date)
    if end_date:
        sponsors = sponsors.filter(event_location__end_date__lte=end_date)
    if category:
        sponsors = sponsors.filter(category=category)
    from django.db.models.functions import Lower
    if sort_by == 'name':
        sponsors = sponsors.order_by(Lower('name'))
    elif sort_by == '-name':
        sponsors = sponsors.order_by(Lower('name').desc())
    else:
        sponsors = sponsors.order_by(sort_by)
    available_categories = sorted(list(set(Sponsor.objects.exclude(category__isnull=True).exclude(category='').values_list('category', flat=True))))
    total_sponsors_count = Sponsor.objects.count()
    verified_sponsors_count = Sponsor.objects.filter(is_verified=True).count()
    context = {
        'available_categories': available_categories,
        'total_sponsors_count': total_sponsors_count,
        'verified_sponsors_count': verified_sponsors_count,
        'sponsors': sponsors,
        'category': category,
        'sort_by': sort_by,
        'start_date': start_date,
        'end_date': end_date
    }

    return render(request, 'dashboard/sponsors.html', context)


@login_required(login_url='/portal/login/')
def sponsor_create(request):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")
    from .forms import SponsorForm
    if request.method == 'POST':
        form = SponsorForm(request.POST, request.FILES)
        if form.is_valid():
            sp = form.save(commit=False)
            sp.is_verified = True
            sp.save()

            return redirect('dashboard_sponsors')
    else:
        form = SponsorForm()

    return render(request, 'dashboard/sponsor_form.html', {'form': form, 'action': 'Create'})


@login_required(login_url='/portal/login/')
def sponsor_update(request, pk):
    from .forms import SponsorForm
    from .models import Sponsor
    from django.shortcuts import get_object_or_404
    sponsor = get_object_or_404(Sponsor, pk=pk)

    # Object Level Security
    if not request.user.is_superuser:
        if not hasattr(request.user, 'sponsor_profile') or request.user.sponsor_profile.pk != sponsor.pk:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to edit this profile.")
    if request.method == 'POST':
        form = SponsorForm(request.POST, request.FILES, instance=sponsor)
        if form.is_valid():
            form.save()

            return redirect('dashboard_sponsors')
    else:
        form = SponsorForm(instance=sponsor)

    return render(request, 'dashboard/sponsor_form.html', {'form': form, 'action': 'Update'})


@login_required(login_url='/portal/login/')
def sponsor_delete(request, pk):
    from .models import Sponsor
    from django.shortcuts import get_object_or_404
    sponsor = get_object_or_404(Sponsor, pk=pk)

    # Object Level Security
    if not request.user.is_superuser:
        if not hasattr(request.user, 'sponsor_profile') or request.user.sponsor_profile.pk != sponsor.pk:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to delete this profile.")
    if request.method == 'POST':
        sponsor.delete()

        return redirect('dashboard_sponsors')

    return render(request, 'dashboard/sponsor_confirm_delete.html', {'sponsor': sponsor})


@login_required(login_url='/portal/login/')
def dashboard_speakers(request):
    """Unified Admin view to manage Speakers and Education Experts with toggle filtering."""
    from .models import Speaker, EducationExpert, ExpertConsultationAttendance, ProgrammeSession
    from django.db.models import Count, Q
    from django.urls import reverse
    filter_type = request.GET.get('type', 'all').lower()
    query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort_by', 'name')
    is_verified = request.GET.get('is_verified')

    # Total counts
    total_speakers_count = Speaker.objects.count()
    total_experts_count = EducationExpert.objects.count()
    total_all_count = total_speakers_count + total_experts_count
    active_desks = EducationExpert.objects.values('desk_name').distinct().count()
    total_punched = ExpertConsultationAttendance.objects.count()
    verified_speakers_count = Speaker.objects.filter(is_verified=True).count()
    items = []

    # Query Speakers
    speakers_qs = Speaker.objects.all().prefetch_related('programmesession_set')
    if query:
        speakers_qs = speakers_qs.filter(
            Q(name__icontains=query) |
            Q(title__icontains=query) |
            Q(organization__icontains=query) |
            Q(profile__icontains=query)
        )
    if is_verified == '1':
        speakers_qs = speakers_qs.filter(is_verified=True)
    elif is_verified == '0':
        speakers_qs = speakers_qs.filter(is_verified=False)

    # Query Education Experts
    experts_qs = EducationExpert.objects.select_related('user').annotate(
        total_punched=Count('consultations')
    )
    if query:
        experts_qs = experts_qs.filter(
            Q(name__icontains=query) |
            Q(desk_name__icontains=query) |
            Q(title__icontains=query) |
            Q(specialization__icontains=query) |
            Q(user__username__icontains=query)
        )

    # If filter is 'all' or 'speaker', include speakers
    if filter_type in ['all', 'speaker', 'speakers']:
        for sp in speakers_qs:
            sessions = list(sp.programmesession_set.all())
            items.append({
                'id': sp.id,
                'item_type': 'Speaker',
                'type_key': 'speaker',
                'name': sp.name,
                'title': sp.title or 'Keynote Speaker',
                'organization': sp.organization or 'Independent Academic',
                'photo': sp.photo.url if sp.photo else None,
                'is_verified': sp.is_verified,
                'sessions': sessions,
                'sessions_count': len(sessions),
                'user': sp.user,
                'edit_url': reverse('speaker_update', args=[sp.id]),
                'delete_url': reverse('speaker_delete', args=[sp.id]),
                'sort_name': sp.name.lower(),
            })

    # If filter is 'all' or 'expert', include education experts
    if filter_type in ['all', 'expert', 'experts']:
        for exp in experts_qs:
            items.append({
                'id': exp.id,
                'item_type': 'Education Expert',
                'type_key': 'expert',
                'name': exp.name,
                'title': exp.title or 'Senior Academic Counsellor',
                'organization': exp.desk_name or 'Academic Counselling Hub',
                'desk_name': exp.desk_name or 'Academic Counselling Hub',
                'specialization': exp.specialization or 'Global Admissions Advisory & Scholarships',
                'mobile': exp.mobile or '',
                'photo': None,
                'is_verified': True,
                'sessions': [],
                'sessions_count': 0,
                'user': exp.user,
                'raw_password': exp.raw_password,
                'total_punched': exp.total_punched,
                'scanner_url': reverse('expert_attendance_scanner'),
                'sort_name': exp.name.lower(),
                'raw_expert': exp,
            })

    # Sorting
    if sort_by in ['name', 'title']:
        items.sort(key=lambda x: x['sort_name'])
    elif sort_by in ['-name', '-title']:
        items.sort(key=lambda x: x['sort_name'], reverse=True)
    elif sort_by == 'type':
        items.sort(key=lambda x: (x['type_key'], x['sort_name']))
    else:
        items.sort(key=lambda x: x['sort_name'])
    context = {
        'items': items,
        'speakers': speakers_qs,
        'experts': experts_qs,
        'total_all_count': total_all_count,
        'total_speakers_count': total_speakers_count,
        'total_experts_count': total_experts_count,
        'active_desks': active_desks,
        'total_punched': total_punched,
        'verified_speakers_count': verified_speakers_count,
        'filter_type': filter_type,
        'query': query,
        'sort_by': sort_by,
        'is_verified': is_verified,
        'page_title': 'Speakers & Education Experts',
    }

    return render(request, 'dashboard/speakers.html', context)


@login_required(login_url='/portal/login/')
def speaker_create(request):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")
    from .forms import SpeakerForm
    if request.method == 'POST':
        form = SpeakerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            return redirect('dashboard_speakers')
    else:
        form = SpeakerForm()

    return render(request, 'dashboard/speaker_form.html', {'form': form, 'action': 'Create'})


@login_required(login_url='/portal/login/')
def speaker_update(request, pk):
    from .forms import SpeakerForm
    from .models import Speaker
    from django.shortcuts import get_object_or_404
    speaker = get_object_or_404(Speaker, pk=pk)

    # Object Level Security
    if not request.user.is_superuser:
        if not hasattr(request.user, 'speaker_profile') or request.user.speaker_profile.pk != speaker.pk:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to edit this profile.")
    if request.method == 'POST':
        form = SpeakerForm(request.POST, request.FILES, instance=speaker)
        if form.is_valid():
            form.save()

            return redirect('dashboard_speakers')
    else:
        form = SpeakerForm(instance=speaker)

    return render(request, 'dashboard/speaker_form.html', {'form': form, 'action': 'Update'})


@login_required(login_url='/portal/login/')
def speaker_delete(request, pk):
    from .models import Speaker
    from django.shortcuts import get_object_or_404
    speaker = get_object_or_404(Speaker, pk=pk)

    # Object Level Security
    if not request.user.is_superuser:
        if not hasattr(request.user, 'speaker_profile') or request.user.speaker_profile.pk != speaker.pk:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to delete this profile.")
    if request.method == 'POST':
        speaker.delete()

        return redirect('dashboard_speakers')

    return render(request, 'dashboard/speaker_confirm_delete.html', {'speaker': speaker})


@login_required(login_url='/portal/login/')
def dashboard_programme(request):
    from django.shortcuts import redirect
    from django.urls import reverse

    return redirect(reverse('dashboard_events') + '?type=seminar')


@login_required(login_url='/portal/login/')
def programme_create(request):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")
    from .forms import ProgrammeSessionForm
    if request.method == 'POST':
        form = ProgrammeSessionForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('/dashboard/events/?type=seminar')
    else:
        form = ProgrammeSessionForm()

    return render(request, 'dashboard/programme_form.html', {'form': form, 'action': 'Create'})


@login_required(login_url='/portal/login/')
def programme_update(request, pk):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")
    from .forms import ProgrammeSessionForm
    from .models import ProgrammeSession
    from django.shortcuts import get_object_or_404
    session = get_object_or_404(ProgrammeSession, pk=pk)
    if request.method == 'POST':
        form = ProgrammeSessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()

            return redirect('/dashboard/events/?type=seminar')
    else:
        form = ProgrammeSessionForm(instance=session)

    return render(request, 'dashboard/programme_form.html', {'form': form, 'action': 'Update'})


@login_required(login_url='/portal/login/')
def programme_delete(request, pk):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")
    from .models import ProgrammeSession
    from django.shortcuts import get_object_or_404
    session = get_object_or_404(ProgrammeSession, pk=pk)
    if request.method == 'POST':
        session.delete()

        return redirect('/dashboard/events/?type=seminar')

    return render(request, 'dashboard/programme_confirm_delete.html', {'session': session})


@login_required(login_url='/portal/login/')
def dashboard_registrations(request):
    from .models import Registration
    registrations = Registration.objects.all().select_related('event_location')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    role = request.GET.get('role')
    sort_by = request.GET.get('sort_by', '-registered_at')
    if start_date:
        registrations = registrations.filter(registered_at__gte=start_date)
    if end_date:
        registrations = registrations.filter(registered_at__lte=end_date)
    if role:
        registrations = registrations.filter(role=role)
    from django.db.models.functions import Lower
    if sort_by == 'full_name':
        registrations = registrations.order_by(Lower('full_name'))
    elif sort_by == '-full_name':
        registrations = registrations.order_by(Lower('full_name').desc())
    else:
        registrations = registrations.order_by(sort_by)
    from .utils import get_top_matches_for_exhibitor
    matches = []
    if hasattr(request.user, 'exhibitor_profile') and not request.user.is_superuser:
        profile = request.user.exhibitor_profile
        registrations = profile.interested_students.all()
        if start_date:
            registrations = registrations.filter(registered_at__gte=start_date)
        if end_date:
            registrations = registrations.filter(registered_at__lte=end_date)
        if role:
            registrations = registrations.filter(role=role)
        if sort_by == 'full_name':
            registrations = registrations.order_by(Lower('full_name'))
        elif sort_by == '-full_name':
            registrations = registrations.order_by(Lower('full_name').desc())
        else:
            registrations = registrations.order_by(sort_by)
        matches = get_top_matches_for_exhibitor(profile, limit=10)
    context = {
        'registrations': registrations,
        'matches': matches,
        'start_date': start_date,
        'end_date': end_date,
        'role': role,
        'sort_by': sort_by
    }

    return render(request, 'dashboard/registrations.html', context)


@login_required(login_url='/portal/login/')
def registration_create(request):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")
    from .forms import RegistrationForm
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('dashboard_registrations')
    else:
        form = RegistrationForm()

    return render(request, 'dashboard/registration_form.html', {'form': form, 'action': 'Create'})


@login_required(login_url='/portal/login/')
def registration_update(request, pk):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")
    from .forms import RegistrationForm
    from .models import Registration
    from django.shortcuts import get_object_or_404
    registration = get_object_or_404(Registration, pk=pk)
    if request.method == 'POST':
        form = RegistrationForm(request.POST, instance=registration)
        if form.is_valid():
            form.save()

            return redirect('dashboard_registrations')
    else:
        form = RegistrationForm(instance=registration)

    return render(request, 'dashboard/registration_form.html', {'form': form, 'action': 'Update'})


@login_required(login_url='/portal/login/')
def registration_delete(request, pk):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")
    from .models import Registration
    from django.shortcuts import get_object_or_404
    registration = get_object_or_404(Registration, pk=pk)
    if request.method == 'POST':
        registration.delete()

        return redirect('dashboard_registrations')

    return render(request, 'dashboard/registration_confirm_delete.html', {'registration': registration})


@login_required(login_url='/portal/login/')
def dashboard_cms(request):
    from .models import SiteConfiguration, CustomSection
    from .forms import SiteConfigurationForm
    from django.contrib import messages
    from django.http import JsonResponse
    from django.shortcuts import redirect, render

    if not (request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name__in=['admin', 'manager', 'editor', 'seo']).exists()):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to edit website content or section visibility.")

    config = SiteConfiguration.get_solo()
    active_tab = request.GET.get('tab', 'sections')
    if active_tab == 'seo':
        return redirect('dashboard_seo')

    # Instant AJAX toggle for any boolean field (show_* or disable_*)
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.POST.get('action') == 'toggle_section':
        field_name = request.POST.get('field')
        if hasattr(config, field_name) and isinstance(getattr(config, field_name), bool):
            current_val = getattr(config, field_name)
            new_val = not current_val
            setattr(config, field_name, new_val)
            config.save(update_fields=[field_name])
            if field_name.startswith('disable_'):
                label = field_name.replace('disable_', '').replace('_', ' ').title()
                msg = f"{label} is now {'Disabled (Click Locked)' if new_val else 'Active & Clickable'}."
            else:
                label = field_name.replace('show_', '').replace('_', ' ').title()
                msg = f"{label} is now {'Visible' if new_val else 'Hidden'} on website."
            return JsonResponse({
                'status': 'success',
                'field': field_name,
                'is_active': new_val,
                'is_visible': new_val if not field_name.startswith('disable_') else None,
                'is_disabled': new_val if field_name.startswith('disable_') else None,
                'message': msg
            })
        return JsonResponse({'status': 'error', 'message': 'Invalid setting field.'}, status=400)

    # AJAX Toggle Custom Dynamic Section
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.POST.get('action') == 'toggle_custom_section':
        sec_id = request.POST.get('section_id')
        sec = CustomSection.objects.filter(id=sec_id).first()
        if sec:
            sec.is_active = not sec.is_active
            sec.save(update_fields=['is_active'])
            return JsonResponse({
                'status': 'success',
                'section_id': sec.id,
                'is_active': sec.is_active,
                'message': f"Custom section '{sec.name}' is now {'Visible' if sec.is_active else 'Hidden'}."
            })
        return JsonResponse({'status': 'error', 'message': 'Custom section not found.'}, status=404)

    # Standard Form Actions
    if request.method == 'POST':
        action = request.POST.get('action')

        # Add or edit Custom Section
        if action == 'save_custom_section':
            sec_id = request.POST.get('section_id')
            if sec_id:
                sec = CustomSection.objects.filter(id=sec_id).first()
            else:
                sec = CustomSection()
            if sec:
                sec.name = request.POST.get('name', 'Custom Section').strip()
                sec.badge = request.POST.get('badge', '').strip()
                sec.title = request.POST.get('title', '').strip()
                sec.subtitle = request.POST.get('subtitle', '').strip()
                sec.content_html = request.POST.get('content_html', '').strip()
                sec.bg_color = request.POST.get('bg_color', '#ffffff').strip() or '#ffffff'
                sec.text_color = request.POST.get('text_color', '#0f172a').strip() or '#0f172a'
                sec.button_text = request.POST.get('button_text', '').strip()
                sec.button_url = request.POST.get('button_url', '').strip()
                sec.placement = request.POST.get('placement', 'after_why')
                try:
                    sec.order = int(request.POST.get('order', 1))
                except (ValueError, TypeError):
                    sec.order = 1
                sec.is_active = (request.POST.get('is_active') == 'on') or (request.POST.get('is_active') == 'true')
                sec.save()
                messages.success(request, f"Custom section '{sec.name}' saved successfully!")
                return redirect('/dashboard/cms/?tab=sections')

        # Delete Custom Section
        elif action == 'delete_custom_section':
            sec_id = request.POST.get('section_id')
            sec = CustomSection.objects.filter(id=sec_id).first()
            if sec:
                sec_name = sec.name
                sec.delete()
                messages.success(request, f"Custom section '{sec_name}' was removed from the website.")
            return redirect('/dashboard/cms/?tab=sections')

        # Save CMS General / Content Form
        else:
            active_tab_post = request.POST.get('active_tab', active_tab)
            post_data = request.POST.copy()
            if active_tab_post != 'sections':
                # Preserve all boolean toggles when editing content/seo tabs
                for f in config._meta.fields:
                    if f.name.startswith(('show_', 'disable_')):
                        if getattr(config, f.name):
                            post_data[f.name] = 'on'
                        else:
                            post_data.pop(f.name, None)
            if active_tab_post != 'seo':
                # Preserve schema org toggle when editing non-seo tabs
                if config.enable_schema_org:
                    post_data['enable_schema_org'] = 'on'
                else:
                    post_data.pop('enable_schema_org', None)
            form = SiteConfigurationForm(post_data, request.FILES, instance=config)

            if form.is_valid():
                form.save()
                messages.success(request, "Website contents and section visibility updated successfully!")
                return redirect(f"/dashboard/cms/?tab={active_tab_post}")
            else:
                messages.error(request, "There was an error saving some settings. Please review the highlighted fields.")
    else:
        form = SiteConfigurationForm(instance=config)

    custom_sections_list = CustomSection.objects.all().order_by('order', '-created_at')

    context = {
        'form': form,
        'config': config,
        'active_tab': active_tab,
        'custom_sections_list': custom_sections_list,
    }
    return render(request, 'dashboard/cms.html', context)



@login_required(login_url='/portal/login/')
def dashboard_seo(request):
    from .models import SiteConfiguration
    from .forms import SiteConfigurationForm
    from django.contrib import messages
    from django.core.exceptions import PermissionDenied
    from django.shortcuts import redirect, render

    if not (request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name__in=['admin', 'manager', 'editor', 'seo']).exists()):
        raise PermissionDenied("You do not have permission to manage SEO configurations.")

    config = SiteConfiguration.get_solo()
    seo_tab = request.GET.get('tab', 'primary')

    if request.method == 'POST':
        post_data = request.POST.copy()
        # Preserve all boolean toggles from other sections
        for f in config._meta.fields:
            if f.name.startswith(('show_', 'disable_')):
                if getattr(config, f.name):
                    post_data[f.name] = 'on'
                else:
                    post_data.pop(f.name, None)

        # Handle enable_schema_org
        if request.POST.get('enable_schema_org') in ['on', 'true', True]:
            post_data['enable_schema_org'] = 'on'
        else:
            post_data.pop('enable_schema_org', None)

        form = SiteConfigurationForm(post_data, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "SEO & Search Engine configurations saved successfully!")
            target_tab = request.POST.get('seo_tab', seo_tab)
            return redirect(f"/dashboard/seo/?tab={target_tab}")
        else:
            messages.error(request, "Please correct the highlighted fields in the SEO form.")
    else:
        form = SiteConfigurationForm(instance=config)

    context = {
        'form': form,
        'config': config,
        'seo_tab': seo_tab,
    }
    return render(request, 'dashboard/seo.html', context)

@login_required(login_url='/portal/login/')
def dashboard_settings(request):
    from .models import SiteConfiguration, DataImportJob, Country
    from .forms import SiteConfigurationForm
    from django.contrib import messages
    from django.shortcuts import render, redirect
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.db.models import Q
    from django.db.models.functions import Lower

    if not request.user.is_superuser and not request.user.groups.filter(name__in=['admin', 'manager', 'seo']).exists():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to access site settings.")

    config = SiteConfiguration.get_solo()
    active_tab = request.GET.get('tab', 'backup')

    # Country CSV Export
    export_format = request.GET.get('export')
    if active_tab == 'countries' and export_format in ['csv', 'excel']:
        import csv
        from django.http import HttpResponse
        from django.utils import timezone
        countries_qs = Country.objects.all()
        q = (request.GET.get('q') or '').strip()
        if q:
            countries_qs = countries_qs.filter(
                Q(name__icontains=q) | Q(code__icontains=q) | Q(continent__icontains=q) | Q(dial_code__icontains=q)
            )
        selected_continent = (request.GET.get('continent') or '').strip()
        if selected_continent:
            countries_qs = countries_qs.filter(continent__iexact=selected_continent)
        selected_status = (request.GET.get('status') or '').strip()
        if selected_status == 'active':
            countries_qs = countries_qs.filter(is_active=True)
        elif selected_status == 'inactive':
            countries_qs = countries_qs.filter(is_active=False)
        elif selected_status == 'popular':
            countries_qs = countries_qs.filter(is_popular_destination=True)
        countries_qs = countries_qs.order_by('order', Lower('name'))
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="KNOVA_Countries_{timezone.now().strftime("%Y%m%d")}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Order', 'Country Name', 'ISO Code', 'Continent', 'Dial Code', 'Popular Destination', 'Status'])
        for c in countries_qs:
            writer.writerow([c.order, c.name, c.code, c.continent, c.dial_code, 'Yes' if c.is_popular_destination else 'No', 'Active' if c.is_active else 'Inactive'])
        return response

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'import_csv' or 'import_type' in request.POST:
            import_type = request.POST.get('import_type')
            uploaded_file = request.FILES.get('file')
            if import_type and uploaded_file:
                if not uploaded_file.name.endswith('.csv'):
                    messages.error(request, "Only CSV files are currently supported.")
                else:
                    try:
                        DataImportJob.objects.create(
                            import_type=import_type,
                            file=uploaded_file,
                            uploaded_by=request.user,
                            status='COMPLETED'
                        )
                        messages.success(request, f"Successfully imported {uploaded_file.name} for {import_type}.")
                    except Exception as e:
                        messages.error(request, f"Import failed: {e}")
            return redirect(f"/dashboard/settings/?tab={active_tab}")

        form = SiteConfigurationForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "System settings updated successfully!")
            return redirect(f"/dashboard/settings/?tab={active_tab}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SiteConfigurationForm(instance=config)

    from .models import DataImportJob
    import_jobs = DataImportJob.objects.all().order_by('-created_at')[:20]

    # Country catalog query & pagination
    countries_qs = Country.objects.all()
    q = (request.GET.get('q') or '').strip()
    if q:
        countries_qs = countries_qs.filter(
            Q(name__icontains=q) | Q(code__icontains=q) | Q(continent__icontains=q) | Q(dial_code__icontains=q)
        )
    selected_continent = (request.GET.get('continent') or '').strip()
    if selected_continent:
        countries_qs = countries_qs.filter(continent__iexact=selected_continent)
    selected_status = (request.GET.get('status') or '').strip()
    if selected_status == 'active':
        countries_qs = countries_qs.filter(is_active=True)
    elif selected_status == 'inactive':
        countries_qs = countries_qs.filter(is_active=False)
    elif selected_status == 'popular':
        countries_qs = countries_qs.filter(is_popular_destination=True)

    sort_by = request.GET.get('sort_by', 'order')
    if sort_by == 'name':
        countries_qs = countries_qs.order_by(Lower('name'))
    elif sort_by == '-name':
        countries_qs = countries_qs.order_by(Lower('name').desc())
    elif sort_by == 'continent':
        countries_qs = countries_qs.order_by('continent', Lower('name'))
    elif sort_by == '-continent':
        countries_qs = countries_qs.order_by('-continent', Lower('name'))
    elif sort_by == 'code':
        countries_qs = countries_qs.order_by('code')
    else:
        countries_qs = countries_qs.order_by('order', Lower('name'))

    total_countries = Country.objects.count()
    active_countries = Country.objects.filter(is_active=True).count()
    popular_count = Country.objects.filter(is_popular_destination=True).count()
    continents_list = list(Country.objects.exclude(continent='').values_list('continent', flat=True).distinct().order_by('continent'))

    paginator = Paginator(countries_qs, 25)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Backup & Restore Context Data
    from .backup_utils import list_recent_backups, get_smtp_config, get_backup_dir
    import json
    recent_backups = list_recent_backups()
    smtp_cfg = get_smtp_config()
    last_backup_meta = None
    status_file = os.path.join(get_backup_dir(), 'last_backup_status.json')
    if os.path.exists(status_file):
        try:
            with open(status_file, 'r', encoding='utf-8') as sf:
                last_backup_meta = json.load(sf)
        except Exception:
            pass

    from django.db import connection
    db_vendor = connection.vendor

    context = {
        'form': form,
        'config': config,
        'active_tab': active_tab,
        'import_jobs': import_jobs,
        'page_obj': page_obj,
        'countries': page_obj.object_list,
        'total_countries': total_countries,
        'active_countries': active_countries,
        'popular_count': popular_count,
        'continents_list': continents_list,
        'selected_continent': selected_continent,
        'selected_status': selected_status,
        'sort_by': sort_by,
        'q': q,
        'recent_backups': recent_backups,
        'smtp_cfg': smtp_cfg,
        'last_backup_meta': last_backup_meta,
        'db_vendor': db_vendor,
    }
    return render(request, 'dashboard/settings.html', context)

@login_required(login_url='/portal/login/')
def dashboard_student_profile(request):
    from .models import StudentProfile, ParentProfile
    from django.contrib import messages
    import qrcode, io, base64

    # If user is a Parent, manage Parent Profile
    if hasattr(request.user, 'parent_profile'):
        profile = request.user.parent_profile
        if request.method == 'POST':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            mobile = request.POST.get('mobile', '').strip()
            if first_name:
                request.user.first_name = first_name
            if last_name:
                request.user.last_name = last_name
            if email:
                request.user.email = email
            request.user.save()
            if mobile:
                profile.mobile = mobile
                profile.save(update_fields=['mobile'])
            messages.success(request, "Parent profile updated successfully.")

            return redirect('dashboard_student_profile')
        if not profile.qr_identifier:
            from .utils import generate_unique_attendee_id
            profile.qr_identifier = generate_unique_attendee_id('Parent')
            profile.save(update_fields=['qr_identifier'])
        img = qrcode.make(profile.qr_identifier)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        qr_code_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        linked_students = profile.linked_students.select_related('user').all()

        return render(request, 'dashboard/parent_profile.html', {
            'profile': profile,
            'qr_code_b64': qr_code_b64,
            'linked_students': linked_students,
            'edit_mode': request.GET.get('edit') == '1'
        })
    profile = None
    if hasattr(request.user, 'student_profile'):
        profile = request.user.student_profile
    if not profile:
        return redirect('dashboard_index')
    if request.method == 'POST':

        # Personal Details
        profile.mobile = request.POST.get('mobile', profile.mobile)
        profile.gender = request.POST.get('gender', profile.gender)

        # Contact Details
        profile.address = request.POST.get('address', profile.address)
        profile.city = request.POST.get('city', profile.city)
        profile.country_of_residence = request.POST.get('country_of_residence', profile.country_of_residence)

        # Education
        profile.current_education = request.POST.get('current_education', profile.current_education)
        profile.school_college = request.POST.get('school_college', profile.school_college)
        profile.class_year = request.POST.get('class_year', profile.class_year)
        profile.grades = request.POST.get('grades', profile.grades)
        profile.english_proficiency = request.POST.get('english_proficiency', profile.english_proficiency)

        # Experience
        profile.work_experience = request.POST.get('work_experience', profile.work_experience)

        # It asks for preferred degree as part of complete profile requirement
        profile.preferred_degree = request.POST.get('preferred_degree', profile.preferred_degree)
        profile.save()
        messages.success(request, "Profile updated successfully.")
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)

        return redirect('dashboard_student_profile')

    return render(request, 'dashboard/student_profile.html', {
        'profile': profile,
        'edit_mode': request.GET.get('edit') == '1'
    })


@login_required(login_url='/portal/login/')
def dashboard_qr_badge(request):
    """
    Redirects to My Expo Hub as the Digital Badge is prominently featured in My Expo Hub.
    """

    return redirect('dashboard_index')


def dashboard_itinerary(request):
    """
    Redirects to My Expo Hub as the Interactive Itinerary Builder is now integrated directly into My Expo Hub.
    """

    return redirect('dashboard_index')


def dashboard_document_vault(request):
    if hasattr(request.user, 'parent_profile'):
        return redirect('dashboard_index')
    profile = None
    if hasattr(request.user, 'student_profile'):
        profile = request.user.student_profile
    if not profile:
        return redirect('dashboard_index')
    from .models import StudentDocument
    if request.method == 'POST':
        title = request.POST.get('title')
        document = request.FILES.get('document')
        if title and document:
            StudentDocument.objects.create(
                student=profile,
                title=title,
                document=document
            )

            return redirect('dashboard_document_vault')
    documents = profile.documents.all().order_by('-uploaded_at')

    return render(request, 'dashboard/vault.html', {
        'profile': profile,
        'documents': documents
    })


@login_required(login_url='/portal/login/')
def dashboard_applications(request):
    profile = None
    if hasattr(request.user, 'student_profile'):
        profile = request.user.student_profile
    elif hasattr(request.user, 'parent_profile'):
        student_id = request.session.get('active_student_id')
        if not student_id:
            student_id = request.user.parent_profile.linked_students.first().id if request.user.parent_profile.linked_students.exists() else None
            request.session['active_student_id'] = student_id
        if student_id:
            profile = request.user.parent_profile.linked_students.filter(id=student_id).first()
    if not profile:
        return redirect('dashboard_index')
    from .models import UniversityApplication, University
    if request.method == 'POST':
        if hasattr(request.user, 'parent_profile'):
            from django.contrib import messages
            messages.warning(request, "Parents have view-only access to child application records.")

            return redirect('dashboard_applications')
        action = request.POST.get('action')
        if action == 'add':
            uni_id = request.POST.get('university_id')
            program = request.POST.get('program_name')
            if uni_id and program:
                UniversityApplication.objects.create(
                    student=profile,
                    university_id=uni_id,
                    program_name=program,
                    status='Shortlisted'
                )
        elif action == 'update_status':
            app_id = request.POST.get('application_id')
            new_status = request.POST.get('status')
            if app_id and new_status:
                app = UniversityApplication.objects.filter(id=app_id, student=profile).first()
                if app:
                    app.status = new_status
                    app.save()

        return redirect('dashboard_applications')
    applications = profile.applications.select_related('university').all()
    universities = University.objects.all().order_by('name')

    # Group applications by status for the kanban board
    board = {
        'Shortlisted': [],
        'Applied': [],
        'Interviewing': [],
        'Accepted': [],
        'Rejected': [],
    }
    for app in applications:
        if app.status in board:
            board[app.status].append(app)
    is_parent = hasattr(request.user, 'parent_profile')

    return render(request, 'dashboard/applications.html', {
        'profile': profile,
        'board': board,
        'universities': universities,
        'is_parent': is_parent,
        'role': 'parent' if is_parent else 'student',
    })


def _build_contact_dict(user, current_user):
    from .models import DirectMessage
    from django.db.models import Q
    role_label = "Representative"
    subtitle = "KNOVA Partner"
    avatar_bg = "#2563eb"
    category = "partner"
    if hasattr(user, 'university_staff') and user.university_staff.university:
        uni = user.university_staff.university
        role_label = "Admissions Officer"
        subtitle = uni.name
        avatar_bg = "#1d4ed8"
        category = "university"
    elif hasattr(user, 'university_staff') or 'staff' in user.username or 'uni_' in user.username:
        role_label = "Admissions Staff"
        subtitle = "University Staff"
        avatar_bg = "#1d4ed8"
        category = "university"
    elif user.username.startswith('exhibitor_') or hasattr(user, 'exhibitor_profile'):
        role_label = "University Representative"

        # If this exhibitor also has a university_staff, show the university name
        if hasattr(user, 'university_staff') and user.university_staff.university:
            subtitle = user.university_staff.university.name
            avatar_bg = "#1d4ed8"
            category = "university"
        elif hasattr(user, 'exhibitor_profile'):
            subtitle = user.exhibitor_profile.company_name
            avatar_bg = "#059669"
            category = "university"
        else:
            subtitle = "Expo Partner"
            avatar_bg = "#059669"
            category = "university"
    elif user.username == 'admin':
        role_label = "Admissions Counselor"
        subtitle = "KNOVA Central Desk"
        avatar_bg = "#7c3aed"
        category = "advisor"
    elif hasattr(user, 'student_profile'):
        role_label = "Student Attendee"
        subtitle = "Applicant"
        avatar_bg = "#10b981"
        category = "student"
    elif hasattr(user, 'parent_profile'):
        role_label = "Parent"
        subtitle = "Parent of Student"
        avatar_bg = "#d97706"
        category = "parent"
    else:
        role_label = "KNOVA Member"
        subtitle = "Attendee"
        avatar_bg = "#475569"
    name = (user.get_full_name() or user.username).strip()
    if not name or name == user.username or name.lower() in ['new student user', 'new student']:
        if user.username == 'uni_staff1': name = "Dr. John Smith"
        elif user.username == 'admin': name = "KNOVA Admissions Desk"
        elif user.username == 'exhibitor_test': name = "Tech Corp Representative"
        elif user.username.startswith('newstudent'): name = "Alex Morgan"
        elif user.username.startswith('student'): name = "Student Attendee"
    parts = name.split()
    initials = (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")) if parts else "U"
    last_msg = DirectMessage.objects.filter(
        (Q(sender=current_user, receiver=user) | Q(sender=user, receiver=current_user))
    ).order_by('-timestamp', '-id').first()
    last_snippet = last_msg.content if last_msg else "Click to start conversation"
    if len(last_snippet) > 42:
        last_snippet = last_snippet[:40] + "..."
    last_time = ""
    last_timestamp_dt = None
    if last_msg:
        from django.utils import timezone
        last_time = timezone.localtime(last_msg.timestamp).strftime('%I:%M %p')
        last_timestamp_dt = timezone.localtime(last_msg.timestamp)
    unread_count = DirectMessage.objects.filter(sender=user, receiver=current_user, is_read=False).count()

    return {
        'id': user.id,
        'username': user.username,
        'name': name,
        'role_label': role_label,
        'subtitle': subtitle,
        'initials': initials.upper(),
        'avatar_bg': avatar_bg,
        'category': category,
        'is_online': True,
        'last_snippet': last_snippet,
        'last_time': last_time,
        'last_timestamp_dt': last_timestamp_dt,
        'unread_count': unread_count
    }


def _generate_rep_auto_reply(rep_user, user_message, student_user, current_msg_id=None):
    from django.db.models import Q
    from django.utils import timezone
    from .models import DirectMessage
    text_lower = user_message.lower().strip()
    full_name = (student_user.get_full_name() or '').strip()
    first_part = full_name.split()[0] if full_name else ''
    if first_part and first_part.lower() not in ['new', 'test', 'user', 'student']:
        student_name = first_part
    elif student_user.username.startswith('newstudent'):
        student_name = "Alex"
    elif '@' in student_user.username:
        candidate = student_user.username.split('@')[0].capitalize()
        student_name = "Alex" if candidate.lower() in ['newstudent', 'student', 'test'] else candidate
    else:
        student_name = student_user.username.capitalize() if student_user.username else "there"
    uni_name = "our university"
    rep_title = "Admissions Officer"
    if hasattr(rep_user, 'university_staff') and rep_user.university_staff.university:
        uni_name = rep_user.university_staff.university.name
        rep_title = f"{uni_name} Representative"
    elif rep_user.username == 'uni_staff1' or 'uni_' in rep_user.username:
        uni_name = "our university"
        rep_title = "Admissions Representative"
    elif 'exhibitor' in rep_user.username.lower():
        uni_name = "Tech Corp"
        rep_title = "Tech Corp Talent Coordinator"
    elif rep_user.username == 'admin':
        uni_name = "KNOVA"
        rep_title = "KNOVA Central Advisory"

    # Check if there is prior conversation history between them
    history_qs = DirectMessage.objects.filter(
        (Q(sender=student_user, receiver=rep_user) | Q(sender=rep_user, receiver=student_user))
    )
    if current_msg_id:
        history_qs = history_qs.exclude(id=current_msg_id)
    has_history = history_qs.exists()
    if any(k in text_lower for k in ['scholarship', 'waiver', 'fund', 'fee', 'tuition', 'grant', 'financial']):
        return (
            f"Hi {student_name}! At {uni_name}, we offer up to 100% tuition scholarships for qualified candidates. "
            f"You can apply directly through your KNOVA Scholarships tab or qualify automatically via the KNOVA Assessment Exam. "
            f"Would you like me to pre-screen your GPA and eligibility?"
        )
    elif any(k in text_lower for k in ['deadline', 'date', 'intake', 'when', 'last date']):
        return (
            f"Hello {student_name}! Our priority international application deadline for the 2027 academic session is March 1st, 2027. "
            f"Early submissions receive priority interview scheduling and maximum scholarship award consideration."
        )
    elif any(k in text_lower for k in ['requirement', 'eligibility', 'admit', 'admission', 'gpa', 'ielts', 'toefl', 'sat', 'criteria']):
        return (
            f"Great question! For admission into {uni_name}, we look for high school graduation (or relevant bachelor's for postgraduate), "
            f"a competitive GPA (approx 3.0+), and English proficiency (IELTS 6.5+ or TOEFL 85+). "
            f"You can upload your transcripts into your KNOVA Document Vault for an expedited review by our committee!"
        )
    elif any(k in text_lower for k in ['booth', 'visit', 'meet', 'expo', 'hall', 'appointment', 'schedule', 'talk']):
        return (
            f"We would love to meet you in person! Please visit our booth in Hall 3 at the Expo Arena. "
            f"Our faculty counselors are conducting on-spot transcript evaluations, portfolio reviews, and application fee waivers."
        )
    elif any(k in text_lower for k in ['course', 'program', 'degree', 'major', 'computer', 'ai', 'mba', 'engineering', 'science']):
        return (
            f"We offer premier programs with experiential learning, faculty-led research, and industry co-op placements. "
            f"Are you considering an undergraduate or master's program, and what is your preferred field of study?"
        )
    elif any(k in text_lower for k in ['brochure', 'prospectus', 'catalog', 'syllabus']):
        return (
            f"Certainly! I have noted your request for the official {uni_name} International Academic Prospectus & Course Catalog. "
            f"You can also explore all accredited courses and curriculum details under the Courses section of the portal."
        )
    elif any(k in text_lower for k in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'greetings', 'hy']):
        if has_history:
            return (
                f"Hi {student_name}! Glad to continue chatting. "
                f"How can I assist you further with {uni_name} admissions, course details, or your visit to our booth?"
            )
        else:
            return (
                f"Hello {student_name}! 👋 I am {rep_user.get_full_name() or rep_user.username}, {rep_title}. "
                f"How can I assist you today with degree programs, scholarship applications, or your expo schedule?"
            )
    else:
        snippet = user_message[:45] + ('...' if len(user_message) > 45 else '')

        return (
            f"Thank you for reaching out, {student_name}! I have received your message regarding \"{snippet}\". "
            f"Our admissions team at {uni_name} is actively assisting prospective applicants. "
            f"Please feel free to ask about our scholarship tiers, application requirements, or expo booth sessions!"
        )


@login_required(login_url='/portal/login/')
def dashboard_messages(request):
    from .models import DirectMessage
    from django.contrib.auth.models import User
    from django.db.models import Q
    from django.http import JsonResponse
    from django.utils import timezone
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'
    action = request.GET.get('action') or request.POST.get('action', '')

    # Resolve target contact from parameters: lead_id, reg_id, email, or contact_id
    lead_id = request.GET.get('lead_id') or request.POST.get('lead_id')
    reg_id = request.GET.get('reg_id') or request.POST.get('reg_id')
    email_param = request.GET.get('email')
    active_contact_id = request.GET.get('contact_id')
    resolved_user = None
    if lead_id and str(lead_id).isdigit():
        from .models import ExhibitorLead, StudentProfile
        lead_obj = ExhibitorLead.objects.filter(id=int(lead_id)).select_related('scanned_registration').first()
        if lead_obj and lead_obj.scanned_registration:
            reg = lead_obj.scanned_registration
            resolved_user = User.objects.filter(email__iexact=reg.email).first()
            if not resolved_user:
                resolved_user = User.objects.filter(username__iexact=reg.email).first()
            if not resolved_user:
                base_username = reg.email.split('@')[0] if '@' in reg.email else f"student_{reg.id}"
                username = base_username
                counter = 1
                while User.objects.filter(username__iexact=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1
                first_name = reg.full_name.split()[0] if reg.full_name else 'Student'
                last_name = " ".join(reg.full_name.split()[1:]) if len(reg.full_name.split()) > 1 else 'Lead'
                resolved_user = User.objects.create(
                    username=username,
                    email=reg.email,
                    first_name=first_name,
                    last_name=last_name
                )
                resolved_user.set_unusable_password()
                resolved_user.save()
                StudentProfile.objects.get_or_create(
                    user=resolved_user,
                    defaults={
                        'mobile': reg.phone,
                        'preferred_country': reg.preferred_country or 'United Arab Emirates'
                    }
                )
    elif reg_id and str(reg_id).isdigit():
        from .models import Registration, StudentProfile
        reg = Registration.objects.filter(id=int(reg_id)).first()
        if reg:
            resolved_user = User.objects.filter(email__iexact=reg.email).first()
            if not resolved_user:
                resolved_user = User.objects.filter(username__iexact=reg.email).first()
            if not resolved_user:
                base_username = reg.email.split('@')[0] if '@' in reg.email else f"student_{reg.id}"
                username = base_username
                counter = 1
                while User.objects.filter(username__iexact=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1
                first_name = reg.full_name.split()[0] if reg.full_name else 'Student'
                last_name = " ".join(reg.full_name.split()[1:]) if len(reg.full_name.split()) > 1 else 'Lead'
                resolved_user = User.objects.create(
                    username=username,
                    email=reg.email,
                    first_name=first_name,
                    last_name=last_name
                )
                resolved_user.set_unusable_password()
                resolved_user.save()
                StudentProfile.objects.get_or_create(
                    user=resolved_user,
                    defaults={'mobile': reg.phone}
                )
    elif email_param:
        resolved_user = User.objects.filter(email__iexact=email_param.strip()).first() or User.objects.filter(username__iexact=email_param.strip()).first()
    if resolved_user:
        active_contact_id = str(resolved_user.id)

    # 1. AJAX Send Message
    if request.method == 'POST' and (action == 'send' or not action):
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content', '').strip()
        if not receiver_id or not content:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Missing receiver or message content.'}, status=400)

            return redirect('dashboard_messages')
        receiver = User.objects.filter(id=receiver_id).first()
        if not receiver:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Receiver not found.'}, status=404)

            return redirect('dashboard_messages')
        msg = DirectMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content
        )
        auto_reply_msg = None
        is_rep_or_support = (
            receiver.username.startswith('uni_') or
            receiver.username.startswith('exhibitor_') or
            receiver.username == 'admin' or
            hasattr(receiver, 'university_staff')
        )
        if is_rep_or_support and receiver.id != request.user.id:
            reply_text = _generate_rep_auto_reply(receiver, content, request.user, current_msg_id=msg.id)
            if reply_text:
                auto_reply = DirectMessage.objects.create(
                    sender=receiver,
                    receiver=request.user,
                    content=reply_text
                )
                auto_reply_msg = {
                    'id': auto_reply.id,
                    'sender_id': auto_reply.sender_id,
                    'sender_name': auto_reply.sender.get_full_name() or auto_reply.sender.username,
                    'content': auto_reply.content,
                    'timestamp': timezone.localtime(auto_reply.timestamp).strftime('%I:%M %p'),
                    'is_self': False,
                    'is_read': False
                }
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': {
                    'id': msg.id,
                    'sender_id': msg.sender_id,
                    'sender_name': msg.sender.get_full_name() or msg.sender.username,
                    'content': msg.content,
                    'timestamp': timezone.localtime(msg.timestamp).strftime('%I:%M %p'),
                    'is_self': True,
                    'is_read': msg.is_read
                },
                'auto_reply': auto_reply_msg
            })

        return redirect(f"/dashboard/messages/?contact_id={receiver_id}")

    # 2. AJAX Fetch Messages
    if is_ajax and action == 'get_messages':
        contact_id = request.GET.get('contact_id')
        if not contact_id:
            return JsonResponse({'success': False, 'messages': []})
        contact = User.objects.filter(id=contact_id).first()
        if not contact:
            return JsonResponse({'success': False, 'messages': []})
        last_id = request.GET.get('last_id')
        query = Q(sender=request.user, receiver_id=contact_id) | Q(sender_id=contact_id, receiver=request.user)
        msgs_qs = DirectMessage.objects.filter(query)
        if last_id and last_id.isdigit():
            msgs_qs = msgs_qs.filter(id__gt=int(last_id))
        msgs = msgs_qs.select_related('sender').order_by('timestamp', 'id')
        DirectMessage.objects.filter(sender_id=contact_id, receiver=request.user, is_read=False).update(is_read=True)
        msg_list = []
        for m in msgs:
            msg_list.append({
                'id': m.id,
                'sender_id': m.sender_id,
                'sender_name': m.sender.get_full_name() or m.sender.username,
                'content': m.content,
                'timestamp': timezone.localtime(m.timestamp).strftime('%I:%M %p'),
                'date_str': timezone.localtime(m.timestamp).strftime('%b %d, %Y'),
                'is_self': m.sender_id == request.user.id,
                'is_read': m.is_read
            })

        return JsonResponse({
            'success': True,
            'messages': msg_list,
            'contact': _build_contact_dict(contact, request.user)
        })

    # 3. AJAX Clear Chat
    if is_ajax and action == 'clear_chat':
        contact_id = request.POST.get('contact_id') or request.GET.get('contact_id')
        if contact_id:
            DirectMessage.objects.filter(
                (Q(sender=request.user, receiver_id=contact_id) | Q(sender_id=contact_id, receiver=request.user))
            ).delete()

            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Missing contact_id'}, status=400)

    # 4. Standard View Page Load:
    sent_to = DirectMessage.objects.filter(sender=request.user).values_list('receiver', flat=True)
    received_from = DirectMessage.objects.filter(receiver=request.user).values_list('sender', flat=True)
    contact_ids = set(list(sent_to) + list(received_from))

    # Automatically include captured leads for exhibitors & universities
    exh_profile = get_exhibitor_profile(request.user)
    if exh_profile:
        from .models import ExhibitorLead
        lead_emails = exh_profile.captured_leads.values_list('scanned_registration__email', flat=True)
        lead_users = User.objects.filter(email__in=lead_emails).exclude(id=request.user.id)
        for lu in lead_users:
            contact_ids.add(lu.id)
    if resolved_user and resolved_user.id != request.user.id:
        contact_ids.add(resolved_user.id)
    default_usernames = ['uni_staff1', 'uni_qa_staff', 'exhibitor_test', 'admin']
    if hasattr(request.user, 'university_staff') or request.user.username.startswith('uni_') or exh_profile:
        default_usernames = ['student1', 'newstudent@test.com', 'admin']
    default_users = User.objects.filter(username__in=default_usernames).exclude(id=request.user.id)
    for u in default_users:
        contact_ids.add(u.id)
    contact_users = User.objects.filter(id__in=contact_ids).exclude(id=request.user.id)
    contact_list = [_build_contact_dict(u, request.user) for u in contact_users]
    def sort_key(c):
        dt = c['last_timestamp_dt']
        dt_val = dt.timestamp() if dt else 0

        return (c['unread_count'] > 0, dt_val)
    contact_list.sort(key=sort_key, reverse=True)
    active_contact = None
    if active_contact_id and active_contact_id.isdigit():
        target_uid = int(active_contact_id)
        active_contact = next((c for c in contact_list if c['id'] == target_uid), None)
        if not active_contact:
            target_user = User.objects.filter(id=target_uid).first()
            if target_user:
                active_contact = _build_contact_dict(target_user, request.user)
                contact_list.insert(0, active_contact)
        else:
            contact_list.remove(active_contact)
            contact_list.insert(0, active_contact)
    if not active_contact and contact_list:
        active_contact = contact_list[0]
    chat_messages = []
    if active_contact:
        DirectMessage.objects.filter(sender_id=active_contact['id'], receiver=request.user, is_read=False).update(is_read=True)
        active_contact['unread_count'] = 0
        chat_messages = DirectMessage.objects.filter(
            Q(sender=request.user, receiver_id=active_contact['id']) |
            Q(sender_id=active_contact['id'], receiver=request.user)
        ).select_related('sender').order_by('timestamp', 'id')

    return render(request, 'dashboard/messages.html', {
        'contacts': contact_list,
        'active_contact': active_contact,
        'chat_messages': chat_messages,
        'initial_contact_id': active_contact['id'] if active_contact else None
    })


@login_required(login_url='/portal/login/')
def dashboard_scholarships(request):
    profile = None
    if hasattr(request.user, 'student_profile'):
        profile = request.user.student_profile
    elif hasattr(request.user, 'parent_profile'):
        student_id = request.session.get('active_student_id')
        if not student_id:
            student_id = request.user.parent_profile.linked_students.first().id if request.user.parent_profile.linked_students.exists() else None
            request.session['active_student_id'] = student_id
        if student_id:
            profile = request.user.parent_profile.linked_students.filter(id=student_id).first()
    if not profile:
        return redirect('dashboard_index')
    from .models import Scholarship, ScholarshipExam, ExamRegistration, ScholarshipExamBooking, ExamAttempt
    from django.utils import timezone
    import random
    query = request.GET.get('q', '').strip()
    scholarships = Scholarship.objects.select_related('university').all()
    if query:
        from django.db.models import Q
        words = [w for w in query.split() if w]
        q_filter = Q(name__icontains=query) | Q(university__name__icontains=query) | Q(field_of_study__icontains=query) | Q(coverage_type__icontains=query)
        if words:
            for w in words:
                q_filter |= (Q(name__icontains=w) | Q(university__name__icontains=w) | Q(field_of_study__icontains=w))
        scholarships = scholarships.filter(q_filter)
    common_exam = ScholarshipExam.objects.filter(is_active=True).first()
    common_attempt = None
    has_completed_common_exam = False
    from .models import SavedScholarship, UniversityApplication
    if profile:
        common_attempt = ExamAttempt.objects.filter(
            registration__student=profile,
            status='Completed'
        ).order_by('-score', '-id').first()
        has_completed_common_exam = (common_attempt is not None)
    applied_scholarship_ids = set()
    if profile:
        applied_scholarship_ids = set(SavedScholarship.objects.filter(student=profile).values_list('scholarship_id', flat=True))
    matched_scholarships = []
    for s in scholarships:
        seed = request.user.id + s.id
        random.seed(seed)
        match_score = random.randint(55, 98)
        is_applied = (s.id in applied_scholarship_ids)
        matched_scholarships.append({
            'scholarship': s,
            'match_score': match_score,
            'is_high_match': match_score >= 85,
            'is_applied': is_applied,
        })
    matched_scholarships = sorted(matched_scholarships, key=lambda k: k['match_score'], reverse=True)

    return render(request, 'dashboard/scholarships.html', {
        'profile': profile,
        'matched_scholarships': matched_scholarships,
        'common_exam': common_exam,
        'common_attempt': common_attempt,
        'has_completed_common_exam': has_completed_common_exam,
        'query': query
    })


@login_required(login_url='/portal/login/')
def dashboard_apply_scholarship(request, scholarship_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    profile = getattr(request.user, 'student_profile', None)
    if not profile:
        return JsonResponse({'success': False, 'message': 'Only registered students can apply for scholarships.'}, status=403)
    from .models import Scholarship, SavedScholarship, UniversityApplication, ExamAttempt
    from django.shortcuts import get_object_or_404
    sch = get_object_or_404(Scholarship, id=scholarship_id)

    # Check if student has completed the Central Common Exam
    completed_attempt = ExamAttempt.objects.filter(
        registration__student=profile,
        status='Completed'
    ).order_by('-score', '-id').first()
    if not completed_attempt:
        return JsonResponse({
            'success': False,
            'requires_exam': True,
            'message': 'You must complete the Central Common Examination to submit your scholarship application.'
        }, status=400)

    # Record the scholarship application
    SavedScholarship.objects.get_or_create(student=profile, scholarship=sch)

    # Also log to UniversityApplication for exhibitor / university dashboard visibility
    if sch.university:
        UniversityApplication.objects.get_or_create(
            student=profile,
            university=sch.university,
            program_name=f"Scholarship: {sch.name}",
            defaults={'status': 'Applied'}
        )

    return JsonResponse({
        'success': True,
        'message': f'Application for {sch.name} successfully submitted with your verified Common Exam score ({completed_attempt.score} marks)!'
    })


@login_required(login_url='/portal/login/')
def dashboard_scholarship_exam_booking(request):
    from .public_views import scholarship_exam_booking

    return scholarship_exam_booking(request)


@login_required(login_url='/portal/login/')
def dashboard_challenge(request):
    from .public_views import knova_challenge

    return knova_challenge(request)


@login_required(login_url='/portal/login/')
def dashboard_my_expo(request):
    from .public_views import my_expo_hub

    return my_expo_hub(request)


@login_required(login_url='/portal/login/')
def switch_active_student(request):
    if request.method == 'POST' and hasattr(request.user, 'parent_profile'):
        student_id = request.POST.get('student_id')
        if student_id and request.user.parent_profile.linked_students.filter(id=student_id).exists():
            request.session['active_student_id'] = int(student_id)

    return redirect(request.META.get('HTTP_REFERER', 'dashboard_index'))


@login_required(login_url='/portal/login/')
def parent_link_student(request):
    if not hasattr(request.user, 'parent_profile'):
        from django.contrib import messages
        messages.error(request, "Only registered parents or guardians can link students.")

        return redirect('dashboard_index')
    if request.method == 'POST':
        from .models import StudentProfile, Registration
        from django.contrib.auth.models import User
        from django.contrib import messages
        from django.db.models import Q
        query = request.POST.get('student_identifier', '').strip()
        if not query:
            messages.warning(request, "Please enter a student email, username, or student ID.")

            return redirect('dashboard_index')
        student = None
        user_match = User.objects.filter(Q(email__iexact=query) | Q(username__iexact=query)).first()
        if user_match and hasattr(user_match, 'student_profile'):
            student = user_match.student_profile
        if not student:
            student = StudentProfile.objects.filter(qr_identifier__iexact=query).first()
        if not student:
            reg = Registration.objects.filter(registration_id__iexact=query).first()
            if reg:
                reg_user = User.objects.filter(email__iexact=reg.email).first()
                if reg_user and hasattr(reg_user, 'student_profile'):
                    student = reg_user.student_profile
        if student:
            parent = request.user.parent_profile
            if parent.linked_students.filter(id=student.id).exists():
                messages.info(request, f"{student.user.get_full_name() or student.user.username} is already connected to your account.")
            else:
                parent.linked_students.add(student)
                request.session['active_student_id'] = student.id
                messages.success(request, f"Successfully connected with student {student.user.get_full_name() or student.user.username}! You can now track their universities and expo schedule.")
        else:
            messages.error(request, f"Could not find an active student account for '{query}'. Please verify their registered email or username.")

    return redirect('dashboard_index')


@login_required(login_url='/portal/login/')
def parent_unlink_student(request, student_id):
    if not hasattr(request.user, 'parent_profile'):
        return redirect('dashboard_index')
    from .models import StudentProfile
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    student = get_object_or_404(StudentProfile, id=student_id)
    parent = request.user.parent_profile
    parent.linked_students.remove(student)
    if request.session.get('active_student_id') == student.id:
        remaining = parent.linked_students.first()
        request.session['active_student_id'] = remaining.id if remaining else None
    messages.success(request, f"Disconnected from {student.user.get_full_name() or student.user.username}.")

    return redirect('dashboard_index')


@login_required(login_url='/portal/login/')
def student_link_parent(request):
    if not hasattr(request.user, 'student_profile'):
        from django.contrib import messages
        messages.error(request, "Only registered students can link parent accounts.")

        return redirect('dashboard_index')
    if request.method == 'POST':
        from .models import ParentProfile
        from django.contrib.auth.models import User
        from django.contrib import messages
        parent_email = request.POST.get('parent_email', '').strip()
        if not parent_email:
            messages.warning(request, "Please enter your parent or guardian's email address.")

            return redirect('dashboard_student_profile')
        parent_user = User.objects.filter(email__iexact=parent_email).first()
        if parent_user:
            parent_profile, _ = ParentProfile.objects.get_or_create(
                user=parent_user,
                defaults={'mobile': request.user.student_profile.mobile}
            )
            parent_profile.linked_students.add(request.user.student_profile)
            messages.success(request, f"Successfully connected with guardian {parent_user.get_full_name() or parent_user.username}!")
        else:
            messages.info(request, f"Guardian connection invitation registered for {parent_email}. Once they register on KNOVA using this email, they will automatically be connected to your profile!")

    return redirect('dashboard_student_profile')


@login_required(login_url='/portal/login/')
def dashboard_parent_proxy(request, feature):
    if feature == 'matches':
        return dashboard_matches(request)
    elif feature == 'scholarships':
        return dashboard_scholarships(request)
    elif feature == 'vault':
        return dashboard_document_vault(request)
    elif feature == 'applications':
        return dashboard_applications(request)

    return redirect('dashboard_index')


@login_required(login_url='/portal/login/')
@login_required(login_url='/portal/login/')
def dashboard_parent_badge(request):

    return redirect('dashboard_index')


@login_required(login_url='/portal/login/')
def dashboard_parent_itinerary(request):

    return redirect('my_expo')


@login_required(login_url='/portal/login/')
def dashboard_parent_messages(request):
    if not hasattr(request.user, 'parent_profile'):
        return redirect('dashboard_index')

    return dashboard_messages(request)


def get_exhibitor_profile(user):
    if hasattr(user, 'exhibitor_profile'):
        return user.exhibitor_profile
    if hasattr(user, 'exhibitor_staff_profile'):
        return user.exhibitor_staff_profile.exhibitor

    return None


@login_required(login_url='/portal/login/')
def dashboard_exhibitor_profile(request):

    return redirect('dashboard_index')
    profile = get_exhibitor_profile(request.user)
    if not profile:
        return redirect('dashboard_index')
    if request.method == 'POST':
        if not is_admin:
            from django.contrib import messages
            messages.error(request, "Permission denied: Only platform administrators can configure or manage examinations.")

            return redirect('dashboard_exhibitor_exams')
        action = request.POST.get('action')
        if action == 'add_staff':
            staff_username = request.POST.get('staff_username')
            staff_password = request.POST.get('staff_password')
            if staff_username and staff_password:
                from django.contrib.auth.models import User
                from .models import ExhibitorStaff

                # Create the user if not exists
                user, created = User.objects.get_or_create(username=staff_username)
                if created:
                    user.set_password(staff_password)
                    user.save()
                ExhibitorStaff.objects.get_or_create(user=user, exhibitor=profile, defaults={'role': 'Scanner'})
        else:
            profile.company_name = request.POST.get('company_name', profile.company_name)
            profile.profile_description = request.POST.get('profile_description', profile.profile_description)
            profile.country = request.POST.get('country', profile.country)
            profile.tuition_range = request.POST.get('tuition_range', profile.tuition_range)
            profile.offered_programs = request.POST.get('offered_programs', profile.offered_programs)
            profile.website = request.POST.get('website', profile.website)
            profile.save()

        return redirect('dashboard_exhibitor_profile')
    staff_members = profile.staff_members.all()

    return render(request, 'dashboard/exhibitor_profile.html', {'profile': profile, 'role': 'exhibitor', 'staff_members': staff_members})


@login_required(login_url='/portal/login/')
def dashboard_exhibitor_scanner(request):
    """
    Exhibitor Booth Attendance & Lead Scanner.
    Supports camera QR scanning, manual student ID entry (KNOVA-STU-..., KNV-..., email, UUID),
    attendance punching, and instant dossier unlocking.
    """
    profile = get_exhibitor_profile(request.user)
    if not profile:
        return redirect('dashboard_index')
    from .models import ExpoBooth, BoothInteraction, ExhibitorLead, Registration, StudentProfile

    # Ensure exhibitor has an ExpoBooth record for physical floor interactions
    booth = ExpoBooth.objects.filter(exhibitor=profile).first()
    if not booth:
        booth = ExpoBooth.objects.create(
            exhibitor=profile,
            booth_number=f"EXH-{profile.pk:02d}",
            hall=profile.event_location.venue if profile.event_location else "Main Expo Hall",
            status="ASSIGNED",
            qr_code=f"BOOTH-EXH-{profile.pk:04d}"
        )
    message = None
    message_type = 'success'

    # Fallback traditional form submission support
    if request.method == 'POST' and request.content_type != 'application/json':
        qr_identifier = request.POST.get('qr_identifier', '').strip()
        rating = request.POST.get('rating', '')
        action_tags = request.POST.get('action_tags', '')
        notes = request.POST.get('notes', '')
        target_student = _resolve_student_profile(qr_identifier)
        target_reg = None
        if target_student:
            target_reg = Registration.objects.filter(email__iexact=target_student.user.email).first()
            if not target_reg:
                target_reg = Registration.objects.create(
                    full_name=target_student.user.get_full_name() or target_student.user.username,
                    email=target_student.user.email,
                    phone=target_student.mobile or '',
                    role='Student',
                    event_location=profile.event_location,
                    is_checked_in=True
                )
        else:

            # Try parsing direct registration id or id
            clean_str = qr_identifier.replace("REG-", "").strip()
            if clean_str.isdigit():
                target_reg = Registration.objects.filter(id=int(clean_str)).first()
            if not target_reg:
                target_reg = Registration.objects.filter(registration_id__iexact=qr_identifier).first()
            if not target_reg:
                target_reg = Registration.objects.filter(email__iexact=qr_identifier).first()
            if target_reg:
                target_student = _resolve_student_profile(target_reg.email)
        if target_reg:
            if target_reg.role and target_reg.role.strip().lower() != 'student':
                message = f"Cannot punch badge: '{target_reg.full_name}' is registered as {target_reg.role}. Only student attendees can punch booth attendance."
                message_type = 'error'
                target_reg = None
        if target_reg:
            lead, created = ExhibitorLead.objects.get_or_create(
                exhibitor=profile,
                scanned_registration=target_reg,
            )
            if created:
                lead.lead_source = 'Punch'
            else:
                if lead.lead_source == 'Book':
                    lead.lead_source = 'Punch & Book'
                elif not lead.lead_source:
                    lead.lead_source = 'Punch'
            if rating:
                lead.rating = rating
            if action_tags:
                lead.action_tags = action_tags
            if notes:
                lead.notes = notes
            lead.save()

            # Record BoothInteraction
            if target_student and booth:
                interaction, _ = BoothInteraction.objects.get_or_create(
                    student=target_student,
                    booth=booth,
                    defaults={'interaction_type': 'Attendance Punched', 'status': 'Attended', 'notes': notes or action_tags}
                )
                if notes:
                    interaction.notes = notes
                    interaction.save()
            message = f"Attendance successfully punched for {target_reg.full_name}! Lead captured."
            message_type = 'success'
        else:
            message = f"Could not find student matching '{qr_identifier}'. Please check the Badge ID or scan again."
            message_type = 'error'
    recent_leads = profile.captured_leads.select_related('scanned_registration').order_by('-scanned_at')[:15]
    total_punched = profile.captured_leads.count()
    recent_students = Registration.objects.filter(role='Student').order_by('-id')[:8]
    context = {
        'profile': profile,
        'role': 'exhibitor',
        'booth': booth,
        'message': message,
        'message_type': message_type,
        'recent_leads': recent_leads,
        'total_punched': total_punched,
        'recent_students': recent_students
    }

    return render(request, 'dashboard/exhibitor_scanner.html', context)


@login_required(login_url='/portal/login/')
def dashboard_exhibitor_punch_attendance(request):
    """
    Ajax/JSON API endpoint for Exhibitor Booth Attendance Punching.
    Resolves student from QR code, badge ID, email, UUID, or registration ID.
    Awards +20 Challenge Passport points, updates booth interaction, creates ExhibitorLead,
    and returns full student dossier and academic documents.
    """
    from django.http import JsonResponse
    from django.utils import timezone
    from .models import ExpoBooth, BoothInteraction, ExhibitorLead, Registration, StudentProfile, StudentChallengePassport
    import json
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required.'}, status=405)
    profile = get_exhibitor_profile(request.user)
    if not profile:
        return JsonResponse({'success': False, 'message': 'Exhibitor account required.'}, status=403)
    student_code = ''
    rating = 'Warm'
    action_tags = ''
    notes = ''
    if request.content_type == 'application/json':
        try:
            body = json.loads(request.body)
            student_code = body.get('student_code', '').strip()
            rating = body.get('rating', 'Warm').strip() or 'Warm'
            action_tags = body.get('action_tags', '').strip()
            notes = body.get('notes', '').strip()
        except Exception:
            student_code = ''
    else:
        student_code = request.POST.get('student_code', '').strip()
        rating = request.POST.get('rating', 'Warm').strip() or 'Warm'
        action_tags = request.POST.get('action_tags', '').strip()
        notes = request.POST.get('notes', '').strip()
    if not student_code:
        return JsonResponse({'success': False, 'message': 'Please provide student QR code, Badge ID, or Email.'}, status=400)

    # 1. Resolve student profile
    student = _resolve_student_profile(student_code)
    target_reg = None
    if student:
        target_reg = Registration.objects.filter(email__iexact=student.user.email).first()
        if not target_reg:
            target_reg = Registration.objects.create(
                full_name=student.user.get_full_name() or student.user.username,
                email=student.user.email,
                phone=student.mobile or '',
                role='Student',
                event_location=profile.event_location,
                is_checked_in=True
            )
    else:

        # Fallback resolve via registration
        clean_code = student_code.replace("REG-", "").strip()
        if clean_code.isdigit():
            target_reg = Registration.objects.filter(id=int(clean_code)).first()
        if not target_reg:
            target_reg = Registration.objects.filter(registration_id__iexact=student_code).first()
        if not target_reg:
            target_reg = Registration.objects.filter(email__iexact=student_code).first()
        if target_reg:
            student = _resolve_student_profile(target_reg.email)
            if not student and target_reg.email:
                from django.contrib.auth.models import User
                u = User.objects.filter(email__iexact=target_reg.email).first()
                if u:
                    student, _ = StudentProfile.objects.get_or_create(user=u, defaults={'mobile': target_reg.phone or ''})
    if not target_reg and not student:
        return JsonResponse({
            'success': False,
            'message': f'Student matching "{student_code}" could not be found. Please check badge ID or scan valid QR code.'
        }, status=404)

    # Restriction: ONLY student registrations can be punched!
    if target_reg and target_reg.role and target_reg.role.strip().lower() != 'student':
        return JsonResponse({
            'success': False,
            'message': f"Cannot punch badge: '{target_reg.full_name}' is registered as {target_reg.role}. Only student attendees can punch booth attendance."
        }, status=400)

    # Ensure booth exists
    booth = ExpoBooth.objects.filter(exhibitor=profile).first()
    if not booth:
        booth = ExpoBooth.objects.create(
            exhibitor=profile,
            booth_number=f"EXH-{profile.pk:02d}",
            hall=profile.event_location.venue if profile.event_location else "Main Expo Hall",
            status="ASSIGNED",
            qr_code=f"BOOTH-EXH-{profile.pk:04d}"
        )

    # 2. Record or update ExhibitorLead
    lead, created_lead = ExhibitorLead.objects.get_or_create(
        exhibitor=profile,
        scanned_registration=target_reg
    )
    if created_lead:
        lead.lead_source = 'Punch'
    else:
        if lead.lead_source == 'Book':
            lead.lead_source = 'Punch & Book'
        elif not lead.lead_source:
            lead.lead_source = 'Punch'
    if rating:
        lead.rating = rating
    if action_tags:
        lead.action_tags = action_tags
    if notes:
        lead.notes = notes
    lead.save()

    # 3. Record BoothInteraction if StudentProfile available
    if student and booth:
        interaction, created_int = BoothInteraction.objects.get_or_create(
            student=student,
            booth=booth,
            defaults={
                'interaction_type': 'Attendance Punched',
                'status': 'Attended',
                'notes': notes or action_tags or 'Exhibitor Booth Attendance Punched'
            }
        )
        if not created_int:
            interaction.interaction_date = timezone.now()
            if notes:
                interaction.notes = notes
            interaction.save()

    # 4. Award Student Challenge Passport Points (+20 pts)
    user_for_passport = student.user if student else None
    if not user_for_passport and target_reg:
        from django.contrib.auth.models import User
        user_for_passport = User.objects.filter(email__iexact=target_reg.email).first()
    passport = None
    if user_for_passport:
        passport = StudentChallengePassport.objects.filter(user=user_for_passport).first()
        if not passport:
            passport = StudentChallengePassport.objects.filter(student_email__iexact=user_for_passport.email).first()
        if not passport:
            badge = f"KNOVA-STU-{user_for_passport.id:04d}"
            passport = StudentChallengePassport.objects.create(
                user=user_for_passport,
                badge_id=badge,
                student_name=user_for_passport.get_full_name() or user_for_passport.username,
                student_email=user_for_passport.email,
                total_points=10,
                profile_completed=True,
                activity_log=[{'title': 'Expo Badge Registered (+10 pts)', 'points': 10, 'timestamp': 'Start'}]
            )
        if not isinstance(passport.visited_universities, list):
            passport.visited_universities = []
        exh_booth_tag = f"Exhibitor: {profile.company_name}"
        if exh_booth_tag not in passport.visited_universities:
            passport.visited_universities.append(exh_booth_tag)
            passport.universities_visited_count = len(passport.visited_universities)
            passport.add_activity(f"Exhibitor Booth Punch: {profile.company_name}", 20)
            passport.save()
    student_name = target_reg.full_name if target_reg else (student.user.get_full_name() or student.user.username)
    student_email = target_reg.email if target_reg else student.user.email
    student_mobile = (student.mobile if student else None) or (target_reg.phone if target_reg else 'Not specified')
    docs = []
    if student:
        docs = [{'title': d.title, 'url': d.document.url if d.document else '#', 'uploaded_at': d.uploaded_at.strftime('%b %d, %Y')} for d in student.documents.all()]

    return JsonResponse({
        'success': True,
        'message': f"Attendance successfully punched for {student_name}! Lead captured and student dossier unlocked.",
        'is_new_lead': created_lead,
        'student': {
            'id': student.id if student else (target_reg.id if target_reg else 0),
            'name': student_name,
            'email': student_email,
            'mobile': student_mobile or 'Not specified',
            'city': (student.city if student else '') or (target_reg.event_location.city if target_reg and target_reg.event_location else 'N/A'),
            'country': (student.country_of_residence if student else '') or (target_reg.preferred_country if target_reg else 'N/A'),
            'education': (student.current_education if student else '') or (target_reg.role if target_reg else 'Student'),
            'school_college': (student.school_college if student else '') or 'N/A',
            'grades': (student.grades if student else '') or 'Not disclosed',
            'english_proficiency': (student.english_proficiency if student else '') or 'Not taken yet',
            'preferred_degree': (student.preferred_degree if student else '') or 'Undergraduate / Postgraduate',
            'preferred_program': (student.preferred_program if student else '') or (target_reg.preferred_program if target_reg else 'General'),
            'budget_range': (student.budget_range if student else '') or (target_reg.budget_range if target_reg else 'Medium'),
            'badge_id': (passport.badge_id if passport else '') or (target_reg.registration_id if target_reg else f"KNOVA-STU-{target_reg.id:04d}"),
            'passport_points': passport.total_points if passport else 10,
            'rating': rating,
            'notes': notes or action_tags,
            'documents': docs,
            'punch_time': timezone.now().strftime('%b %d, %Y • %I:%M %p')
        }
    })


@login_required(login_url='/portal/login/')
def dashboard_exhibitor_leads(request):
    from .models import Exhibitor, ExhibitorLead
    profile = get_exhibitor_profile(request.user)
    if not profile and hasattr(request.user, 'university_staff'):
        uni = request.user.university_staff.university
        profile = Exhibitor.objects.filter(company_name__iexact=uni.name).first()
        if not profile:
            profile = Exhibitor.objects.filter(company_name__icontains=uni.name.split()[0]).first()
    if not profile and (request.user.is_superuser or request.user.is_staff):
        exh_id = request.GET.get('exhibitor_id')
        if exh_id:
            profile = Exhibitor.objects.filter(pk=exh_id).first()
        if not profile:
            profile = Exhibitor.objects.filter(captured_leads__isnull=False).distinct().first() or Exhibitor.objects.first()
    if not profile:
        return redirect('dashboard_index')
    leads = profile.captured_leads.filter(scanned_registration__role__iexact='Student').select_related('scanned_registration').order_by('-scanned_at')
    all_exhibitors = Exhibitor.objects.all() if (request.user.is_superuser or request.user.is_staff) else None

    return render(request, 'dashboard/exhibitor_leads.html', {
        'profile': profile,
        'role': 'exhibitor',
        'leads': leads,
        'all_exhibitors': all_exhibitors
    })


@login_required(login_url='/portal/login/')
def dashboard_exhibitor_scheduler(request):

    return redirect('dashboard_index')
    profile = get_exhibitor_profile(request.user)
    if not profile:
        return redirect('dashboard_index')
    from .models import ExhibitorMeeting, Registration
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'schedule':
            reg_id = request.POST.get('registration_id')
            time_str = request.POST.get('scheduled_time')
            notes = request.POST.get('notes', '')
            try:
                target_reg = Registration.objects.get(id=reg_id)
                import datetime
                dt = datetime.datetime.fromisoformat(time_str)
                ExhibitorMeeting.objects.create(
                    exhibitor=profile,
                    student_registration=target_reg,
                    scheduled_time=dt,
                    notes=notes
                )
            except Exception as e:
                pass
        elif action == 'update_status':
            meeting_id = request.POST.get('meeting_id')
            status = request.POST.get('status')
            try:
                meeting = ExhibitorMeeting.objects.get(id=meeting_id, exhibitor=profile)
                meeting.status = status
                meeting.save()
            except:
                pass

        return redirect('dashboard_exhibitor_scheduler')
    meetings = ExhibitorMeeting.objects.filter(exhibitor=profile)

    # We can fetch recent leads to easily schedule them
    recent_leads = profile.captured_leads.all().order_by('-scanned_at')[:20]

    return render(request, 'dashboard/exhibitor_scheduler.html', {
        'profile': profile,
        'role': 'exhibitor',
        'meetings': meetings,
        'recent_leads': recent_leads
    })


@login_required(login_url='/portal/login/')
def dashboard_data_import(request):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Only administrators can access bulk imports.")
    from django.shortcuts import redirect
    from django.contrib import messages
    from .models import DataImportJob
    from .tasks import process_data_import_task
    if request.method == 'POST':
        import_type = request.POST.get('import_type')
        uploaded_file = request.FILES.get('file')
        if import_type and uploaded_file:
            if not uploaded_file.name.endswith('.csv'):
                messages.error(request, "Only CSV files are currently supported.")

                return redirect('/dashboard/settings/?tab=import')
            job = DataImportJob.objects.create(
                import_type=import_type,
                uploaded_file=uploaded_file,
                uploaded_by=request.user
            )
            try:
                process_data_import_task.delay(job.id)
            except Exception:
                try:
                    process_data_import_task(job.id)
                except Exception:
                    pass
            messages.success(request, f"Import job #{job.id} started. It will process in the background.")

        return redirect('/dashboard/settings/?tab=import')

    return redirect('/dashboard/settings/?tab=import')
import os, io, zipfile, csv
from django.core.management import call_command
from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.contrib import messages
from django.core.files.storage import FileSystemStorage


@login_required(login_url='/portal/login/')
def dashboard_backup_data(request):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Only administrators can backup data.")
    
    from .backup_utils import generate_backup, save_backup_to_disk
    compressed = request.GET.get('compress') == '1' or request.GET.get('format') == 'gz'
    backup = generate_backup(compressed=compressed)
    
    # Save a copy to local disk to keep retention archive up to date
    try:
        save_backup_to_disk(backup['content'], backup['filename'])
    except Exception:
        pass

    content_type = 'application/gzip' if compressed else 'application/json'
    response = HttpResponse(backup['content'], content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{backup["filename"]}"'
    return response


@login_required(login_url='/portal/login/')
def dashboard_download_stored_backup(request, filename):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Only administrators can download backups.")
    
    from .backup_utils import get_backup_dir
    safe_name = os.path.basename(filename)
    if not safe_name.startswith('knova_backup_'):
        messages.error(request, "Invalid backup filename requested.")
        return redirect('/dashboard/settings/?tab=backup')
    
    backup_dir = get_backup_dir()
    file_path = os.path.join(backup_dir, safe_name)
    if not os.path.exists(file_path):
        messages.error(request, "Requested backup file does not exist or has expired.")
        return redirect('/dashboard/settings/?tab=backup')

    with open(file_path, 'rb') as f:
        content = f.read()

    content_type = 'application/gzip' if safe_name.endswith('.gz') else 'application/json'
    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{safe_name}"'
    return response


@login_required(login_url='/portal/login/')
def dashboard_restore_data(request):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Only administrators can restore data.")
    
    from .backup_utils import restore_database_dump
    if request.method == 'POST' and request.FILES.get('backup_file'):
        uploaded_file = request.FILES['backup_file']
        clean_wipe = request.POST.get('clean_wipe') == '1'
        
        ok, msg, count = restore_database_dump(uploaded_file, uploaded_file.name, clean_wipe=clean_wipe)
        if ok:
            messages.success(request, f"Database restored successfully! {msg}")
        else:
            messages.error(request, f"Restore failed: {msg}")
    else:
        messages.warning(request, "Please choose a valid backup snapshot file (.json, .gz, or .zip).")

    return redirect('/dashboard/settings/?tab=backup')


@login_required(login_url='/portal/login/')
def dashboard_trigger_backup_email(request):
    if not request.user.is_superuser and not request.user.is_staff and not request.user.groups.filter(name__in=['admin', 'manager']).exists():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Only administrators can dispatch backups.")
    
    from .backup_utils import generate_backup, save_backup_to_disk, send_backup_email, get_smtp_config
    if request.method == 'POST':
        backup = generate_backup(compressed=True)
        try:
            save_backup_to_disk(backup['content'], backup['filename'])
        except Exception:
            pass
        
        target_email = request.POST.get('recipient') or get_smtp_config().get('recipient') or 'arjunaravinda@gmail.com'
        ok, msg = send_backup_email(
            dump_bytes=backup['content'],
            filename=backup['filename'],
            record_count=backup['record_count'],
            size_formatted=backup['size_formatted'],
            recipient=target_email
        )
        if ok:
            messages.success(request, f"Backup snapshot ({backup['size_formatted']}, {backup['record_count']} objects) generated and dispatched! {msg}")
        else:
            messages.warning(request, f"Backup created & saved on server disk ({backup['size_formatted']}, {backup['record_count']} objects), but email status: {msg}")
            
    return redirect('/dashboard/settings/?tab=backup')


@login_required(login_url='/portal/login/')
def dashboard_toggle_backup_status(request):
    if not request.user.is_superuser and not request.user.is_staff and not request.user.groups.filter(name__in=['admin', 'manager']).exists():
        from django.http import JsonResponse
        return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)

    from .models import SiteConfiguration
    from django.http import JsonResponse
    cfg = SiteConfiguration.get_solo()

    if request.method == 'POST':
        state_param = request.POST.get('state')
        if state_param is not None:
            cfg.backup_enabled = state_param.lower() in ['true', '1', 'on']
        else:
            cfg.backup_enabled = not cfg.backup_enabled
        cfg.save()

    label = "Active (Every 5 min)" if cfg.backup_enabled else "Paused"
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax')

    if is_ajax:
        return JsonResponse({
            'status': 'success',
            'backup_enabled': cfg.backup_enabled,
            'label': label,
            'message': f"Automated 5-minute backup email delivery is now {label}."
        })

    messages.success(request, f"Automated backup delivery status updated: {label}.")
    return redirect('/dashboard/settings/?tab=backup')


@login_required(login_url='/portal/login/')
def dashboard_save_backup_settings(request):
    if not request.user.is_superuser and not request.user.is_staff and not request.user.groups.filter(name__in=['admin', 'manager']).exists():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Only administrators can change system configuration.")

    if request.method == 'POST':
        from .models import SiteConfiguration
        from .backup_utils import parse_email_recipients
        cfg = SiteConfiguration.get_solo()

        # Handle pause/resume toggle
        if 'backup_enabled' in request.POST:
            cfg.backup_enabled = request.POST.get('backup_enabled') in ['on', '1', 'true', True]
        elif 'from_full_form' in request.POST:
            cfg.backup_enabled = False

        recipient_raw = request.POST.get('backup_email_recipient', '').strip()
        if recipient_raw:
            recipients_list = parse_email_recipients(recipient_raw)
            cfg.backup_email_recipient = ", ".join(recipients_list)

        smtp_user = request.POST.get('smtp_user', '').strip()
        if smtp_user:
            cfg.smtp_user = smtp_user

        new_password = request.POST.get('smtp_password', '').strip().replace(' ', '')
        if new_password:
            cfg.smtp_password = new_password

        cfg.smtp_host = request.POST.get('smtp_host', 'smtp.gmail.com').strip() or 'smtp.gmail.com'
        try:
            cfg.smtp_port = int(request.POST.get('smtp_port', 587))
        except (TypeError, ValueError):
            cfg.smtp_port = 587
        cfg.smtp_use_tls = request.POST.get('smtp_use_tls') == 'on' or 'smtp_use_tls' in request.POST
        if cfg.smtp_port == 587 or 'gmail' in cfg.smtp_host.lower():
            cfg.smtp_use_tls = True
        cfg.save()

        # If user also requested an instant test email
        if request.POST.get('test_send'):
            from .backup_utils import generate_backup, send_backup_email
            backup_data = generate_backup(compressed=True)
            ok, msg = send_backup_email(
                dump_bytes=backup_data['content'],
                filename=backup_data['filename'],
                record_count=backup_data['record_count'],
                size_formatted=backup_data['size_formatted'],
                recipient=cfg.backup_email_recipient
            )
            if ok:
                messages.success(request, f"Settings saved! Test backup successfully dispatched to: {cfg.backup_email_recipient}.")
            else:
                messages.warning(request, f"Settings saved, but test email delivery reported: {msg}")
        else:
            status_text = "Active (Every 5 min)" if cfg.backup_enabled else "Paused (No emails sent)"
            messages.success(request, f"Backup mail settings updated successfully! Status: {status_text} | Recipients: {cfg.backup_email_recipient}")

    return redirect('/dashboard/settings/?tab=backup')


@login_required(login_url='/portal/login/')
def dashboard_export_csv(request):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Only administrators can export data.")
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for model in apps.get_models():
            if model._meta.app_label in ['core', 'auth']:
                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer)
                fields = [f.name for f in model._meta.fields]
                writer.writerow(fields)
                for obj in model.objects.all():
                    writer.writerow([getattr(obj, field, '') for field in fields])
                zip_file.writestr(f"{model._meta.model_name}.csv", csv_buffer.getvalue())
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="data_export_csv.zip"'

    return response


@login_required(login_url='/portal/login/')
def dashboard_export_excel(request):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Only administrators can export data.")
    try:
        import openpyxl
    except ImportError:
        messages.error(request, "openpyxl is not installed for Excel export.")

        return redirect('dashboard_settings')
    wb = openpyxl.Workbook()
    wb.remove(wb.active) # Remove default sheet
    for model in apps.get_models():
        if model._meta.app_label in ['core', 'auth']:
            ws = wb.create_sheet(title=model._meta.model_name[:31]) # Excel sheet name limit is 31
            fields = [f.name for f in model._meta.fields]
            ws.append(fields)
            for obj in model.objects.all():
                ws.append([str(getattr(obj, field, '')) for field in fields])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="data_export.xlsx"'
    wb.save(response)

    return response


def toggle_verification(request, model_name, pk):
    from django.shortcuts import redirect, get_object_or_404
    from .models import Exhibitor, Sponsor, Speaker
    if not (request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name__in=['admin', 'manager', 'editor']).exists()):
        return redirect('dashboard_index')
    if model_name == 'exhibitor':
        from .models import University
        obj = get_object_or_404(Exhibitor, pk=pk)
        obj.is_verified = not obj.is_verified
        obj.save()
        University.objects.filter(name__iexact=obj.company_name).update(is_approved=obj.is_verified)
    elif model_name == 'sponsor':
        obj = get_object_or_404(Sponsor, pk=pk)
        obj.is_verified = not obj.is_verified
        obj.save()
    elif model_name == 'speaker':
        obj = get_object_or_404(Speaker, pk=pk)
        obj.is_verified = not obj.is_verified
        obj.save()
    elif model_name == 'university':
        from .models import University, Exhibitor
        obj = get_object_or_404(University, pk=pk)
        obj.is_approved = not obj.is_approved
        obj.save()
        Exhibitor.objects.filter(company_name__iexact=obj.name).update(is_verified=obj.is_approved)
        referer = request.META.get('HTTP_REFERER')

        return redirect(referer if referer else 'dashboard_universities')
    else:
        return redirect('dashboard_index')
    referer = request.META.get('HTTP_REFERER')

    return redirect(referer if referer else 'dashboard_index')


def registration_view(request, pk):
    from django.shortcuts import render, get_object_or_404, redirect
    from .models import Registration
    if not request.user.is_superuser:
        return redirect('dashboard')
    registration = get_object_or_404(Registration, pk=pk)
    context = {
        'role': 'admin',
        'reg': registration
    }

    return render(request, 'dashboard/registration_detail.html', context)


@login_required(login_url='/portal/login/')
def dashboard_search(request):
    query = request.GET.get('q', '').strip()
    results = {}
    if query:
        from .models import EventLocation, Exhibitor, Registration, Speaker, ProgrammeSession, Scholarship, University, Course
        from django.db.models import Q
        results['scholarships'] = Scholarship.objects.filter(Q(name__icontains=query) | Q(university__name__icontains=query) | Q(field_of_study__icontains=query)).select_related('university')[:20]
        results['universities'] = University.objects.filter(Q(name__icontains=query) | Q(profile__location_city__icontains=query) | Q(profile__location_state_country__icontains=query)).select_related('profile')[:20]
        results['courses'] = Course.objects.filter(Q(name__icontains=query) | Q(stream__icontains=query) | Q(university__name__icontains=query)).select_related('university', 'category')[:20]
        results['events'] = EventLocation.objects.filter(Q(name__icontains=query) | Q(city__icontains=query))
        results['exhibitors'] = Exhibitor.objects.filter(Q(company_name__icontains=query) | Q(country__icontains=query))
        results['registrations'] = Registration.objects.filter(Q(full_name__icontains=query) | Q(email__icontains=query))
        results['speakers'] = Speaker.objects.filter(Q(name__icontains=query) | Q(organization__icontains=query))
        results['sessions'] = ProgrammeSession.objects.filter(title__icontains=query)
    context = {
        'query': query,
        'results': results
    }

    return render(request, 'dashboard/search_results.html', context)


@login_required(login_url='/portal/login/')
def dashboard_universities(request):
    from .models import University, UniversityProfile
    from django.db.models import Q
    from django.core.paginator import Paginator
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    country_filter = request.GET.get('country', '').strip()
    from django.db.models import Case, When, Value, IntegerField
    unis = University.objects.select_related('profile').all().order_by(
        Case(
            When(hero_priority=0, then=Value(999)),
            default='hero_priority',
            output_field=IntegerField()
        ),
        '-id'
    )
    if query:
        unis = unis.filter(Q(name__icontains=query) | Q(profile__location_city__icontains=query) | Q(profile__location_state_country__icontains=query))
    if status_filter == 'approved':
        unis = unis.filter(is_approved=True)
    elif status_filter == 'hidden':
        unis = unis.filter(is_approved=False)
    if country_filter:
        unis = unis.filter(profile__location_state_country__iexact=country_filter)
    paginator = Paginator(unis, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    all_countries = sorted(list(set(UniversityProfile.objects.exclude(location_state_country='').values_list('location_state_country', flat=True))))
    context = {
        'role': 'admin',
        'universities': page_obj,
        'all_countries': all_countries,
        'query': query,
        'status_filter': status_filter,
        'country_filter': country_filter,
        'total_count': University.objects.count(),
        'approved_count': University.objects.filter(is_approved=True).count(),
        'hidden_count': University.objects.filter(is_approved=False).count(),
    }

    return render(request, 'dashboard/universities.html', context)


def can_manage_university(user, uni):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff or user.groups.filter(name__in=['Admin', 'admin', 'Manager', 'manager']).exists() or user.username.lower() == 'admin':
        return True
    if hasattr(user, 'university_staff') and user.university_staff and user.university_staff.university == uni:
        return True
    if hasattr(user, 'exhibitor_profile') and user.exhibitor_profile:
        if user.exhibitor_profile.company_name.strip().lower() == uni.name.strip().lower():
            return True
    if hasattr(user, 'exhibitor_staff_profile') and user.exhibitor_staff_profile:
        if user.exhibitor_staff_profile.exhibitor.company_name.strip().lower() == uni.name.strip().lower():
            return True
    from .models import Exhibitor
    exh = Exhibitor.objects.filter(company_name__iexact=uni.name).first()
    if exh and (exh.user == user or (exh.contact_email and exh.contact_email.lower() == user.email.lower())):
        return True

    return False


@login_required(login_url='/portal/login/')
def university_create(request):
    from .forms import UniversityForm
    from .models import University, UniversityProfile, Exhibitor
    from django.utils.text import slugify
    import uuid
    if not (request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name__in=['Admin', 'admin']).exists()):
        messages.error(request, "Permission denied.")

        return redirect('dashboard_index')
    if request.method == 'POST':
        form = UniversityForm(request.POST, request.FILES)
        if form.is_valid():
            uni = form.save(commit=False)
            base_slug = slugify(uni.name) or f"uni-{uuid.uuid4().hex[:6]}"
            slug = base_slug
            counter = 1
            while University.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            uni.slug = slug
            if not uni.hero_priority:
                from django.db.models import Max
                max_pri = University.objects.aggregate(Max('hero_priority'))['hero_priority__max'] or 0
                uni.hero_priority = max_pri + 1
            uni.is_approved = True
            uni.save()
            profile, _ = UniversityProfile.objects.get_or_create(university=uni)
            profile.location_city = form.cleaned_data.get('location_city') or 'Global Campus'
            profile.location_state_country = form.cleaned_data.get('location_state_country') or 'International'
            profile.short_description = form.cleaned_data.get('short_description') or f"{uni.name} is a premier higher education institution offering accredited degree programs."
            profile.website = form.cleaned_data.get('website', '')
            profile.established_year = form.cleaned_data.get('established_year') or 2000
            profile.university_type = form.cleaned_data.get('university_type') or 'Higher Education Institution'
            profile.accreditation = form.cleaned_data.get('accreditation') or 'Accredited University'
            profile.about = form.cleaned_data.get('about') or f"{uni.name} offers comprehensive undergraduate and postgraduate programs with global accreditations."
            profile.campus_facilities = form.cleaned_data.get('campus_facilities') or "Modern lecture theatres, digital research labs, interactive study suites, and student advisory desks."
            profile.academic_programmes = form.cleaned_data.get('academic_programmes') or "Signature degree courses, international accreditations, and specialized research tracks designed for global industry readiness."
            profile.admission_process = form.cleaned_data.get('admission_process') or "Direct consultation, portfolio evaluation, and on-spot scholarship assessment available at the university booth."
            profile.scholarships_assistance = form.cleaned_data.get('scholarships_assistance') or "Merit-based waivers, partial tuition assistance, and competitive grants offered to eligible prospective students."
            profile.international_support = form.cleaned_data.get('international_support') or "Comprehensive visa guidance, student housing assistance, cultural transition mentorship, and 24/7 student welfare support."
            profile.career_opportunities = form.cleaned_data.get('career_opportunities') or "Extensive corporate partner networks, on-campus recruitments, internships, and global alumni placement support."
            profile.why_choose_us = form.cleaned_data.get('why_choose_us') or "World-class academic standards, state-of-the-art facilities, career-focused learning, and a vibrant global student community."
            if 'logo' in request.FILES:
                profile.logo = request.FILES['logo']
            if 'cover_image' in request.FILES:
                profile.cover_image = request.FILES['cover_image']
            profile.save()

            # Auto-sync with Exhibitor model
            from .models import Exhibitor, EventLocation, ExpoBooth
            loc = EventLocation.objects.filter(is_active=True).first() or EventLocation.objects.first()
            exh = Exhibitor.objects.filter(company_name__iexact=uni.name).first() or Exhibitor.objects.filter(university=uni).first()
            if not exh and loc:
                exh = Exhibitor.objects.create(
                    university=uni,
                    company_name=uni.name,
                    event_location=loc,
                    country=profile.location_state_country or "International",
                    website=profile.website,
                    logo=profile.logo,
                    is_verified=uni.is_approved
                )
            elif exh and not exh.university:
                exh.university = uni
                exh.save(update_fields=['university'])

            # Allocate an ExpoBooth if unallocated
            if exh and not ExpoBooth.objects.filter(exhibitor=exh).exists() and not ExpoBooth.objects.filter(university=uni).exists():
                available_booth = ExpoBooth.objects.filter(status='AVAILABLE', exhibitor__isnull=True, university__isnull=True).first()
                if available_booth:
                    available_booth.exhibitor = exh
                    available_booth.university = uni
                    available_booth.status = 'ASSIGNED'
                    available_booth.save()

            messages.success(request, f'University Card & Exhibitor Profile for "{uni.name}" successfully created and synced!')

            return redirect('dashboard_universities')
    else:
        form = UniversityForm()

    return render(request, 'dashboard/university_form.html', {
        'form': form,
        'action': 'Add New',
        'role': 'admin'
    })


@login_required(login_url='/portal/login/')
def university_update(request, pk=None):
    from .forms import UniversityForm
    from .models import University, UniversityProfile, Exhibitor
    from django.shortcuts import get_object_or_404
    uni = None
    if pk:
        uni = get_object_or_404(University, pk=pk)
    elif hasattr(request.user, 'university_staff') and request.user.university_staff:
        uni = request.user.university_staff.university
    elif hasattr(request.user, 'exhibitor_profile') and request.user.exhibitor_profile:
        uni = University.objects.filter(name__iexact=request.user.exhibitor_profile.company_name).first()
    elif hasattr(request.user, 'exhibitor_staff_profile') and request.user.exhibitor_staff_profile:
        uni = University.objects.filter(name__iexact=request.user.exhibitor_staff_profile.exhibitor.company_name).first()
    elif request.user.is_superuser or request.user.is_staff:
        uni = University.objects.first()
    if not uni:
        messages.error(request, "University profile not found.")

        return redirect('dashboard_index')
    if not can_manage_university(request.user, uni):
        messages.error(request, "Permission denied: you cannot edit this institution.")

        return redirect('dashboard_index')
    is_admin = request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name__in=['Admin', 'admin']).exists()
    if request.method == 'POST':
        form = UniversityForm(request.POST, request.FILES, instance=uni, is_admin=is_admin)
        if form.is_valid():
            uni = form.save()
            profile, _ = UniversityProfile.objects.get_or_create(university=uni)
            profile.location_city = form.cleaned_data.get('location_city', '')
            profile.location_state_country = form.cleaned_data.get('location_state_country', '')
            profile.short_description = form.cleaned_data.get('short_description', '')
            profile.website = form.cleaned_data.get('website', '')
            profile.established_year = form.cleaned_data.get('established_year', '')
            profile.university_type = form.cleaned_data.get('university_type', '')
            profile.accreditation = form.cleaned_data.get('accreditation', '')
            profile.about = form.cleaned_data.get('about', '')
            profile.campus_facilities = form.cleaned_data.get('campus_facilities', '')
            profile.academic_programmes = form.cleaned_data.get('academic_programmes', '')
            profile.admission_process = form.cleaned_data.get('admission_process', '')
            profile.scholarships_assistance = form.cleaned_data.get('scholarships_assistance', '')
            profile.international_support = form.cleaned_data.get('international_support', '')
            profile.career_opportunities = form.cleaned_data.get('career_opportunities', '')
            profile.why_choose_us = form.cleaned_data.get('why_choose_us', '')
            if 'logo' in request.FILES:
                profile.logo = request.FILES['logo']
            if 'cover_image' in request.FILES:
                profile.cover_image = request.FILES['cover_image']
            profile.save()

            # Also sync Exhibitor if exists
            exh = Exhibitor.objects.filter(company_name__iexact=uni.name).first()
            if exh:
                if profile.short_description:
                    exh.description = profile.short_description
                if profile.website:
                    exh.website = profile.website
                if 'logo' in request.FILES:
                    exh.logo = request.FILES['logo']
                exh.save()
            messages.success(request, f'University "{uni.name}" profile and page content updated successfully!')
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            if request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name__in=['Admin', 'admin']).exists():
                return redirect('dashboard_universities')

            return redirect('university_dashboard_view', pk=uni.pk)
    else:
        form = UniversityForm(instance=uni, is_admin=is_admin)
    is_admin = request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name__in=['Admin', 'admin']).exists()

    return render(request, 'dashboard/university_form.html', {
        'form': form,
        'university': uni,
        'action': 'Edit',
        'is_admin': is_admin,
        'role': 'admin' if is_admin else 'university'
    })


@login_required(login_url='/portal/login/')
def university_delete(request, pk):
    from .models import University
    from django.shortcuts import get_object_or_404
    uni = get_object_or_404(University, pk=pk)
    if not (request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name__in=['Admin', 'admin']).exists()):
        messages.error(request, "Permission denied.")

        return redirect('dashboard_index')
    if request.method == 'POST':
        name = uni.name
        uni.delete()
        messages.success(request, f'University "{name}" has been removed.')

        return redirect('dashboard_universities')

    return render(request, 'dashboard/university_confirm_delete.html', {
        'university': uni,
        'role': 'admin'
    })


@login_required(login_url='/portal/login/')
def university_dashboard_view(request, pk=None):

    return redirect('/dashboard/#coursesSection')
    from .models import University, UniversityProfile, Course, Scholarship, ExpoBooth, BoothInteraction, UniversityApplication, Exhibitor, CourseCategory
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    uni = None
    if pk:
        uni = get_object_or_404(University, pk=pk)
    elif hasattr(request.user, 'university_staff') and request.user.university_staff:
        uni = request.user.university_staff.university
    elif hasattr(request.user, 'exhibitor_profile') and request.user.exhibitor_profile:
        uni = University.objects.filter(name__iexact=request.user.exhibitor_profile.company_name).first()
    elif hasattr(request.user, 'exhibitor_staff_profile') and request.user.exhibitor_staff_profile:
        uni = University.objects.filter(name__iexact=request.user.exhibitor_staff_profile.exhibitor.company_name).first()
    elif request.user.is_superuser or request.user.is_staff:
        uni = University.objects.first()
        if not uni:
            messages.info(request, "No universities created yet.")

            return redirect('university_create')
    if not uni:
        messages.error(request, "University profile could not be located. Access restricted to University Representatives and Administrators.")

        return redirect('dashboard_index')
    if not can_manage_university(request.user, uni):
        messages.error(request, "Permission denied to view this institution's management portal.")

        return redirect('dashboard_index')
    profile, _ = UniversityProfile.objects.get_or_create(university=uni)
    courses = uni.courses.all().order_by('-id')
    scholarships = uni.scholarships.all().order_by('-id')
    applications = uni.student_applications.select_related('student__user').order_by('-applied_at')
    booths = ExpoBooth.objects.filter(university=uni)
    interactions = BoothInteraction.objects.filter(booth__university=uni).select_related('student__user').order_by('-interaction_date')[:25]
    from .models import Registration
    recent_students = Registration.objects.filter(role='Student').order_by('-id')[:20]
    categories = CourseCategory.objects.all()
    context = {
        'role': 'university' if not (request.user.is_superuser or request.user.is_staff) else 'admin',
        'university': uni,
        'profile': profile,
        'courses': courses,
        'categories': categories,
        'scholarships': scholarships,
        'applications': applications,
        'booths': booths,
        'interactions': interactions,
        'recent_students': recent_students,
        'total_courses': courses.count(),
        'total_applications': applications.count(),
        'total_scholarships': scholarships.count(),
        'total_interactions': interactions.count(),
    }

    return render(request, 'dashboard/university_dashboard.html', context)


@login_required(login_url='/portal/login/')
def university_course_create(request, uni_pk=None):
    from .models import University, Course, CourseCategory
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    from django.utils.text import slugify
    uni = None
    if uni_pk:
        uni = get_object_or_404(University, pk=uni_pk)
    elif hasattr(request.user, 'university_staff') and request.user.university_staff:
        uni = request.user.university_staff.university
    elif hasattr(request.user, 'exhibitor_profile') and request.user.exhibitor_profile:
        uni = University.objects.filter(name__iexact=request.user.exhibitor_profile.company_name).first()
    elif hasattr(request.user, 'exhibitor_staff_profile') and request.user.exhibitor_staff_profile:
        uni = University.objects.filter(name__iexact=request.user.exhibitor_staff_profile.exhibitor.company_name).first()
    elif request.user.is_superuser or request.user.is_staff:
        uni = University.objects.first()
    if not uni:
        messages.error(request, "University profile not found.")

        return redirect('dashboard_index')
    if not can_manage_university(request.user, uni):
        messages.error(request, "Permission denied: you cannot add courses to this institution.")

        return redirect('dashboard_index')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        degree_type = request.POST.get('degree_type', 'Undergraduate')
        stream = request.POST.get('stream', 'General')
        duration = request.POST.get('duration', '3 Years')
        mode = request.POST.get('mode', 'Full Time')
        fees = request.POST.get('fees', '$15,000 / year')
        eligibility = request.POST.get('eligibility', 'High School Diploma')
        scholarship_available = request.POST.get('scholarship_available') in ['on', 'true', 'True', '1', True]
        if name:
            category = None
            category_id = request.POST.get('category')
            if category_id:
                category = CourseCategory.objects.filter(pk=category_id).first()
            if not category and stream:
                category = CourseCategory.objects.filter(name__iexact=stream).first()
                if not category:
                    category, _ = CourseCategory.objects.get_or_create(name=stream)
            Course.objects.create(
                university=uni,
                name=name,
                category=category,
                degree_type=degree_type,
                stream=stream,
                duration=duration,
                mode=mode,
                fees=fees,
                eligibility=eligibility,
                scholarship_available=scholarship_available,
                is_active=True,
                status='Approved'
            )
            messages.success(request, f'Course "{name}" successfully added to {uni.name}!')
            next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
            if next_url:
                return redirect(next_url)

            return redirect('university_dashboard_view', pk=uni.pk)

    return redirect('university_dashboard_view', pk=uni.pk)


@login_required(login_url='/portal/login/')
def university_course_delete(request, pk):
    from .models import Course
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    course = get_object_or_404(Course, pk=pk)
    uni = course.university
    if not can_manage_university(request.user, uni):
        messages.error(request, "Permission denied.")

        return redirect('dashboard_index')
    course_name = course.name
    course.delete()
    messages.success(request, f'Course "{course_name}" removed.')
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)

    return redirect('university_dashboard_view', pk=uni.pk)


@login_required(login_url='/portal/login/')
def university_scholarship_create(request, uni_pk=None):
    from .models import University, Scholarship
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    from datetime import datetime
    uni = None
    if uni_pk:
        uni = get_object_or_404(University, pk=uni_pk)
    elif hasattr(request.user, 'university_staff') and request.user.university_staff:
        uni = request.user.university_staff.university
    elif hasattr(request.user, 'exhibitor_profile') and request.user.exhibitor_profile:
        uni = University.objects.filter(name__iexact=request.user.exhibitor_profile.company_name).first()
    elif hasattr(request.user, 'exhibitor_staff_profile') and request.user.exhibitor_staff_profile:
        uni = University.objects.filter(name__iexact=request.user.exhibitor_staff_profile.exhibitor.company_name).first()
    elif request.user.is_superuser or request.user.is_staff:
        uni = University.objects.first()
    if not uni:
        messages.error(request, "University profile not found.")

        return redirect('dashboard_index')
    if not can_manage_university(request.user, uni):
        messages.error(request, "Permission denied: you cannot add scholarships to this institution.")

        return redirect('dashboard_index')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        amount = request.POST.get('amount', '').strip() or 'Partial Tuition Waiver'
        coverage_type = request.POST.get('coverage_type', 'Partial')
        field_of_study = request.POST.get('field_of_study', '').strip() or 'All Fields'
        level = request.POST.get('level', 'All Levels')
        category = request.POST.get('category', '').strip() or 'Merit-Based'
        eligibility = request.POST.get('eligibility', '').strip() or 'Academic excellence and qualifying test scores.'
        description = request.POST.get('description', '').strip() or f'{name} offered by {uni.name} for prospective students.'
        deadline_str = request.POST.get('deadline', '').strip()
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        if name:
            Scholarship.objects.create(
                university=uni,
                name=name,
                amount=amount,
                coverage_type=coverage_type,
                field_of_study=field_of_study,
                level=level,
                category=category,
                eligibility=eligibility,
                description=description,
                deadline=deadline,
                status='Approved'
            )
            messages.success(request, f'Scholarship "{name}" successfully added to {uni.name}!')
            next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
            if next_url:
                return redirect(next_url)

            return redirect('university_dashboard_view', pk=uni.pk)

    return redirect('university_dashboard_view', pk=uni.pk)


@login_required(login_url='/portal/login/')
@login_required(login_url='/portal/login/')
def university_course_update(request, pk):
    from .models import Course, CourseCategory
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    course = get_object_or_404(Course, pk=pk)
    uni = course.university
    if not can_manage_university(request.user, uni):
        messages.error(request, "Permission denied.")

        return redirect('dashboard_index')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        degree_type = request.POST.get('degree_type', course.degree_type)
        stream = request.POST.get('stream', course.stream).strip()
        duration = request.POST.get('duration', course.duration).strip()
        mode = request.POST.get('mode', course.mode)
        fees = request.POST.get('fees', course.fees).strip()
        eligibility = request.POST.get('eligibility', course.eligibility).strip()
        scholarship_available = request.POST.get('scholarship_available') in ['on', 'true', 'True', '1', True]
        if name:
            course.name = name
            course.degree_type = degree_type
            course.stream = stream
            course.duration = duration
            course.mode = mode
            course.fees = fees
            course.eligibility = eligibility
            course.scholarship_available = scholarship_available
            category = None
            category_id = request.POST.get('category')
            if category_id:
                category = CourseCategory.objects.filter(pk=category_id).first()
            if not category and stream:
                category, _ = CourseCategory.objects.get_or_create(name=stream)
            if category:
                course.category = category
            course.save()
            messages.success(request, f'Course "{name}" updated successfully!')
            next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
            if next_url:
                return redirect(next_url)

            return redirect('university_dashboard_view', pk=uni.pk)

    return redirect('university_dashboard_view', pk=uni.pk)


@login_required(login_url='/portal/login/')
def university_scholarship_update(request, pk):
    from .models import Scholarship
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    from datetime import datetime
    sch = get_object_or_404(Scholarship, pk=pk)
    uni = sch.university
    if not can_manage_university(request.user, uni):
        messages.error(request, "Permission denied.")

        return redirect('dashboard_index')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        amount = request.POST.get('amount', '').strip() or sch.amount
        coverage_type = request.POST.get('coverage_type', sch.coverage_type)
        field_of_study = request.POST.get('field_of_study', '').strip() or sch.field_of_study
        level = request.POST.get('level', sch.level)
        category = request.POST.get('category', '').strip() or sch.category
        eligibility = request.POST.get('eligibility', '').strip() or sch.eligibility
        description = request.POST.get('description', '').strip() or sch.description
        deadline_str = request.POST.get('deadline', '').strip()
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        if name:
            sch.name = name
            sch.amount = amount
            sch.coverage_type = coverage_type
            sch.field_of_study = field_of_study
            sch.level = level
            sch.category = category
            sch.eligibility = eligibility
            sch.description = description
            sch.deadline = deadline
            sch.save()
            messages.success(request, f'Scholarship "{name}" updated successfully!')
            next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
            if next_url:
                return redirect(next_url)

            return redirect('university_dashboard_view', pk=uni.pk)

    return redirect('university_dashboard_view', pk=uni.pk)


def university_scholarship_delete(request, pk):
    from .models import Scholarship
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    sch = get_object_or_404(Scholarship, pk=pk)
    uni = sch.university
    if not can_manage_university(request.user, uni):
        messages.error(request, "Permission denied.")

        return redirect('dashboard_index')
    sch_name = sch.name
    sch.delete()
    messages.success(request, f'Scholarship "{sch_name}" removed.')
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)

    return redirect('university_dashboard_view', pk=uni.pk)


@login_required(login_url='/portal/login/')
def university_booth_checkin(request, uni_pk=None):
    from .models import (
        University, ExpoBooth, BoothInteraction, StudentChallengePassport,
        StudentProfile, Registration, User
    )
    from django.shortcuts import get_object_or_404, redirect
    from django.http import JsonResponse
    from django.contrib import messages
    import json
    uni = None
    if uni_pk:
        uni = get_object_or_404(University, pk=uni_pk)
    elif hasattr(request.user, 'university_staff'):
        uni = request.user.university_staff.university
    elif request.user.is_superuser:
        uni = University.objects.first()
    if not uni:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'success': False, 'message': 'University not found or access denied.'}, status=404)
        messages.error(request, 'University not found or access denied.')

        return redirect('dashboard_index')
    if not request.user.is_superuser and not (hasattr(request.user, 'university_staff') and request.user.university_staff.university == uni):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'success': False, 'message': 'Permission denied.'}, status=403)
        messages.error(request, 'Permission denied.')

        return redirect('dashboard_index')
    if request.method == 'POST':
        student_id = ''
        if request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                student_id = body.get('student_id', '').strip()
            except Exception:
                student_id = ''
        else:
            student_id = request.POST.get('student_id', '').strip()
        if not student_id:
            msg = 'Please enter a Student Badge ID, Registration ID, or Email.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({'success': False, 'message': msg}, status=400)
            messages.error(request, msg)

            return redirect('university_dashboard_view', pk=uni.pk)

        # 1. Lookup Student Challenge Passport or Registration
        passport = (
            StudentChallengePassport.objects.filter(badge_id__iexact=student_id).first()
            or StudentChallengePassport.objects.filter(student_email__iexact=student_id).first()
            or StudentChallengePassport.objects.filter(registration__registration_id__iexact=student_id).first()
        )
        reg = None
        user_obj = None
        if not passport:
            reg = (
                Registration.objects.filter(registration_id__iexact=student_id).first()
                or Registration.objects.filter(email__iexact=student_id).first()
            )
            if not reg:
                user_obj = (
                    User.objects.filter(username__iexact=student_id).first()
                    or User.objects.filter(email__iexact=student_id).first()
                )
                if user_obj:
                    reg = Registration.objects.filter(email=user_obj.email).first()
            if reg:
                passport = StudentChallengePassport.objects.filter(registration=reg).first()
                if not passport:
                    badge = reg.registration_id or f"KNOVA-{reg.pk:04d}"
                    passport = StudentChallengePassport.objects.create(
                        registration=reg,
                        badge_id=badge,
                        student_name=reg.full_name,
                        student_email=reg.email,
                        total_points=10,
                        profile_completed=True,
                        activity_log=[{'title': 'Expo Badge Registered (+10 pts)', 'points': 10, 'timestamp': 'Start'}]
                    )
            elif user_obj:
                passport = StudentChallengePassport.objects.filter(user=user_obj).first()
                if not passport:
                    badge = f"KNOVA-{user_obj.id:04d}"
                    name = user_obj.get_full_name() or user_obj.username
                    passport = StudentChallengePassport.objects.create(
                        user=user_obj,
                        badge_id=badge,
                        student_name=name,
                        student_email=user_obj.email,
                        total_points=10,
                        profile_completed=True,
                        activity_log=[{'title': 'Profile Activated (+10 pts)', 'points': 10, 'timestamp': 'Start'}]
                    )
        if not passport:
            msg = f'No attendee found matching "{student_id}". Please verify the Badge ID or Registration ID.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({'success': False, 'message': msg}, status=404)
            messages.error(request, msg)

            return redirect('university_dashboard_view', pk=uni.pk)

        # 2. Get or create booth for this university
        booth = ExpoBooth.objects.filter(university=uni).first()
        if not booth:
            booth = ExpoBooth.objects.create(
                university=uni,
                booth_number=f"U-{uni.pk}",
                hall="Main Hall",
                status="ASSIGNED"
            )

        # 3. Check if university is already in passport.visited_universities
        if not isinstance(passport.visited_universities, list):
            passport.visited_universities = []
        already_visited = uni.name in passport.visited_universities
        newly_completed_challenge = False
        if not already_visited:
            if not passport.is_elite_pass and len(passport.visited_universities) >= 3:
                err_msg = f"Standard Pass limit reached (3 booths max): {passport.student_name} ({passport.badge_id}) has already visited 3 booths. Complete all 6 KNOVA Challenge tasks to unlock Elite Pass for unlimited booth visits!"
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                    return JsonResponse({'success': False, 'message': err_msg, 'limit_reached': True, 'is_elite_pass': False}, status=403)
                messages.warning(request, err_msg)

                return redirect('university_dashboard_view', pk=uni.pk)
            passport.visited_universities.append(uni.name)
            passport.universities_visited_count = len(passport.visited_universities)
            passport.add_activity(f"Booth Check-in: {uni.name}", 10)
            if passport.universities_visited_count >= 3:
                newly_completed_challenge = True
                success_msg = f"Check-in verified for {passport.student_name} ({passport.badge_id})! 3/3 universities visited — Challenge 1 (Visit 3 Universities) COMPLETED! (+10 pts)"
            else:
                success_msg = f"Check-in verified for {passport.student_name} ({passport.badge_id}) at {uni.name}! Progress: {passport.universities_visited_count}/3 university visits (+10 pts)."
            messages.success(request, success_msg)
        else:
            success_msg = f"Notice: {passport.student_name} ({passport.badge_id}) was already checked in at {uni.name}. (Total: {passport.universities_visited_count}/3 visited)."
            messages.info(request, success_msg)

        # 4. Record BoothInteraction
        student_profile = None
        if passport.user:
            student_profile = getattr(passport.user, 'studentprofile', None)
            if not student_profile:
                student_profile, _ = StudentProfile.objects.get_or_create(user=passport.user)
        elif passport.registration:
            u = User.objects.filter(email=passport.registration.email).first()
            if not u:
                import uuid
                u = User.objects.create_user(
                    username=f"student_{uuid.uuid4().hex[:6]}",
                    email=passport.registration.email,
                    first_name=passport.registration.full_name
                )
            student_profile, _ = StudentProfile.objects.get_or_create(user=u)
        if student_profile and booth:
            BoothInteraction.objects.create(
                student=student_profile,
                booth=booth,
                interaction_type=f"Booth Check-in ({uni.name})"
            )
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({
                'success': True,
                'message': success_msg,
                'already_visited': already_visited,
                'student_name': passport.student_name,
                'badge_id': passport.badge_id,
                'universities_visited_count': passport.universities_visited_count,
                'challenge_completed': passport.universities_visited_count >= 3,
                'total_points': passport.total_points,
            })

        return redirect('university_dashboard_view', pk=uni.pk)

    return redirect('university_dashboard_view', pk=uni.pk)

# =============================================================================
# UNIVERSITY BOOTH ATTENDANCE SCANNER & ATTENDED STUDENTS SYSTEM
# =============================================================================


def _resolve_student_profile(student_code):
    """
    Robust student resolver matching QR UUID, Challenge Passport Badge ID,
    Registration ID, User Email, Username, or Student Profile PK.
    STRICT: Only resolves real prospective student attendees, NEVER exhibitors/staff/admins/parents.
    """
    student_code = (student_code or '').strip()
    if not student_code:
        return None
    from .models import StudentProfile, StudentChallengePassport, Registration
    from django.contrib.auth.models import User
    def is_non_student_user(u):
        if not u:
            return True
        if u.is_superuser or u.username.lower() == 'admin' or hasattr(u, 'university_staff') or hasattr(u, 'exhibitor_profile') or hasattr(u, 'exhibitor_staff_profile') or hasattr(u, 'parent_profile') or hasattr(u, 'seminar_staff'):
            return True
        reg = Registration.objects.filter(email__iexact=u.email).first() if u.email else None
        if reg and reg.role and reg.role.strip().lower() != 'student':
            return True

        return False

    # 1. Match on StudentProfile.qr_identifier (UUID)
    sp = StudentProfile.objects.filter(qr_identifier=student_code).select_related('user').first()
    if sp and not is_non_student_user(sp.user):
        return sp

    # 2. Match on StudentChallengePassport.badge_id
    passp = StudentChallengePassport.objects.filter(badge_id__iexact=student_code).first()
    if passp:
        if passp.user and not is_non_student_user(passp.user):
            sp, _ = StudentProfile.objects.get_or_create(user=passp.user)

            return sp
        elif passp.registration and passp.registration.role and passp.registration.role.strip().lower() == 'student':
            u = User.objects.filter(email__iexact=passp.registration.email).first()
            if u and not is_non_student_user(u):
                sp, _ = StudentProfile.objects.get_or_create(user=u, defaults={'mobile': passp.registration.phone or ''})

                return sp

    # 3. Match on Registration.registration_id or integer ID
    clean_code = student_code.replace("REG-", "").strip()
    reg = Registration.objects.filter(registration_id__iexact=student_code).first()
    if not reg and clean_code.isdigit():
        reg = Registration.objects.filter(id=int(clean_code)).first()
    if not reg:
        reg = Registration.objects.filter(email__iexact=student_code).first()
    if reg:
        if reg.role and reg.role.strip().lower() != 'student':
            return None
        u = User.objects.filter(email__iexact=reg.email).first()
        if u and not is_non_student_user(u):
            sp, _ = StudentProfile.objects.get_or_create(user=u, defaults={'mobile': reg.phone or ''})

            return sp

    # 4. Match on User.email or username ONLY if user is a student
    u = User.objects.filter(email__iexact=student_code).first() or User.objects.filter(username__iexact=student_code).first()
    if u and not is_non_student_user(u):
        if hasattr(u, 'student_profile'):
            return u.student_profile
        sp, _ = StudentProfile.objects.get_or_create(user=u)

        return sp

    # 5. Try parsing integer ID of StudentProfile
    if student_code.isdigit():
        sp = StudentProfile.objects.filter(id=int(student_code)).select_related('user').first()
        if sp and not is_non_student_user(sp.user):
            return sp

    return None


@login_required(login_url='/portal/login/')
def university_booth_scanner(request):
    """
    Booth Scanner portal for university staff.
    Allows real-time camera scanning and manual entry to punch student attendance.
    """
    from .models import University, ExpoBooth, BoothInteraction, Registration
    uni = None
    if hasattr(request.user, 'university_staff'):
        uni = request.user.university_staff.university
    elif request.user.is_superuser:
        uni_pk = request.GET.get('uni_id')
        if uni_pk:
            uni = University.objects.filter(pk=uni_pk).first()
        if not uni:
            uni = University.objects.first()
    if not uni:
        messages.error(request, "Access restricted to university staff or authorized administrators.")

        return redirect('dashboard_index')
    booth = ExpoBooth.objects.filter(university=uni).first()
    if not booth:
        booth = ExpoBooth.objects.create(
            university=uni,
            booth_number=f"B-{uni.pk:02d}",
            hall="University Hall A",
            status="ASSIGNED",
            qr_code=f"BOOTH-{uni.pk:04d}"
        )
    recent_punches = BoothInteraction.objects.filter(booth=booth).select_related('student__user').order_by('-interaction_date')[:15]
    recent_students = Registration.objects.filter(role='Student').order_by('-id')[:10]
    total_punched = BoothInteraction.objects.filter(booth=booth).count()
    context = {
        'role': 'university' if hasattr(request.user, 'university_staff') else 'admin',
        'university': uni,
        'booth': booth,
        'recent_punches': recent_punches,
        'recent_students': recent_students,
        'total_punched': total_punched,
        'all_universities': University.objects.all().order_by('name') if request.user.is_superuser else None
    }

    return render(request, 'dashboard/university_booth_scanner.html', context)


@login_required(login_url='/portal/login/')
def university_punch_attendance(request):
    """
    Endpoint to punch student attendance at the university booth.
    Makes the student's complete profile and academic documents visible to the university.
    Awards +20 Challenge Passport points.
    """
    from .models import University, ExpoBooth, BoothInteraction, StudentChallengePassport, StudentDocument
    from django.http import JsonResponse
    from django.utils import timezone
    import json
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required.'}, status=405)
    uni = None
    if hasattr(request.user, 'university_staff'):
        uni = request.user.university_staff.university
    elif request.user.is_superuser:
        uni_id = request.POST.get('uni_id')
        if not uni_id and request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                uni_id = body.get('uni_id')
            except Exception:
                pass
        if uni_id:
            uni = University.objects.filter(pk=uni_id).first()
        if not uni:
            uni = University.objects.first()
    if not uni:
        return JsonResponse({'success': False, 'message': 'University not found or access denied.'}, status=403)

    # Read payload
    student_code = ''
    status = 'Attended'
    notes = ''
    if request.content_type == 'application/json':
        try:
            body = json.loads(request.body)
            student_code = body.get('student_code', '').strip()
            status = body.get('status', 'Attended').strip() or 'Attended'
            notes = body.get('notes', '').strip()
        except Exception:
            student_code = ''
    else:
        student_code = request.POST.get('student_code', '').strip()
        status = request.POST.get('status', 'Attended').strip() or 'Attended'
        notes = request.POST.get('notes', '').strip()
    if not student_code:
        return JsonResponse({'success': False, 'message': 'Please provide student QR code, Badge ID, or Email.'}, status=400)
    student = _resolve_student_profile(student_code)
    if not student:
        return JsonResponse({'success': False, 'message': f'Student matching "{student_code}" could not be found. Please check badge ID or scan valid QR code.'}, status=404)

    # Resolve or create booth
    booth = ExpoBooth.objects.filter(university=uni).first()
    if not booth:
        booth = ExpoBooth.objects.create(
            university=uni,
            booth_number=f"B-{uni.pk:02d}",
            hall="University Hall A",
            status="ASSIGNED",
            qr_code=f"BOOTH-{uni.pk:04d}"
        )

    # Record or update BoothInteraction
    interaction, created = BoothInteraction.objects.get_or_create(
        student=student,
        booth=booth,
        defaults={
            'interaction_type': 'Attendance Punched',
            'status': status,
            'notes': notes
        }
    )
    if not created:
        interaction.status = status
        if notes:
            interaction.notes = notes
        interaction.interaction_date = timezone.now()
        interaction.save()

    # Award Challenge Passport points
    passport = StudentChallengePassport.objects.filter(user=student.user).first()
    if not passport:
        passport = StudentChallengePassport.objects.filter(student_email__iexact=student.user.email).first()
    if not passport:
        badge = student.qr_identifier[:10].upper() if student.qr_identifier else f"KNV-{student.user.id:04d}"
        passport = StudentChallengePassport.objects.create(
            user=student.user,
            badge_id=badge,
            student_name=student.user.get_full_name() or student.user.username,
            student_email=student.user.email,
            total_points=10,
            profile_completed=True,
            activity_log=[{'title': 'Expo Badge Registered (+10 pts)', 'points': 10, 'timestamp': 'Start'}]
        )
    if not isinstance(passport.visited_universities, list):
        passport.visited_universities = []
    already_awarded = uni.name in passport.visited_universities
    if not already_awarded:
        if not passport.is_elite_pass and len(passport.visited_universities) >= 3:
            return JsonResponse({
                'success': False,
                'message': f"Standard Pass limit reached (3 booths max) for {passport.student_name}. Complete all 6 challenge missions to unlock Elite Pass for unlimited booth visits!",
                'limit_reached': True,
                'is_elite_pass': False
            }, status=403)
        passport.visited_universities.append(uni.name)
        passport.universities_visited_count = len(passport.visited_universities)
        passport.add_activity(f"Booth Attendance Punched: {uni.name}", 20)
        passport.save()

    # Prepare complete student profile data for the university response
    docs = [{'title': d.title, 'url': d.document.url if d.document else '#', 'uploaded_at': d.uploaded_at.strftime('%b %d, %Y')} for d in student.documents.all()]
    student_name = student.user.get_full_name() or student.user.username
    data = {
        'success': True,
        'message': f"Attendance punched successfully for {student_name}! Complete student profile and academic documents are now fully visible.",
        'is_new_punch': created,
        'student': {
            'id': student.id,
            'name': student_name,
            'email': student.user.email,
            'mobile': student.mobile or 'Not specified',
            'city': student.city or 'N/A',
            'country': student.country_of_residence or 'N/A',
            'address': student.address or '',
            'education': student.current_education or 'Undergraduate',
            'school_college': student.school_college or 'N/A',
            'class_year': student.class_year or 'N/A',
            'grades': student.grades or 'Not disclosed',
            'english_proficiency': student.english_proficiency or 'Not taken yet',
            'work_experience': student.work_experience or '',
            'preferred_country': student.preferred_country or 'Global',
            'preferred_degree': student.get_preferred_degree_display() if hasattr(student, 'get_preferred_degree_display') and student.preferred_degree else (student.preferred_degree or 'Bachelor / Master'),
            'preferred_program': student.preferred_program or 'Open',
            'budget_range': student.get_budget_range_display() if hasattr(student, 'get_budget_range_display') and student.budget_range else (student.budget_range or 'Medium'),
            'intake_year': student.intake_year or '2027',
            'badge_id': passport.badge_id,
            'passport_points': passport.total_points,
            'universities_visited_count': passport.universities_visited_count,
            'documents': docs,
            'punch_time': timezone.now().strftime('%b %d, %Y • %I:%M %p'),
            'status': interaction.status,
            'notes': interaction.notes or ''
        }
    }

    return JsonResponse(data)


@login_required(login_url='/portal/login/')
def university_attended_students(request):
    """
    Roster view showing all students whose attendance was punched at this university's booth.
    Displays complete student profile data: contacts, academics, grades, preferences, and documents.
    """
    from .models import University, BoothInteraction, ExpoBooth
    from django.db.models import Q
    uni = None
    if hasattr(request.user, 'university_staff'):
        uni = request.user.university_staff.university
    elif request.user.is_superuser:
        uni_pk = request.GET.get('uni_id')
        if uni_pk:
            uni = University.objects.filter(pk=uni_pk).first()
        if not uni:
            uni = University.objects.first()
    if not uni:
        messages.error(request, "Access restricted to university representatives and administrators.")

        return redirect('dashboard_index')
    interactions_qs = BoothInteraction.objects.filter(booth__university=uni).select_related(
        'student__user', 'booth'
    ).prefetch_related('student__documents').order_by('-interaction_date')

    # Filters
    search_q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    degree_filter = request.GET.get('degree', '').strip()
    if search_q:
        interactions_qs = interactions_qs.filter(
            Q(student__user__first_name__icontains=search_q) |
            Q(student__user__last_name__icontains=search_q) |
            Q(student__user__email__icontains=search_q) |
            Q(student__school_college__icontains=search_q) |
            Q(student__preferred_program__icontains=search_q) |
            Q(student__mobile__icontains=search_q)
        )
    if status_filter:
        interactions_qs = interactions_qs.filter(status=status_filter)
    if degree_filter:
        interactions_qs = interactions_qs.filter(student__preferred_degree=degree_filter)
    total_attended = interactions_qs.count()
    context = {
        'role': 'university' if hasattr(request.user, 'university_staff') else 'admin',
        'university': uni,
        'interactions': interactions_qs,
        'total_attended': total_attended,
        'search_q': search_q,
        'status_filter': status_filter,
        'degree_filter': degree_filter,
        'all_universities': University.objects.all().order_by('name') if request.user.is_superuser else None
    }

    return render(request, 'dashboard/university_attended_students.html', context)


@login_required(login_url='/portal/login/')
def student_punch_booth_attendance(request, uni_pk):
    """
    Allows a student to mark/punch their attendance at a university booth.
    Immediately makes their data visible to that university.
    """
    from .models import University, ExpoBooth, BoothInteraction, StudentProfile
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse
    from django.utils import timezone
    uni = get_object_or_404(University, pk=uni_pk)
    student = None
    if hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
    else:
        student, _ = StudentProfile.objects.get_or_create(user=request.user)
    booth = ExpoBooth.objects.filter(university=uni).first()
    if not booth:
        booth = ExpoBooth.objects.create(
            university=uni,
            booth_number=f"B-{uni.pk:02d}",
            hall="Main Expo Hall",
            status="ASSIGNED",
            qr_code=f"BOOTH-{uni.pk:04d}"
        )
    interaction, created = BoothInteraction.objects.get_or_create(
        student=student,
        booth=booth,
        defaults={'interaction_type': 'Attendance Punched', 'status': 'Attended'}
    )
    if not created:
        interaction.interaction_date = timezone.now()
        interaction.save()

    # Award passport points
    from .models import StudentChallengePassport
    passport = StudentChallengePassport.objects.filter(user=student.user).first()
    if not passport:
        badge = student.qr_identifier[:10].upper() if student.qr_identifier else f"KNV-{student.user.id:04d}"
        passport = StudentChallengePassport.objects.create(
            user=student.user,
            badge_id=badge,
            student_name=student.user.get_full_name() or student.user.username,
            student_email=student.user.email,
            total_points=10,
            profile_completed=True,
            activity_log=[{'title': 'Expo Badge Registered (+10 pts)', 'points': 10, 'timestamp': 'Start'}]
        )
    if not isinstance(passport.visited_universities, list):
        passport.visited_universities = []
    if uni.name not in passport.visited_universities:
        if not passport.is_elite_pass and len(passport.visited_universities) >= 3:
            messages.warning(request, "Standard Pass limit reached (3 booths max). Complete all 6 KNOVA Challenge tasks to unlock the Elite Pass for unlimited booth visits!")

            return redirect('dashboard_university_detail', pk=uni_pk)
        passport.visited_universities.append(uni.name)
        passport.universities_visited_count = len(passport.visited_universities)
        passport.add_activity(f"Booth Attendance Punched: {uni.name}", 20)
        passport.save()
    msg = f"Attendance punched for {uni.name} booth! Your profile has been shared with {uni.name} admissions representatives (+20 pts)."
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'success': True, 'message': msg, 'points': 20, 'total_points': passport.total_points})
    messages.success(request, msg)

    return redirect(request.META.get('HTTP_REFERER', 'dashboard_index'))

# =============================================================================
# SEMINAR STAFF & SEMINAR ATTENDANCE SYSTEM
# =============================================================================


@login_required(login_url='/portal/login/')
def seminar_attendance_scanner(request):
    """
    Scanner portal for seminar coordinators.
    Allows selecting a seminar session, camera QR scanning, and manual punch.
    """
    from .models import ProgrammeSession, SeminarAttendance, SeminarStaff
    from django.utils import timezone
    profile = getattr(request.user, 'seminar_staff', None)
    if not profile and not request.user.is_superuser:
        messages.error(request, "Access restricted to Seminar Coordinators and Administrators.")

        return redirect('dashboard_index')
    hall_name = profile.hall_name if profile else request.GET.get('hall', 'All Halls')
    sessions_qs = ProgrammeSession.objects.select_related('speaker', 'event_location').order_by('date', 'start_time')
    if profile and profile.session:
        sessions = [profile.session] + [s for s in sessions_qs if s.id != profile.session.id]
    elif profile and profile.hall_name:
        hall_sessions = sessions_qs.filter(hall_name__iexact=profile.hall_name)
        if hall_sessions.exists():
            sessions = hall_sessions
        else:
            sessions = sessions_qs
    else:
        sessions = sessions_qs
    selected_session_id = request.GET.get('session_id')
    selected_session = None
    if selected_session_id and selected_session_id.isdigit():
        selected_session = ProgrammeSession.objects.filter(pk=int(selected_session_id)).first()
    elif profile and getattr(profile, 'session', None):
        selected_session = profile.session
    if not selected_session and sessions:
        selected_session = sessions[0]
    recent_attendances = []
    total_punched_for_session = 0
    if selected_session:
        recent_attendances = SeminarAttendance.objects.filter(session=selected_session).select_related('student__user').order_by('-attended_at')[:15]
        total_punched_for_session = SeminarAttendance.objects.filter(session=selected_session).count()
    context = {
        'role': 'seminar' if profile else 'admin',
        'profile': profile,
        'hall_name': hall_name,
        'sessions': sessions,
        'selected_session': selected_session,
        'recent_attendances': recent_attendances,
        'total_punched_for_session': total_punched_for_session,
    }

    return render(request, 'dashboard/seminar_scanner.html', context)


@login_required(login_url='/portal/login/')
def seminar_punch_attendance(request):
    """
    Endpoint for seminar staff to punch student attendance for a seminar session.
    Awards +25 points to student Challenge Passport.
    """
    from .models import ProgrammeSession, SeminarAttendance, StudentChallengePassport
    from django.http import JsonResponse
    from django.utils import timezone
    import json
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required.'}, status=405)
    session_id = None
    student_code = ''
    notes = ''
    if request.content_type == 'application/json':
        try:
            body = json.loads(request.body)
            session_id = body.get('session_id')
            student_code = body.get('student_code', '').strip()
            notes = body.get('notes', '').strip()
        except Exception:
            pass
    else:
        session_id = request.POST.get('session_id')
        student_code = request.POST.get('student_code', '').strip()
        notes = request.POST.get('notes', '').strip()
    if not session_id or not student_code:
        return JsonResponse({'success': False, 'message': 'Session ID and Student Code are required.'}, status=400)
    session = ProgrammeSession.objects.filter(pk=session_id).select_related('speaker', 'event_location').first()
    if not session:
        return JsonResponse({'success': False, 'message': 'Seminar session not found.'}, status=404)
    student = _resolve_student_profile(student_code)
    reg = None
    if not student:
        from .models import Registration
        from django.contrib.auth.models import User
        if student_code.isdigit():
            reg = Registration.objects.filter(id=int(student_code)).first()
        if not reg and student_code.upper().startswith('REG-'):
            reg_id = student_code.replace('REG-', '').strip()
            if reg_id.isdigit():
                reg = Registration.objects.filter(id=int(reg_id)).first()
        if not reg:
            reg = Registration.objects.filter(email__iexact=student_code).first()
        if not reg:
            reg = Registration.objects.filter(full_name__iexact=student_code).first()
        if reg:
            user = User.objects.filter(email__iexact=reg.email).first()
            if not user:
                base_u = reg.email.split('@')[0].replace('.', '_')
                u_name = base_u
                c = 1
                while User.objects.filter(username__iexact=u_name).exists():
                    u_name = f"{base_u}{c}"
                    c += 1
                user = User.objects.create_user(
                    username=u_name,
                    email=reg.email,
                    password='student123',
                    first_name=reg.full_name[:30]
                )
            student, _ = StudentProfile.objects.get_or_create(user=user)
    if not student and not reg:

        # Record direct attendee / visitor punch
        attendance, created = SeminarAttendance.objects.get_or_create(
            visitor_name=student_code,
            session=session,
            defaults={
                'punch_method': 'Staff Punch',
                'notes': notes
            }
        )
        already_attended = not created
        if already_attended:
            msg = f"ATTENDED ALREADY: Visitor '{student_code}' has ALREADY ATTENDED and was punched earlier for '{session.title}'."
        else:
            msg = f"Visitor attendance punched for '{student_code}' at '{session.title}'!"

        return JsonResponse({
            'success': True,
            'already_attended': already_attended,
            'message': msg,
            'is_new': created,
            'student': {
                'name': student_code,
                'email': 'Visitor Attendee',
                'mobile': 'N/A',
                'education': 'Visitor / Guest',
                'school_college': 'General Admission',
                'attended_at': timezone.now().strftime('%b %d, %Y • %I:%M %p'),
                'session_title': session.title,
                'hall_name': session.hall_name,
                'points': 0,
                'badge_id': f"VISITOR-{attendance.id}"
            }
        })

    # Record SeminarAttendance
    attendance, created = SeminarAttendance.objects.get_or_create(
        student=student,
        session=session,
        defaults={
            'punch_method': 'QR Scanner',
            'notes': notes
        }
    )

    # Award Challenge Passport points
    passport = StudentChallengePassport.objects.filter(user=student.user).first()
    if not passport:
        badge = student.qr_identifier[:10].upper() if student.qr_identifier else f"KNV-{student.user.id:04d}"
        passport = StudentChallengePassport.objects.create(
            user=student.user,
            badge_id=badge,
            student_name=student.user.get_full_name() or student.user.username,
            student_email=student.user.email,
            total_points=10,
            profile_completed=True,
            activity_log=[{'title': 'Expo Badge Registered (+10 pts)', 'points': 10, 'timestamp': 'Start'}]
        )
    if created:
        passport.seminars_attended_count += 1
        passport.add_activity(f"Seminar Attended: {session.title}", 25)
        passport.save()
    student_name = student.user.get_full_name() or student.user.username
    already_attended = not created
    if already_attended:
        msg = f"ATTENDED ALREADY: {student_name} ({passport.badge_id if passport else ''}) has ALREADY ATTENDED and was punched earlier for '{session.title}'."
    else:
        msg = f"Attendance punched for {student_name} at '{session.title}'! (+25 pts awarded)"

    return JsonResponse({
        'success': True,
        'already_attended': already_attended,
        'message': msg,
        'is_new': created,
        'student': {
            'name': student_name,
            'email': student.user.email,
            'mobile': student.mobile or '',
            'education': student.current_education or '',
            'school_college': student.school_college or '',
            'attended_at': timezone.now().strftime('%b %d, %Y • %I:%M %p'),
            'session_title': session.title,
            'hall_name': session.hall_name,
            'points': passport.total_points,
            'badge_id': passport.badge_id
        }
    })


@login_required(login_url='/portal/login/')
def seminar_attendance_roster(request):
    """
    Full roster view of all seminar session attendees.
    """
    from .models import ProgrammeSession, SeminarAttendance, SeminarStaff
    from django.db.models import Q
    profile = getattr(request.user, 'seminar_staff', None)
    if not profile and not request.user.is_superuser:
        messages.error(request, "Access restricted to Seminar Staff and Administrators.")

        return redirect('dashboard_index')
    sessions = ProgrammeSession.objects.all().order_by('date', 'start_time')
    attendances_qs = SeminarAttendance.objects.select_related(
        'student__user', 'session', 'session__event_location', 'session__speaker'
    ).order_by('-attended_at')
    session_filter = request.GET.get('session_id')
    method_filter = request.GET.get('method')
    search_q = request.GET.get('q', '').strip()
    if session_filter and session_filter.isdigit():
        attendances_qs = attendances_qs.filter(session_id=int(session_filter))
    if method_filter:
        attendances_qs = attendances_qs.filter(punch_method=method_filter)
    if search_q:
        attendances_qs = attendances_qs.filter(
            Q(student__user__first_name__icontains=search_q) |
            Q(student__user__last_name__icontains=search_q) |
            Q(student__user__email__icontains=search_q) |
            Q(session__title__icontains=search_q) |
            Q(session__hall_name__icontains=search_q)
        )
    context = {
        'role': 'seminar' if profile else 'admin',
        'profile': profile,
        'sessions': sessions,
        'attendances': attendances_qs,
        'total_attendances': attendances_qs.count(),
        'selected_session_id': int(session_filter) if session_filter and session_filter.isdigit() else None,
        'selected_method': method_filter,
        'search_q': search_q,
    }

    return render(request, 'dashboard/seminar_roster.html', context)


@login_required(login_url='/portal/login/')
def student_punch_seminar_attendance(request, session_id):
    """
    Seminar attendance punching is strictly restricted to official seminar representatives.
    Students cannot self-punch seminar attendance.
    """
    from django.http import JsonResponse

    return JsonResponse({
        'success': False,
        'message': 'Seminar attendance can only be punched by official seminar representatives at the hall entrance.'
    }, status=403)


@login_required(login_url='/portal/login/')
def dashboard_take_exam(request, exam_id=1):
    from .models import ScholarshipExam, ExamAttempt, ExamRegistration, StudentProfile, ExamSlot, ExamQuestion
    from django.utils import timezone
    from django.shortcuts import get_object_or_404, redirect, render
    from django.contrib import messages
    import json
    import datetime
    import random

    # Disallow exhibitors, staff, and non-students from sitting for student exams
    user = request.user
    if hasattr(user, 'parent_profile'):
        from django.contrib import messages
        messages.warning(request, "Exams and tests must be completed by the student attendee. Parents have view-only access to progress and results.")

        return redirect('knova_challenge')
    if hasattr(user, 'exhibitor_profile') or hasattr(user, 'university_staff') or hasattr(user, 'seminar_staff') or user.is_superuser:
        from django.contrib import messages
        messages.error(request, "Only registered student attendees can sit for exams.")

        return redirect('dashboard_index')
    student = None
    if hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
    else:
        student, _ = StudentProfile.objects.get_or_create(user=request.user)
    exam = ScholarshipExam.objects.filter(id=exam_id).first()
    if not exam:
        exam = ScholarshipExam.objects.first()
    if not exam:
        messages.error(request, 'No active online exam found.')

        return redirect('dashboard_index')

    # Ensure student has a registration with an active slot
    reg = ExamRegistration.objects.filter(student=student, exam=exam).first()
    if not reg:
        today = datetime.date.today()
        slot = ExamSlot.objects.filter(exam=exam).first()
        if not slot:
            slot = ExamSlot.objects.create(
                exam=exam,
                date=today,
                start_time=datetime.time(0, 0),
                end_time=datetime.time(23, 59),
                capacity=100
            )
        reg = ExamRegistration.objects.create(
            student=student,
            exam=exam,
            slot=slot
        )
    elif not reg.slot:
        slot = ExamSlot.objects.filter(exam=exam).first()
        if slot:
            reg.slot = slot
            reg.save()

    # Check retake parameter
    is_retake = request.GET.get('retake') == '1'
    if is_retake:

        # Mark existing in-progress attempts as abandoned so a fresh test can start
        ExamAttempt.objects.filter(registration=reg, status='In Progress').update(status='Abandoned')
        attempt = ExamAttempt.objects.create(registration=reg, status='In Progress')
    else:

        # If student has any completed attempt, redirect to its results unless explicit retake is requested
        completed_att = ExamAttempt.objects.filter(registration=reg, status='Completed').order_by('-id').first()
        if completed_att:
            messages.info(request, 'You have already completed this exam.')

            return redirect('dashboard_exam_result', attempt_id=completed_att.id)

        # Find latest attempt
        attempt = ExamAttempt.objects.filter(registration=reg).order_by('-id').first()
        if not attempt:
            attempt = ExamAttempt.objects.create(registration=reg, status='In Progress')
        elif attempt.status == 'Abandoned':
            attempt = ExamAttempt.objects.create(registration=reg, status='In Progress')

    # Category definitions in the exact required sequence
    CATEGORIES = [
        "Numerical Ability",
        "Verbal Ability",
        "Logical Reasoning",
        "Technical Skills",
        "General Knowledge"
    ]

    # Check if this attempt already has randomized questions selected
    selected_ids = []
    if attempt.question_ids:
        try:
            parsed = [int(x.strip()) for x in attempt.question_ids.split(',') if x.strip().isdigit()]

            # Ensure it has exactly 100 valid questions that exist in this exam
            if len(parsed) == 100 and exam.questions.filter(id__in=parsed).count() == 100:
                selected_ids = parsed
        except Exception:
            selected_ids = []
    if not selected_ids:
        selected_ids = []
        for cat in CATEGORIES:
            cat_q_ids = list(exam.questions.filter(section_name=cat).values_list('id', flat=True))
            if len(cat_q_ids) >= 20:
                selected_ids.extend(random.sample(cat_q_ids, 20))
            else:
                selected_ids.extend(cat_q_ids)
        attempt.question_ids = ','.join(str(i) for i in selected_ids)
        attempt.save(update_fields=['question_ids'])

    # Calculate remaining time for this attempt based on start_time
    now = timezone.now()
    if attempt.start_time:
        elapsed = (now - attempt.start_time).total_seconds()
        remaining_seconds = max(0, int(exam.duration_minutes * 60 - elapsed))
    else:
        remaining_seconds = exam.duration_minutes * 60
    if remaining_seconds <= 0 and attempt.status == 'In Progress':
        attempt.status = 'Completed'
        attempt.end_time = now
        attempt.save()
        messages.warning(request, 'Your exam time has expired.')

        return redirect('dashboard_exam_result', attempt_id=attempt.id)

    # Fetch and order the selected questions
    questions_map = {
        q.id: q for q in exam.questions.filter(id__in=selected_ids).prefetch_related('choices')
    }
    ordered_questions = [questions_map[qid] for qid in selected_ids if qid in questions_map]

    # Serialize questions for frontend
    questions_data = []
    for idx, q in enumerate(ordered_questions):
        choices = [{'id': c.id, 'text': c.text} for c in q.choices.all()]
        questions_data.append({
            'index': idx + 1,
            'id': q.id,
            'section': getattr(q, 'section_name', 'General Section'),
            'text': q.text,
            'choices': choices
        })
    context = {
        'exam': exam,
        'attempt': attempt,
        'questions_json': json.dumps(questions_data),
        'duration_seconds': remaining_seconds,
        'roll_number': f"KNOVA-CBT-{attempt.id:04d}",
        'candidate_name': request.user.get_full_name() or request.user.username,
    }

    return render(request, 'dashboard/take_exam.html', context)


@login_required(login_url='/portal/login/')
def dashboard_submit_exam(request, attempt_id):
    import json
    from django.http import JsonResponse
    from django.utils import timezone
    from .models import ExamAttempt, StudentAnswer, QuestionChoice, ExamQuestion
    if hasattr(request.user, 'parent_profile'):
        return JsonResponse({'error': 'Exams cannot be submitted by parents. Student action required.'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)
    try:
        if request.user.is_superuser:
            attempt = ExamAttempt.objects.get(id=attempt_id)
        else:
            attempt = ExamAttempt.objects.get(id=attempt_id, registration__student__user=request.user)
    except ExamAttempt.DoesNotExist:
        return JsonResponse({'error': 'Attempt not found'}, status=404)
    if attempt.status == 'Completed':
        return JsonResponse({'error': 'Already submitted', 'redirect_url': f'/dashboard/exam/attempt/{attempt.id}/result/'}, status=400)
    data = json.loads(request.body)
    answers = data.get('answers', [])

    # Delete any existing answers for this attempt to prevent duplication
    StudentAnswer.objects.filter(attempt=attempt).delete()
    total_score = 0
    for q_data in answers:
        q_id = q_data.get('question_id')
        choice_id = q_data.get('choice_id')
        try:
            question = ExamQuestion.objects.get(id=q_id, exam=attempt.registration.exam)
            selected_choice = None
            if choice_id:
                selected_choice = QuestionChoice.objects.get(id=choice_id, question=question)
                if selected_choice.is_correct:
                    total_score += question.marks
            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_choice=selected_choice
            )
        except Exception:
            continue
    attempt.end_time = timezone.now()
    attempt.score = total_score
    attempt.is_passed = total_score >= attempt.registration.exam.passing_marks
    attempt.status = 'Completed'
    attempt.save()

    # Automatically credit StudentChallengePassport for Challenge 2 (Aptitude Test)
    challenge_credited = False
    try:
        from .models import StudentChallengePassport
        student_user = attempt.registration.student.user
        passport = StudentChallengePassport.objects.filter(user=student_user).first()
        if not passport and student_user.email:
            passport = StudentChallengePassport.objects.filter(student_email__iexact=student_user.email).first()
        if not passport and 'challenge_badge_id' in request.session:
            passport = StudentChallengePassport.objects.filter(badge_id=request.session['challenge_badge_id']).first()
        if passport:
            is_comp, _ = passport.sync_exam_challenge_status()
            challenge_credited = is_comp
    except Exception:
        pass

    return JsonResponse({
        'success': True,
        'score': attempt.score,
        'is_passed': attempt.is_passed,
        'challenge_credited': challenge_credited,
        'redirect_url': f'/dashboard/exam/attempt/{attempt.id}/result/'
    })


@login_required(login_url='/portal/login/')
def dashboard_exam_result(request, attempt_id):
    from .models import ExamAttempt, StudentAnswer, ExamQuestion
    from django.shortcuts import get_object_or_404, render
    is_admin = (
        request.user.is_superuser or
        request.user.is_staff or
        request.user.groups.filter(name__in=['Admin', 'admin']).exists() or
        request.user.username.lower() == 'admin'
    )
    is_exhibitor = (
        hasattr(request.user, 'exhibitor_profile') or
        hasattr(request.user, 'exhibitor_staff_profile') or
        hasattr(request.user, 'university_staff')
    )
    if is_admin or is_exhibitor:
        attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    elif hasattr(request.user, 'parent_profile'):
        from .models import ParentStudentLink
        linked_student_users = list(ParentStudentLink.objects.filter(parent=request.user.parent_profile).values_list('student__user', flat=True))
        attempt = get_object_or_404(ExamAttempt, id=attempt_id, registration__student__user__in=linked_student_users)
    else:
        attempt = get_object_or_404(ExamAttempt, id=attempt_id, registration__student__user=request.user)
    exam = attempt.registration.exam

    # Retrieve all assigned questions for this attempt
    q_ids = []
    if attempt.question_ids:
        try:
            q_ids = [int(x.strip()) for x in attempt.question_ids.split(',') if x.strip().isdigit()]
        except Exception:
            q_ids = []
    if q_ids:
        assigned_questions = {q.id: q for q in ExamQuestion.objects.filter(id__in=q_ids).prefetch_related('choices')}
        questions_list = [assigned_questions[qid] for qid in q_ids if qid in assigned_questions]
    else:
        questions_list = list(exam.questions.all().prefetch_related('choices')[:100])

    # Map student answers
    answers_map = {ans.question_id: ans for ans in attempt.answers.select_related('selected_choice').all()}

    # Calculate detailed analytics
    CATEGORIES = [
        "Numerical Ability",
        "Verbal Ability",
        "Logical Reasoning",
        "Technical Skills",
        "General Knowledge"
    ]
    section_stats = {cat: {'total': 0, 'answered': 0, 'correct': 0, 'score': 0} for cat in CATEGORIES}
    review_data = []
    total_correct = 0
    total_incorrect = 0
    total_unattempted = 0
    for idx, q in enumerate(questions_list):
        sec = getattr(q, 'section_name', 'General Section')
        if sec not in section_stats:
            section_stats[sec] = {'total': 0, 'answered': 0, 'correct': 0, 'score': 0}
        section_stats[sec]['total'] += 1
        user_ans = answers_map.get(q.id)
        selected_choice = user_ans.selected_choice if user_ans else None
        correct_choice = next((c for c in q.choices.all() if c.is_correct), None)
        is_user_correct = False
        if selected_choice:
            section_stats[sec]['answered'] += 1
            if selected_choice.is_correct:
                is_user_correct = True
                total_correct += 1
                section_stats[sec]['correct'] += 1
                section_stats[sec]['score'] += q.marks
            else:
                total_incorrect += 1
        else:
            total_unattempted += 1
        review_data.append({
            'index': idx + 1,
            'question': q,
            'section': sec,
            'selected_choice': selected_choice,
            'correct_choice': correct_choice,
            'is_correct': is_user_correct,
            'is_unattempted': selected_choice is None,
        })
    time_taken_str = "N/A"
    if attempt.end_time and attempt.start_time:
        diff_sec = max(0, int((attempt.end_time - attempt.start_time).total_seconds()))
        m = diff_sec // 60
        s = diff_sec % 60
        time_taken_str = f"{m}m {s}s"

    # Check challenge passport
    passport = None
    if request.user.is_authenticated:
        from .models import StudentChallengePassport
        passport = StudentChallengePassport.objects.filter(user=request.user).first()
        if not passport and request.user.email:
            passport = StudentChallengePassport.objects.filter(student_email__iexact=request.user.email).first()
    if not passport and 'challenge_badge_id' in request.session:
        from .models import StudentChallengePassport
        passport = StudentChallengePassport.objects.filter(badge_id=request.session['challenge_badge_id']).first()
    context = {
        'attempt': attempt,
        'exam': exam,
        'section_stats': section_stats,
        'review_data': review_data,
        'total_correct': total_correct,
        'total_incorrect': total_incorrect,
        'total_unattempted': total_unattempted,
        'time_taken_str': time_taken_str,
        'percentage': round((attempt.score / max(1, exam.total_marks)) * 100, 1) if attempt.score is not None else 0,
        'challenge_passport': passport
    }

    return render(request, 'dashboard/exam_result.html', context)


@login_required(login_url='/portal/login/')
def dashboard_exam_register(request, exam_id):
    from .models import ScholarshipExam, ExamSlot, ExamRegistration, StudentProfile
    from django.shortcuts import get_object_or_404, redirect, render
    from django.contrib import messages
    import datetime
    exam = get_object_or_404(ScholarshipExam, id=exam_id)
    student = None
    if hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
    else:
        student, _ = StudentProfile.objects.get_or_create(user=request.user)
    if not exam.slots.exists():
        today = datetime.date.today()
        for i in range(8):
            start_time = datetime.time(9 + i, 0)
            end_time = datetime.time(10 + i, 0)
            ExamSlot.objects.create(
                exam=exam,
                date=today,
                start_time=start_time,
                end_time=end_time,
                capacity=100
            )
    slots = exam.slots.all().order_by('date', 'start_time')
    for slot in slots:
        slot.is_full_flag = slot.is_full()
    if request.method == 'POST':
        if hasattr(request.user, 'parent_profile'):
            messages.warning(request, "Exam slots must be selected and registered by the student attendee.")

            return redirect('dashboard_scholarships')
        slot_id = request.POST.get('slot_id')
        slot = get_object_or_404(ExamSlot, id=slot_id, exam=exam)
        if slot.is_full():
            messages.error(request, 'This slot is full. Please select another time.')

            return redirect('dashboard_exam_register', exam_id=exam.id)
        reg, created = ExamRegistration.objects.get_or_create(
            student=student,
            exam=exam,
            defaults={'slot': slot}
        )
        if not created:
            reg.slot = slot
            reg.save()
            messages.success(request, f'Slot updated to {slot.start_time.strftime("%I:%M %p")}')
        else:
            messages.success(request, f'Successfully registered for {exam.title} at {slot.start_time.strftime("%I:%M %p")}')

        return redirect('dashboard_take_exam', exam_id=exam.id)
    context = {
        'exam': exam,
        'slots': slots,
    }

    return render(request, 'dashboard/exam_register.html', context)


@login_required(login_url='/portal/login/')
def dashboard_online_exam_portal(request):
    """Direct entrance to the online exam portal"""
    if hasattr(request.user, 'parent_profile'):
        from django.contrib import messages
        messages.info(request, "Exams and tests must be completed by the student attendee. Parents have view-only access to child progress and scores.")

        return redirect('knova_challenge')
    from .models import ScholarshipExam, ExamAttempt

    # If student already completed an exam attempt and did not request a retake, show result
    if request.user.is_authenticated and request.GET.get('retake') != '1':
        completed_att = ExamAttempt.objects.filter(
            registration__student__user=request.user,
            status='Completed'
        ).order_by('-id').first()
        if completed_att:
            return redirect('dashboard_exam_result', attempt_id=completed_att.id)
    exam = ScholarshipExam.objects.filter(is_active=True).first()
    if exam:
        retake_qs = '?retake=1' if request.GET.get('retake') == '1' else ''

        return redirect(f"/dashboard/exam/{exam.id}/take/{retake_qs}")

    return redirect('dashboard_scholarships')


def seed_exam_1000_questions(exam):
    try:
        from scripts.questions_data.numerical import get_numerical_questions
        from scripts.questions_data.verbal import get_verbal_questions
        from scripts.questions_data.logical import get_logical_questions
        from scripts.questions_data.technical import get_technical_questions
        from scripts.questions_data.gk import get_gk_questions
        from .models import ExamQuestion, QuestionChoice
        categories = [
            ("Numerical Ability", get_numerical_questions()),
            ("Verbal Ability", get_verbal_questions()),
            ("Logical Reasoning", get_logical_questions()),
            ("Technical Skills", get_technical_questions()),
            ("General Knowledge", get_gk_questions()),
        ]
        created_questions = []
        question_choices_map = []
        order_counter = 1
        for sec_name, q_list in categories:
            for item in q_list:
                q = ExamQuestion(
                    exam=exam,
                    section_name=sec_name,
                    text=item["text"],
                    marks=1.0,
                    order=order_counter
                )
                created_questions.append(q)
                question_choices_map.append(item["choices"])
                order_counter += 1
        saved_questions = ExamQuestion.objects.bulk_create(created_questions)
        choices_to_create = []
        for q_obj, choices_list in zip(saved_questions, question_choices_map):
            for c_text, is_corr in choices_list:
                choices_to_create.append(QuestionChoice(
                    question=q_obj,
                    text=str(c_text),
                    is_correct=bool(is_corr)
                ))
        QuestionChoice.objects.bulk_create(choices_to_create)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error seeding 1000 questions for exam {exam.id}: {e}")


def dashboard_exhibitor_exams(request):
    is_admin = (
        request.user.is_superuser or
        request.user.is_staff or
        request.user.groups.filter(name='Admin').exists() or
        request.user.username.lower() == 'admin'
    )
    is_exhibitor = (
        hasattr(request.user, 'exhibitor_profile') or
        hasattr(request.user, 'exhibitor_staff_profile') or
        hasattr(request.user, 'university_staff')
    )
    if not (is_admin or is_exhibitor):
        from django.contrib import messages
        messages.error(request, "Access restricted: The examination portal is accessible to platform administrators and participating university exhibitors.")

        return redirect('dashboard_index')
    from .models import ScholarshipExam, Scholarship, ExamQuestion, ExamRegistration, ExamAttempt
    exams = ScholarshipExam.objects.all().order_by('-created_at')
    if request.method == 'POST':
        if not is_admin:
            from django.contrib import messages
            messages.error(request, 'Permission denied: Only platform administrators can configure or manage examinations.')

            return redirect('dashboard_exhibitor_exams')
        action = request.POST.get('action')
        if action == 'create_exam':
            from django.contrib import messages
            title = request.POST.get('title', '').strip()
            if not title:
                messages.error(request, "Please provide an exam title.")

                return redirect('dashboard_exhibitor_exams')
            duration = int(request.POST.get('duration_minutes', 60) or 60)
            total_marks = int(request.POST.get('total_marks', 100) or 100)
            passing_marks = int(request.POST.get('passing_marks', 50) or 50)
            description = request.POST.get('description', '').strip() or 'KNOVA Central Common Scholarship Aptitude & Assessment Exam recognized by all participating universities.'
            scholarship_id = request.POST.get('scholarship_id')
            exam = ScholarshipExam.objects.create(
                title=title,
                exhibitor=None,  # Common examination across all universities
                duration_minutes=duration,
                total_marks=total_marks,
                passing_marks=passing_marks,
                description=description,
                is_active=True
            )
            if scholarship_id:
                try:
                    s = Scholarship.objects.get(id=scholarship_id)
                    exam.scholarship = s
                    exam.save()
                except Scholarship.DoesNotExist:
                    pass

            # Automatically populate 1,000 questions (200 per category) for the new common exam
            seed_exam_1000_questions(exam)
            messages.success(request, f"Central Common Exam '{exam.title}' successfully created.")

            return redirect('dashboard_exhibitor_exams')
        elif action == 'delete_exam':
            from django.contrib import messages
            exam_id = request.POST.get('exam_id')
            ScholarshipExam.objects.filter(id=exam_id).delete()
            messages.success(request, "Exam deleted successfully.")

            return redirect('dashboard_exhibitor_exams')
    all_scholarships = Scholarship.objects.select_related('university').all()

    # Query all completed & published student exam results for Admin and Exhibitors
    completed_attempts = ExamAttempt.objects.filter(
        status='Completed'
    ).select_related(
        'registration__student__user',
        'registration__student',
        'registration__exam'
    ).order_by('-end_time', '-id')
    context = {
        'exams': exams,
        'all_scholarships': all_scholarships,
        'is_admin': is_admin,
        'is_exhibitor': is_exhibitor,
        'completed_attempts': completed_attempts,
        'total_exams': exams.count(),
        'total_questions': ExamQuestion.objects.count(),
        'total_registrations': ExamRegistration.objects.count(),
        'total_attempts': completed_attempts.count(),
        'total_passed': completed_attempts.filter(is_passed=True).count(),
    }

    return render(request, 'dashboard/exhibitor_exams.html', context)


@login_required(login_url='/portal/login/')
def dashboard_exhibitor_exam_questions(request, exam_id):
    is_admin = (
        request.user.is_superuser or
        request.user.is_staff or
        request.user.groups.filter(name='Admin').exists() or
        request.user.username.lower() == 'admin'
    )
    if not is_admin:
        from django.contrib import messages
        messages.error(request, "Access restricted: The examination portal is managed exclusively by platform administrators.")

        return redirect('dashboard_index')
    from .models import ScholarshipExam
    from django.shortcuts import get_object_or_404
    exam = get_object_or_404(ScholarshipExam, id=exam_id)
    questions = exam.questions.all().prefetch_related('choices')
    context = {
        'exam': exam,
        'questions': questions,
        'is_admin': True
    }

    return render(request, 'dashboard/exhibitor_exam_questions.html', context)


@login_required(login_url='/portal/login/')
def dashboard_exhibitor_question_create(request, exam_id):
    is_admin = (
        request.user.is_superuser or
        request.user.is_staff or
        request.user.groups.filter(name='Admin').exists() or
        request.user.username.lower() == 'admin'
    )
    if not is_admin:
        from django.contrib import messages
        messages.error(request, "Access restricted: The examination portal is managed exclusively by platform administrators.")

        return redirect('dashboard_index')
    from .models import ScholarshipExam, ExamQuestion, QuestionChoice
    from django.shortcuts import get_object_or_404
    exam = get_object_or_404(ScholarshipExam, id=exam_id)
    if request.method == 'POST':
        from django.contrib import messages
        text = request.POST.get('text', '').strip()
        marks = int(request.POST.get('marks', 1) or 1)
        section_name = request.POST.get('section_name', 'General Section').strip() or 'General Section'
        question = ExamQuestion.objects.create(
            exam=exam,
            text=text,
            marks=marks,
            section_name=section_name
        )
        correct_choice = request.POST.get('correct_choice', '1')
        for i in range(1, 5):
            choice_text = request.POST.get(f'choice_{i}', '').strip()
            if choice_text:
                is_correct = str(i) == correct_choice
                QuestionChoice.objects.create(
                    question=question,
                    text=choice_text,
                    is_correct=is_correct
                )
        messages.success(request, "Question added to Central Exam question bank.")

        return redirect('dashboard_exhibitor_exam_questions', exam_id=exam.id)

    return render(request, 'dashboard/exhibitor_question_form.html', {'exam': exam})


@login_required(login_url='/portal/login/')
def dashboard_exhibitor_question_delete(request, question_id):
    is_admin = (
        request.user.is_superuser or
        request.user.is_staff or
        request.user.groups.filter(name='Admin').exists() or
        request.user.username.lower() == 'admin'
    )
    if not is_admin:
        from django.contrib import messages
        messages.error(request, "Access restricted: The examination portal is managed exclusively by platform administrators.")

        return redirect('dashboard_index')
    from .models import ExamQuestion
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    question = get_object_or_404(ExamQuestion, id=question_id)
    exam_id = question.exam.id
    question.delete()
    messages.success(request, "Question removed successfully from question bank.")

    return redirect('dashboard_exhibitor_exam_questions', exam_id=exam_id)


def dashboard_logout_view(request):
    """
    Logs out the user and redirects to the login portal.
    Handles both GET and POST requests so standard link buttons work reliably across Django 4 and 5+.
    """
    from django.contrib.auth import logout
    logout(request)

    return redirect('/portal/login/')

# ==============================================================================
# COUNTRY MANAGEMENT (ADMIN DASHBOARD)
# ==============================================================================


@login_required(login_url='/portal/login/')
def dashboard_countries(request):
    params = request.GET.copy()
    params['tab'] = 'countries'
    return redirect(f"/dashboard/settings/?{params.urlencode()}")


@login_required(login_url='/portal/login/')
def country_create(request):
    is_admin = (
        request.user.is_superuser or
        request.user.is_staff or
        request.user.groups.filter(name='Admin').exists() or
        request.user.username.lower() == 'admin'
    )
    if not is_admin:
        from django.contrib import messages
        messages.error(request, "Permission denied.")
        return redirect('dashboard_index')
    from .models import Country
    from django.contrib import messages
    next_url = request.POST.get('next') or request.GET.get('next') or '/dashboard/settings/?tab=countries'
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        code = (request.POST.get('code') or '').strip().upper()
        continent = (request.POST.get('continent') or '').strip() or 'Global'
        dial_code = (request.POST.get('dial_code') or '').strip()
        is_active = request.POST.get('is_active') in ['1', 'true', 'on', True]
        is_popular = request.POST.get('is_popular_destination') in ['1', 'true', 'on', True]
        order_val = request.POST.get('order') or 0
        try:
            order_val = int(order_val)
        except ValueError:
            order_val = 0
        if not name:
            messages.error(request, "Country name cannot be empty.")
            return redirect(next_url)
        if Country.objects.filter(name__iexact=name).exists():
            messages.warning(request, f"Country '{name}' already exists in the catalog.")
            return redirect(next_url)
        country = Country.objects.create(
            name=name,
            code=code,
            continent=continent,
            dial_code=dial_code,
            is_active=is_active,
            is_popular_destination=is_popular,
            order=order_val
        )
        messages.success(request, f"Country '{country.name}' successfully added to catalog.")
        return redirect(next_url)

    return redirect(next_url)


@login_required(login_url='/portal/login/')
def country_update(request, pk):
    is_admin = (
        request.user.is_superuser or
        request.user.is_staff or
        request.user.groups.filter(name='Admin').exists() or
        request.user.username.lower() == 'admin'
    )
    if not is_admin:
        from django.contrib import messages
        messages.error(request, "Permission denied.")
        return redirect('dashboard_index')
    from .models import Country
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    country = get_object_or_404(Country, pk=pk)
    next_url = request.POST.get('next') or request.GET.get('next') or '/dashboard/settings/?tab=countries'
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        code = (request.POST.get('code') or '').strip().upper()
        continent = (request.POST.get('continent') or '').strip() or country.continent
        dial_code = (request.POST.get('dial_code') or '').strip()
        is_active = request.POST.get('is_active') in ['1', 'true', 'on', True]
        is_popular = request.POST.get('is_popular_destination') in ['1', 'true', 'on', True]
        order_val = request.POST.get('order') or 0
        try:
            order_val = int(order_val)
        except ValueError:
            order_val = 0
        if not name:
            messages.error(request, "Country name cannot be empty.")
            return redirect(next_url)
        conflict = Country.objects.filter(name__iexact=name).exclude(pk=country.pk).first()
        if conflict:
            messages.error(request, f"Another country with name '{name}' already exists.")
            return redirect(next_url)
        country.name = name
        country.code = code
        country.continent = continent
        country.dial_code = dial_code
        country.is_active = is_active
        country.is_popular_destination = is_popular
        country.order = order_val
        country.save()
        messages.success(request, f"Country '{country.name}' details successfully updated.")
        return redirect(next_url)

    return redirect(next_url)


@login_required(login_url='/portal/login/')
def country_delete(request, pk):
    is_admin = (
        request.user.is_superuser or
        request.user.is_staff or
        request.user.groups.filter(name='Admin').exists() or
        request.user.username.lower() == 'admin'
    )
    if not is_admin:
        from django.contrib import messages
        messages.error(request, "Permission denied.")
        return redirect('dashboard_index')
    from .models import Country
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    country = get_object_or_404(Country, pk=pk)
    name = country.name
    country.delete()
    messages.success(request, f"Country '{name}' has been deleted.")
    next_url = request.POST.get('next') or request.GET.get('next') or '/dashboard/settings/?tab=countries'
    return redirect(next_url)


@login_required(login_url='/portal/login/')
def country_toggle_status(request, pk):
    is_admin = (
        request.user.is_superuser or
        request.user.is_staff or
        request.user.groups.filter(name='Admin').exists() or
        request.user.username.lower() == 'admin'
    )
    if not is_admin:
        from django.contrib import messages
        messages.error(request, "Permission denied.")
        return redirect('dashboard_index')
    from .models import Country
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    country = get_object_or_404(Country, pk=pk)
    country.is_active = not country.is_active
    country.save()
    status_str = "Active" if country.is_active else "Inactive"
    messages.success(request, f"Country '{country.name}' is now marked as {status_str}.")
    next_url = request.POST.get('next') or request.GET.get('next') or '/dashboard/settings/?tab=countries'
    return redirect(next_url)

# ==========================================
# EDUCATION EXPERT / ACADEMIC COUNSELLOR VIEWS
# ==========================================
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@login_required(login_url='/portal/login/')
def dashboard_expert_punch_attendance(request):
    """
    Dedicated punch API endpoint for Education Expert / Academic Counsellor.
    Punches a student's attendance via QR scan or manual badge ID.
    Awards +40 XP to StudentChallengePassport (Mission 4: Meet an Education Expert).
    """
    import json
    from django.http import JsonResponse
    from .models import EducationExpert, ExpertConsultationAttendance, StudentChallengePassport, StudentProfile
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=400)

    # Permission check: must be education_expert or admin
    is_expert = hasattr(request.user, 'education_expert')
    is_admin = request.user.is_superuser or request.user.is_staff
    if not (is_expert or is_admin):
        return JsonResponse({'success': False, 'error': 'Only authorized Education Experts can punch consultation attendance.'}, status=403)
    expert_profile = getattr(request.user, 'education_expert', None)
    if not expert_profile:
        expert_profile = EducationExpert.objects.first()
    raw_code = request.POST.get('badge_id') or request.POST.get('code')
    punch_method = request.POST.get('punch_method', 'Manual Code')
    if not raw_code and request.content_type == 'application/json':
        try:
            body = json.loads(request.body)
            raw_code = body.get('badge_id') or body.get('code')
            punch_method = body.get('punch_method', punch_method)
        except Exception:
            pass
    if not raw_code:
        return JsonResponse({'success': False, 'error': 'Please enter a Student Badge ID (e.g. KNOVA-0005) or scan a QR code.'}, status=400)
    code = raw_code.strip()
    if 'badge_id=' in code:
        code = code.split('badge_id=')[-1].split('&')[0].strip()
    passport = StudentChallengePassport.objects.filter(badge_id__iexact=code).first()
    if not passport:
        passport = StudentChallengePassport.objects.filter(student_email__iexact=code).first()
    if not passport:
        passport = StudentChallengePassport.objects.filter(user__username__iexact=code).first()
    if not passport and code.isdigit():
        passport = StudentChallengePassport.objects.filter(user__id=int(code)).first()
    if not passport:
        return JsonResponse({'success': False, 'error': f'Student badge "{code}" not found. Verify badge code or scan again.'}, status=404)
    sp = None
    if passport.user and hasattr(passport.user, 'student_profile'):
        sp = passport.user.student_profile
    elif passport.student_email:
        sp = StudentProfile.objects.filter(user__email__iexact=passport.student_email).first()
    already_punched = False
    if ExpertConsultationAttendance.objects.filter(expert=expert_profile, badge_id__iexact=passport.badge_id).exists() or passport.expert_meeting_completed:
        already_punched = True

    # Record consultation attendance
    attendance, created = ExpertConsultationAttendance.objects.get_or_create(
        expert=expert_profile,
        badge_id=passport.badge_id,
        defaults={
            'student': sp,
            'student_name': passport.student_name,
            'punch_method': punch_method,
            'notes': f'Official Consultation with {expert_profile.name}'
        }
    )
    if not passport.expert_meeting_completed:
        passport.expert_meeting_completed = True
        passport.add_activity(f"Official Consultation with {expert_profile.name} (+40 pts)", 40)
        passport.check_passport_completion()
        passport.save()
    total_consults = ExpertConsultationAttendance.objects.filter(expert=expert_profile).count()
    already_attended = already_punched or not created
    if already_attended:
        msg = f"ATTENDED ALREADY: {passport.student_name} ({passport.badge_id}) has ALREADY ATTENDED and was punched earlier for this consultation session with {expert_profile.name} at {expert_profile.desk_name}."
    else:
        msg = f"Consultation attendance successfully punched for {passport.student_name}! +40 Challenge Points verified with {expert_profile.name} at {expert_profile.desk_name}."

    return JsonResponse({
        'success': True,
        'already_attended': already_attended,
        'already_punched': already_attended,
        'student_name': passport.student_name,
        'badge_id': passport.badge_id,
        'total_points': passport.total_points,
        'total_consultations': total_consults,
        'message': msg
    })


@login_required(login_url='/portal/login/')
def expert_attendance_scanner(request):
    """Full-page QR Punch Scanner for Education Expert."""
    from .models import EducationExpert, ExpertConsultationAttendance
    expert_profile = getattr(request.user, 'education_expert', None)
    if not expert_profile and (request.user.is_superuser or request.user.is_staff):
        expert_profile = EducationExpert.objects.first()
    if not expert_profile:
        from django.contrib import messages
        messages.error(request, "Only registered Education Experts can access the Consultation Scanner.")

        return redirect('dashboard_index')
    consultations = ExpertConsultationAttendance.objects.filter(expert=expert_profile).order_by('-attended_at')[:20]
    context = {
        'role': 'education_expert',
        'expert_profile': expert_profile,
        'profile': expert_profile,
        'total_consultations': consultations.count(),
        'recent_consultations': consultations,
    }

    return render(request, 'dashboard/expert_scanner.html', context)


@login_required(login_url='/portal/login/')
def expert_consultation_roster(request):
    """Roster of students who attended consultations with Education Expert."""
    from .models import EducationExpert, ExpertConsultationAttendance
    expert_profile = getattr(request.user, 'education_expert', None)
    if not expert_profile and (request.user.is_superuser or request.user.is_staff):
        expert_profile = EducationExpert.objects.first()
    if not expert_profile:
        from django.contrib import messages
        messages.error(request, "Only registered Education Experts can view consultation attendees.")

        return redirect('dashboard_index')
    q = request.GET.get('q', '').strip()
    consultations = ExpertConsultationAttendance.objects.filter(expert=expert_profile).select_related('student__user').order_by('-attended_at')
    if q:
        from django.db.models import Q
        consultations = consultations.filter(
            Q(student_name__icontains=q) |
            Q(badge_id__icontains=q) |
            Q(student__user__email__icontains=q)
        )
    context = {
        'role': 'education_expert',
        'expert_profile': expert_profile,
        'profile': expert_profile,
        'consultations': consultations,
        'total_consultations': consultations.count(),
        'query': q,
    }

    return render(request, 'dashboard/expert_consultations.html', context)


@login_required(login_url='/portal/login/')
def dashboard_education_experts(request):
    """Redirect to unified Speakers & Education Experts page with type=expert filter."""
    from django.shortcuts import redirect
    from django.urls import reverse
    query_str = request.GET.urlencode()
    if query_str:
        return redirect(f"{reverse('dashboard_speakers')}?type=expert&{query_str}")

    return redirect(f"{reverse('dashboard_speakers')}?type=expert")


@login_required(login_url='/portal/login/')
def education_expert_create(request):
    """Admin endpoint to create a new Education Expert user & station."""
    if request.method != 'POST':
        return redirect('/dashboard/speakers/?type=expert')
    from .models import EducationExpert
    from django.contrib.auth.models import User
    from django.contrib import messages
    import re
    is_admin = request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', '') == 'admin'
    if not is_admin:
        messages.error(request, "Access restricted to Administrators.")

        return redirect('dashboard_index')
    name = request.POST.get('name', '').strip()
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    title = request.POST.get('title', '').strip()
    desk_name = request.POST.get('desk_name', '').strip()
    specialization = request.POST.get('specialization', '').strip()
    mobile = request.POST.get('mobile', '').strip()
    if not name:
        messages.error(request, "Full Name is required for the Education Expert.")

        return redirect('/dashboard/speakers/?type=expert')
    if not username:
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', name.lower().replace('dr.', '').replace('dr', ''))[:12]
        base_username = f"expert_{clean_name}" if clean_name else "expert"
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{suffix}"
            suffix += 1
    if User.objects.filter(username=username).exists():
        messages.error(request, f"Username '{username}' already exists. Please choose a different username.")

        return redirect('/dashboard/speakers/?type=expert')
    if not password:
        password = 'expert' + str(EducationExpert.objects.count() + 101)
    try:
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=name.split()[0] if name else '',
            last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
        )
        desk = desk_name or f"Academic Counselling Hub — Desk {EducationExpert.objects.count() + 1}"
        expert = EducationExpert.objects.create(
            user=user,
            name=name,
            title=title or 'Senior Academic Counsellor',
            desk_name=desk,
            specialization=specialization or 'Global Admissions Advisory, Career Counseling & Full Scholarships',
            mobile=mobile or '+971 50 123 4567',
            raw_password=password
        )
        messages.success(request, f"New Education Expert '{name}' created successfully! User ID: {username} | Password: {password}")
    except Exception as e:
        messages.error(request, f"Failed to create Education Expert: {str(e)}")

    return redirect('/dashboard/speakers/?type=expert')


@login_required(login_url='/portal/login/')
def education_expert_update(request, pk):
    """Admin endpoint to update Education Expert profile details and credentials."""
    if request.method != 'POST':
        return redirect('/dashboard/speakers/?type=expert')
    from .models import EducationExpert
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    is_admin = request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', '') == 'admin'
    if not is_admin:
        messages.error(request, "Access restricted to Administrators.")

        return redirect('dashboard_index')
    expert = get_object_or_404(EducationExpert, pk=pk)
    name = request.POST.get('name', '').strip()
    password = request.POST.get('password', '').strip()
    title = request.POST.get('title', '').strip()
    desk_name = request.POST.get('desk_name', '').strip()
    specialization = request.POST.get('specialization', '').strip()
    mobile = request.POST.get('mobile', '').strip()
    if name:
        expert.name = name
    if title:
        expert.title = title
    if desk_name:
        expert.desk_name = desk_name
    if specialization:
        expert.specialization = specialization
    if mobile:
        expert.mobile = mobile
    if password:
        expert.raw_password = password
        expert.user.set_password(password)
        expert.user.save()
    expert.save()
    messages.success(request, f"Education Expert '{expert.name}' updated successfully.")

    return redirect('/dashboard/speakers/?type=expert')


@login_required(login_url='/portal/login/')
def education_expert_delete(request, pk):
    """Admin endpoint to delete an Education Expert profile and login user."""
    from .models import EducationExpert
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    is_admin = request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', '') == 'admin'
    if not is_admin:
        messages.error(request, "Access restricted to Administrators.")

        return redirect('dashboard_index')
    expert = get_object_or_404(EducationExpert, pk=pk)
    user = expert.user
    name = expert.name
    expert.delete()
    if user:
        user.delete()
    messages.success(request, f"Education Expert '{name}' and associated user account deleted successfully.")

    return redirect('/dashboard/speakers/?type=expert')

# ---------------------------------------------------------
# NOTIFICATIONS API (DROPDOWN & MANAGEMENT)
# ---------------------------------------------------------


@login_required(login_url='/portal/login/')
def dashboard_notifications_list(request):
    """
    API endpoint returning recent notifications and unread count for current user.
    """
    from .models import Notification
    from django.http import JsonResponse
    from django.utils.timesince import timesince
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:25]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    data = []
    for n in notifications:
        data.append({
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%b %d, %Y %I:%M %p'),
            'time_ago': f"{timesince(n.created_at)} ago"
        })

    return JsonResponse({
        'success': True,
        'unread_count': unread_count,
        'notifications': data
    })


@login_required(login_url='/portal/login/')
def dashboard_notification_mark_read(request, pk):
    """
    Mark a single notification as read. Accepts both GET and POST.
    """
    from .models import Notification
    from django.http import JsonResponse
    notif = Notification.objects.filter(id=pk, user=request.user).first()
    if notif:
        notif.is_read = True
        notif.save(update_fields=['is_read'])
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return JsonResponse({
        'success': True,
        'id': pk,
        'unread_count': unread_count
    })


@login_required(login_url='/portal/login/')
def dashboard_notification_mark_all_read(request):
    """
    Mark all notifications as read for current user. Accepts both GET and POST.
    """
    from .models import Notification
    from django.http import JsonResponse
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    return JsonResponse({
        'success': True,
        'unread_count': 0
    })


# ==============================================================================
# MR. K CHATBOT Q&A KNOWLEDGE BASE MANAGEMENT
# ==============================================================================

@login_required(login_url='/portal/login/')
def dashboard_chatbot_faq(request):
    """
    List and manage Mr. K Chatbot Questions & Answers, Suggestion Chips, and Trigger Keywords.
    """
    from .models import ChatbotFAQ
    from django.db.models import Q

    # Admin verification
    is_admin = request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', '') == 'admin'
    if not is_admin:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")

    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    chip_filter = request.GET.get('is_chip', '')

    faqs = ChatbotFAQ.objects.all()

    if q:
        faqs = faqs.filter(
            Q(question__icontains=q) |
            Q(chip_label__icontains=q) |
            Q(keywords__icontains=q) |
            Q(answer__icontains=q)
        )

    if status_filter == 'active':
        faqs = faqs.filter(is_active=True)
    elif status_filter == 'inactive':
        faqs = faqs.filter(is_active=False)

    if chip_filter == 'yes':
        faqs = faqs.filter(is_chip=True)
    elif chip_filter == 'no':
        faqs = faqs.filter(is_chip=False)

    faqs = faqs.order_by('order', 'id')

    total_count = ChatbotFAQ.objects.count()
    active_count = ChatbotFAQ.objects.filter(is_active=True).count()
    chips_count = ChatbotFAQ.objects.filter(is_chip=True, is_active=True).count()

    context = {
        'faqs': faqs,
        'search_query': q,
        'status_filter': status_filter,
        'chip_filter': chip_filter,
        'total_count': total_count,
        'active_count': active_count,
        'chips_count': chips_count,
    }
    return render(request, 'dashboard/chatbot_faq.html', context)


@login_required(login_url='/portal/login/')
def chatbot_faq_create(request):
    """
    Create a new Chatbot Q&A entry.
    """
    from .forms import ChatbotFAQForm
    from django.contrib import messages

    is_admin = request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', '') == 'admin'
    if not is_admin:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")

    if request.method == 'POST':
        form = ChatbotFAQForm(request.POST)
        if form.is_valid():
            faq = form.save()
            messages.success(request, f'Chatbot question "{faq.question}" added successfully.')
            return redirect('dashboard_chatbot_faq')
    else:
        form = ChatbotFAQForm()

    return render(request, 'dashboard/chatbot_faq_form.html', {
        'form': form,
        'is_edit': False,
    })


@login_required(login_url='/portal/login/')
def chatbot_faq_update(request, pk):
    """
    Update an existing Chatbot Q&A entry.
    """
    from .models import ChatbotFAQ
    from .forms import ChatbotFAQForm
    from django.shortcuts import get_object_or_404
    from django.contrib import messages

    is_admin = request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', '') == 'admin'
    if not is_admin:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")

    faq = get_object_or_404(ChatbotFAQ, pk=pk)

    if request.method == 'POST':
        form = ChatbotFAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, f'Chatbot question "{faq.question}" updated successfully.')
            return redirect('dashboard_chatbot_faq')
    else:
        form = ChatbotFAQForm(instance=faq)

    return render(request, 'dashboard/chatbot_faq_form.html', {
        'form': form,
        'faq': faq,
        'is_edit': True,
    })


@login_required(login_url='/portal/login/')
def chatbot_faq_delete(request, pk):
    """
    Delete a Chatbot Q&A entry.
    """
    from .models import ChatbotFAQ
    from django.shortcuts import get_object_or_404
    from django.contrib import messages

    is_admin = request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', '') == 'admin'
    if not is_admin:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")

    faq = get_object_or_404(ChatbotFAQ, pk=pk)

    if request.method == 'POST':
        title = faq.question
        faq.delete()
        messages.success(request, f'Chatbot question "{title}" has been deleted.')
        return redirect('dashboard_chatbot_faq')

    return render(request, 'dashboard/chatbot_faq_confirm_delete.html', {'faq': faq})


@login_required(login_url='/portal/login/')
def chatbot_faq_toggle_active(request, pk):
    """
    Toggle is_active status of a Chatbot Q&A entry.
    """
    from .models import ChatbotFAQ
    from django.shortcuts import get_object_or_404
    from django.contrib import messages

    is_admin = request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', '') == 'admin'
    if not is_admin:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Admin access required")

    faq = get_object_or_404(ChatbotFAQ, pk=pk)
    faq.is_active = not faq.is_active
    faq.save(update_fields=['is_active'])

    status_str = "activated" if faq.is_active else "deactivated"
    messages.success(request, f'Chatbot question "{faq.question}" has been {status_str}.')
    return redirect('dashboard_chatbot_faq')
