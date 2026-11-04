import os, sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knova_backend.settings')
import django
django.setup()

# 1. Update student1 user names
from django.contrib.auth import get_user_model
User = get_user_model()
s1 = User.objects.filter(username='student1').first()
if s1:
    s1.first_name = "Student"
    s1.last_name = "One"
    s1.save()
    print("Updated student1 names to Student One.")

u_staff = User.objects.filter(username='uni_staff1').first()
if u_staff:
    u_staff.first_name = "Admissions"
    u_staff.last_name = "Staff"
    u_staff.save()
    print("Updated uni_staff1 names to Admissions Staff.")

# 2. Fix core/dashboard_views.py
dash_path = 'core/dashboard_views.py'
with open(dash_path, 'r', encoding='utf-8') as f:
    dash_code = f.read()

# Fix lines 337-338
old_line_337 = 'full_name = request.user.get_full_name() or request.user.username or (passport.student_name if passport else "Alex Student")'
new_line_337 = 'full_name = request.user.get_full_name() or request.user.username or (passport.student_name if passport else "")'

old_line_338 = 'school_or_org = getattr(profile, ' + repr('school_college') + ', ' + repr('') + ') or getattr(profile, ' + repr('current_education') + ', ' + repr('') + ') or "Calicut University"'
new_line_338 = 'school_or_org = getattr(profile, ' + repr('school_college') + ', ' + repr('') + ') or getattr(profile, ' + repr('current_education') + ', ' + repr('') + ') or ""'

if old_line_337 in dash_code:
    dash_code = dash_code.replace(old_line_337, new_line_337)
    print("Replaced line 337 in dashboard_views.py")
if old_line_338 in dash_code:
    dash_code = dash_code.replace(old_line_338, new_line_338)
    print("Replaced line 338 in dashboard_views.py")

# Fix _build_contact_dict Harvard reference
old_contact_block = """    elif user.username == 'uni_staff1' or 'harvard' in user.username.lower():
        role_label = "Admissions Director"
        subtitle = "Harvard University"
        avatar_bg = "#a81c1c"
        category = "university"
    elif 'qa' in user.username.lower():
        role_label = "Admissions Officer"
        subtitle = "Global University"
        avatar_bg = "#0369a1"
        category = "university" """

# Let's find exactly how lines 1512-1521 look in dashboard_views.py
target_harvard = """    elif user.username == 'uni_staff1' or 'harvard' in user.username.lower():
        role_label = "Admissions Director"
        subtitle = "Harvard University"
        avatar_bg = "#a81c1c"
        category = "university" """

new_uni_staff_block = """    elif hasattr(user, 'university_staff') or 'staff' in user.username or 'uni_' in user.username:
        role_label = "Admissions Staff"
        subtitle = "University Staff"
        avatar_bg = "#1d4ed8"
        category = "university" """

if "subtitle = \"Harvard University\"" in dash_code:
    dash_code = dash_code.replace(
        """    elif user.username == 'uni_staff1' or 'harvard' in user.username.lower():
        role_label = "Admissions Director"
        subtitle = "Harvard University"
        avatar_bg = "#a81c1c"
        category = "university"
    elif 'qa' in user.username.lower():
        role_label = "Admissions Officer"
        subtitle = "Global University"
        avatar_bg = "#0369a1"
        category = "university" """,
        new_uni_staff_block
    )
    # Also handle single-line version if formatted differently
    if "subtitle = \"Harvard University\"" in dash_code:
        import re
        dash_code = re.sub(
            r"elif user\.username == 'uni_staff1' or 'harvard' in user\.username\.lower\(\):\s*role_label = [^\n]+\s*subtitle = \"Harvard University\"\s*avatar_bg = [^\n]+\s*category = [^\n]+",
            new_uni_staff_block.strip(),
            dash_code
        )
    print("Replaced Harvard contact block in dashboard_views.py")

# Fix auto reply Harvard reference
old_reply_harvard = """    elif rep_user.username == 'uni_staff1' or 'harvard' in rep_user.username.lower():
        uni_name = "Harvard University"
        rep_title = "Harvard Admissions Director" """

new_reply_harvard = """    elif rep_user.username == 'uni_staff1' or 'uni_' in rep_user.username:
        uni_name = "our university"
        rep_title = "Admissions Representative" """

if "uni_name = \"Harvard University\"" in dash_code:
    import re
    dash_code = re.sub(
        r"elif rep_user\.username == 'uni_staff1' or 'harvard' in rep_user\.username\.lower\(\):\s*uni_name = \"Harvard University\"\s*rep_title = \"Harvard Admissions Director\"",
        new_reply_harvard.strip(),
        dash_code
    )
    print("Replaced Harvard in _generate_rep_auto_reply in dashboard_views.py")

with open(dash_path, 'w', encoding='utf-8') as f:
    f.write(dash_code)


# 3. Fix core/public_views.py
pub_path = 'core/public_views.py'
with open(pub_path, 'r', encoding='utf-8') as f:
    pub_code = f.read()

# Fix popular scholarships
old_pop_sch = """        if not query:
            popular = [
                {'type': 'Scholarship', 'title': 'STEM & Future Tech Innovation Award', 'subtitle': 'Engineering & Technology • Direct Grant', 'query_val': 'STEM', 'url': f"{reverse('public_scholarships')}?q=STEM", 'icon': 'ti ti-cpu'},
                {'type': 'Scholarship', 'title': 'Dean’s International Excellence Grant', 'subtitle': 'Business & Finance • Fast-Track', 'query_val': 'Excellence', 'url': f"{reverse('public_scholarships')}?q=Excellence", 'icon': 'ti ti-medal'},
                {'type': 'University', 'title': 'Cornell University Aid Awards', 'subtitle': 'USA • Verified Direct Partner Grants', 'query_val': 'Cornell University', 'url': f"{reverse('public_scholarships')}?q=Cornell+University", 'icon': 'ti ti-building-bank'},
                {'type': 'University', 'title': 'Oxford University Scholarships', 'subtitle': 'UK • Prestigious International Grants', 'query_val': 'Oxford University', 'url': f"{reverse('public_scholarships')}?q=Oxford+University", 'icon': 'ti ti-building-bank'}
            ]
            return JsonResponse({'results': popular})"""

new_pop_sch = """        if not query:
            popular = []
            for s in Scholarship.objects.select_related('university')[:4]:
                popular.append({
                    'type': 'Scholarship',
                    'title': s.name,
                    'subtitle': f"{s.university.name if s.university else 'Open Grant'} • {s.coverage_type}",
                    'query_val': s.name,
                    'url': f"{reverse('public_scholarships')}?q={s.name}",
                    'icon': 'ti ti-medal'
                })
            return JsonResponse({'results': popular})"""

if old_pop_sch in pub_code:
    pub_code = pub_code.replace(old_pop_sch, new_pop_sch)
    print("Replaced popular scholarships in public_views.py")

# Fix popular exhibitors
old_pop_exh = """    if scope == 'exhibitors':
        if not query:
            popular = [
                {'type': 'University', 'title': 'Oxford University', 'subtitle': 'United Kingdom • Hall 1 Pavilion A', 'query_val': 'Oxford University', 'url': f"{reverse('public_exhibitors')}?q=Oxford+University", 'icon': 'ti ti-building-bank'},
                {'type': 'University', 'title': 'Harvard University', 'subtitle': 'USA • Hall 1 Pavilion A', 'query_val': 'Harvard University', 'url': f"{reverse('public_exhibitors')}?q=Harvard+University", 'icon': 'ti ti-building-bank'},
                {'type': 'University', 'title': 'MIT', 'subtitle': 'USA • Hall 1 Pavilion A', 'query_val': 'MIT', 'url': f"{reverse('public_exhibitors')}?q=MIT", 'icon': 'ti ti-building-bank'},
                {'type': 'University', 'title': 'Stanford University', 'subtitle': 'USA • Hall 1 Pavilion A', 'query_val': 'Stanford University', 'url': f"{reverse('public_exhibitors')}?q=Stanford+University", 'icon': 'ti ti-building-bank'},
                {'type': 'University', 'title': 'Cambridge University', 'subtitle': 'United Kingdom • Hall 1 Pavilion A', 'query_val': 'Cambridge University', 'url': f"{reverse('public_exhibitors')}?q=Cambridge+University", 'icon': 'ti ti-building-bank'},
                {'type': 'University', 'title': 'ETH Zurich', 'subtitle': 'Switzerland • Hall 1 Pavilion B', 'query_val': 'ETH Zurich', 'url': f"{reverse('public_exhibitors')}?q=ETH+Zurich", 'icon': 'ti ti-building-bank'}
            ]
            return JsonResponse({'results': popular})"""

new_pop_exh = """    if scope == 'exhibitors':
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
            return JsonResponse({'results': popular})"""

if old_pop_exh in pub_code:
    pub_code = pub_code.replace(old_pop_exh, new_pop_exh)
    print("Replaced popular exhibitors in public_views.py")

# Fix popular courses
old_pop_courses = """        if not query:
            popular = [
                {'type': 'Course', 'title': 'BSc Computer Science', 'subtitle': 'Undergraduate • High Demand', 'query_val': 'Computer Science', 'url': f"{reverse('courses_list')}?q=Computer+Science", 'icon': 'ti ti-sparkles'},
                {'type': 'Course', 'title': 'MSc Artificial Intelligence', 'subtitle': 'Postgraduate • Tech Arena', 'query_val': 'Artificial Intelligence', 'url': f"{reverse('courses_list')}?q=Artificial+Intelligence", 'icon': 'ti ti-cpu'},
                {'type': 'Course', 'title': 'Master of Business Administration (MBA)', 'subtitle': 'Executive & Full-Time', 'query_val': 'MBA', 'url': f"{reverse('courses_list')}?q=MBA", 'icon': 'ti ti-briefcase'},
                {'type': 'University', 'title': 'Harvard University', 'subtitle': 'Cambridge, USA • Top Partner', 'query_val': 'Harvard University', 'url': f"{reverse('courses_list')}?q=Harvard+University", 'icon': 'ti ti-building'},
                {'type': 'University', 'title': 'Oxford University', 'subtitle': 'Oxford, UK • Top Partner', 'query_val': 'Oxford University', 'url': f"{reverse('courses_list')}?q=Oxford+University", 'icon': 'ti ti-building'},
                {'type': 'Category', 'title': 'Engineering & Technology', 'subtitle': 'All Engineering Degrees', 'query_val': 'Engineering', 'url': f"{reverse('courses_list')}?q=Engineering", 'icon': 'ti ti-category'}
            ]
            return JsonResponse({'results': popular})"""

new_pop_courses = """        if not query:
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
            return JsonResponse({'results': popular})"""

if old_pop_courses in pub_code:
    pub_code = pub_code.replace(old_pop_courses, new_pop_courses)
    print("Replaced popular courses in public_views.py")

# Fix unlock_all universities
old_unlock = "passport.visited_universities = ['Harvard University', 'Oxford University', 'Cambridge University']"
new_unlock = "passport.visited_universities = list(University.objects.values_list('name', flat=True)[:3]) or ['Exhibitor Booth A', 'Exhibitor Booth B', 'Exhibitor Booth C']"
if old_unlock in pub_code:
    pub_code = pub_code.replace(old_unlock, new_unlock)
    print("Replaced unlock_all in public_views.py")

# Fix public_my_expo Alex Student / Calicut University
old_my_expo_alex = 'full_name = passport.student_name or "Alex Student"'
new_my_expo_alex = 'full_name = passport.student_name or ""'
if old_my_expo_alex in pub_code:
    pub_code = pub_code.replace(old_my_expo_alex, new_my_expo_alex)
    print("Replaced Alex Student in public_views.py")

old_my_expo_calicut = 'school_or_org = "Calicut University"'
new_my_expo_calicut = 'school_or_org = ""'
if old_my_expo_calicut in pub_code:
    pub_code = pub_code.replace(old_my_expo_calicut, new_my_expo_calicut)
    print("Replaced Calicut University in public_views.py")

with open(pub_path, 'w', encoding='utf-8') as f:
    f.write(pub_code)

print("All python files updated successfully.")

