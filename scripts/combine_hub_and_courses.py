import os
import sys

# 1. Update templates/dashboard/index.html
index_path = 'templates/dashboard/index.html'
with open(index_path, 'r', encoding='utf-8') as f:
    index_html = f.read()

# Fix KPI card values: length of integer bug
old_kpi_courses = """    <span style="font-size:32px; font-weight:800; color:#8b5cf6;">{{ total_courses|default:courses|length }}</span>"""
new_kpi_courses = """    <span style="font-size:32px; font-weight:800; color:#8b5cf6;">{{ courses|length }}</span>"""

assert old_kpi_courses in index_html, "old_kpi_courses not found"
index_html = index_html.replace(old_kpi_courses, new_kpi_courses, 1)

old_kpi_sch = """    <span style="font-size:32px; font-weight:800; color:#f59e0b;">{{ total_scholarships|default:scholarships|length }}</span>"""
new_kpi_sch = """    <span style="font-size:32px; font-weight:800; color:#f59e0b;">{{ scholarships|length }}</span>"""

assert old_kpi_sch in index_html, "old_kpi_sch not found"
index_html = index_html.replace(old_kpi_sch, new_kpi_sch, 1)

# Add Student Enquiries & Applications right after scholarshipsSection
marker_modal = "<!-- ADD COURSE MODAL (INLINE ON DASHBOARD) -->"
assert marker_modal in index_html, "marker_modal not found"

applications_section_html = """<!-- STUDENT ENQUIRIES & APPLICATIONS SECTION (COMBINED HUB) -->
<div id="applicationsSection" class="glass-card" style="margin-bottom: 24px; padding: 24px; border-radius: 16px;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <div>
      <h3 style="margin: 0; font-size: 18px; font-weight: 800; color: #0a1936; display:flex; align-items:center; gap:8px;">
        <i data-feather="users" style="width:20px; height:20px; color:#10b981;"></i> Student Enquiries &amp; Applications
      </h3>
      <p style="margin: 4px 0 0 0; font-size: 13px; color: #64748b;">Direct course applications, shortlists, and consultation requests from students</p>
    </div>
    <span style="font-size: 12px; font-weight: 750; background: #eff6ff; color: #1768ff; padding: 4px 12px; border-radius: 20px; border:1px solid #bfdbfe;">
      {{ applications.count|default:0 }} Applications
    </span>
  </div>

  <div style="overflow-x: auto;">
    <table style="width: 100%; border-collapse: collapse; text-align: left; min-width: 550px;">
      <thead>
        <tr style="border-bottom: 2px solid #e2e8f0; background: #f8fafc;">
          <th style="padding: 12px 14px; font-size: 11.5px; font-weight: 700; color: #64748b; text-transform: uppercase;">Student Applicant</th>
          <th style="padding: 12px 14px; font-size: 11.5px; font-weight: 700; color: #64748b; text-transform: uppercase;">Program Choice</th>
          <th style="padding: 12px 14px; font-size: 11.5px; font-weight: 700; color: #64748b; text-transform: uppercase;">Status</th>
          <th style="padding: 12px 14px; font-size: 11.5px; font-weight: 700; color: #64748b; text-transform: uppercase; text-align: right;">Applied Date</th>
        </tr>
      </thead>
      <tbody>
        {% for app in applications %}
        <tr style="border-bottom: 1px solid #f1f5f9; transition:background 0.15s ease;" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'">
          <td style="padding: 14px;">
            <div style="font-weight: 750; color: #0a1936; font-size: 14px;">{{ app.student.user.get_full_name|default:app.student.user.username }}</div>
            <div style="font-size: 12px; color: #64748b; margin-top:2px;">{{ app.student.user.email }}</div>
          </td>
          <td style="padding: 14px; font-size: 13.5px; color: #334155;">
            <span style="font-weight: 700; color:#0a1936;">{{ app.program_name }}</span>
          </td>
          <td style="padding: 14px;">
            <span style="display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 11.5px; font-weight: 750;
              {% if app.status == 'Accepted' %}background:#ecfdf5; color:#059669; border:1px solid #a7f3d0;
              {% elif app.status == 'Interviewing' %}background:#eff6ff; color:#1768ff; border:1px solid #bfdbfe;
              {% elif app.status == 'Applied' %}background:#fef3c7; color:#d97706; border:1px solid #fde68a;
              {% else %}background:#f1f5f9; color:#64748b; border:1px solid #e2e8f0;{% endif %}">
              {{ app.status }}
            </span>
          </td>
          <td style="padding: 14px; font-size: 12.5px; color: #64748b; text-align: right;">
            {{ app.applied_at|date:"M d, Y" }}
          </td>
        </tr>
        {% empty %}
        <tr>
          <td colspan="4" style="padding: 36px; text-align: center; color: #64748b;">
            <div style="font-size: 28px; margin-bottom: 8px;">📥</div>
            <div style="font-weight: 750; font-size:14.5px; color: #0a1936;">No direct course applications received yet</div>
            <div style="font-size: 12.5px; margin-top: 4px; color:#64748b;">When prospective students shortlist or apply to your degree programs, their dossiers appear here in real-time.</div>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>

"""

index_html = index_html.replace(marker_modal, applications_section_html + marker_modal, 1)

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(index_html)
print("Updated templates/dashboard/index.html with applications section and fixed KPI counts!")

# 2. Update templates/dashboard/base.html
base_path = 'templates/dashboard/base.html'
with open(base_path, 'r', encoding='utf-8') as f:
    base_html = f.read()

# Update Courses & Degrees link to anchor to #coursesSection on dashboard_index
old_nav_courses = """<li><a href="{% url 'university_staff_dashboard' %}" class="nav-item {% block nav_uni_courses %}{% endblock %}"><i data-feather="book-open" style="width:18px; height:18px; color:#8b5cf6;"></i> Courses & Degrees</a></li>"""
new_nav_courses = """<li><a href="{% url 'dashboard_index' %}#coursesSection" class="nav-item {% block nav_uni_courses %}{% endblock %}" id="navUniCourses"><i data-feather="book-open" style="width:18px; height:18px; color:#8b5cf6;"></i> Courses & Degrees</a></li>"""

assert old_nav_courses in base_html, "old_nav_courses not found in base.html"
base_html = base_html.replace(old_nav_courses, new_nav_courses, 1)

# Update the hash listener to handle both #coursesSection and #scholarshipsSection
old_hash_js = """  // Handle sidebar hash navigation (e.g. #scholarshipsSection)
  (function() {
    function updateSidebarHashActive() {
      if (window.location.hash === '#scholarshipsSection') {
        const schLink = document.querySelector('a.nav-item[href*="#scholarshipsSection"]');
        if (schLink) {
          document.querySelectorAll('.nav-menu .nav-item').forEach(function(el) { el.classList.remove('active'); });
          schLink.classList.add('active');
        }
      }
    }
    updateSidebarHashActive();
    window.addEventListener('hashchange', updateSidebarHashActive);
  })();"""

new_hash_js = """  // Handle sidebar hash navigation on combined hub (e.g. #coursesSection, #scholarshipsSection)
  (function() {
    function updateSidebarHashActive() {
      const hash = window.location.hash;
      if (hash === '#coursesSection') {
        const coursesLink = document.querySelector('a.nav-item[href*="#coursesSection"]');
        if (coursesLink) {
          document.querySelectorAll('.nav-menu .nav-item').forEach(function(el) { el.classList.remove('active'); });
          coursesLink.classList.add('active');
        }
      } else if (hash === '#scholarshipsSection') {
        const schLink = document.querySelector('a.nav-item[href*="#scholarshipsSection"]');
        if (schLink) {
          document.querySelectorAll('.nav-menu .nav-item').forEach(function(el) { el.classList.remove('active'); });
          schLink.classList.add('active');
        }
      } else if (window.location.pathname === '/dashboard/' && (!hash || hash === '#' || hash === '#!')) {
        const exhHub = document.querySelector('a.nav-item[href="/dashboard/"]');
        if (exhHub) {
          document.querySelectorAll('.nav-menu .nav-item').forEach(function(el) { el.classList.remove('active'); });
          exhHub.classList.add('active');
        }
      }
    }
    updateSidebarHashActive();
    window.addEventListener('hashchange', updateSidebarHashActive);
  })();"""

assert old_hash_js in base_html, "old_hash_js not found in base.html"
base_html = base_html.replace(old_hash_js, new_hash_js, 1)

with open(base_path, 'w', encoding='utf-8') as f:
    f.write(base_html)
print("Updated templates/dashboard/base.html with anchor link and smooth hash navigation!")

# 3. Update core/dashboard_views.py university_dashboard_view redirect
views_path = 'core/dashboard_views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    views_code = f.read()

target_uni_view = """def university_dashboard_view(request, pk=None):
    from .models import University, UniversityProfile, Course, Scholarship, ExpoBooth, BoothInteraction, UniversityApplication, Exhibitor, CourseCategory
    from django.shortcuts import get_object_or_404
    from django.contrib import messages

    uni = None"""

replacement_uni_view = """def university_dashboard_view(request, pk=None):
    return redirect('/dashboard/#coursesSection')
    from .models import University, UniversityProfile, Course, Scholarship, ExpoBooth, BoothInteraction, UniversityApplication, Exhibitor, CourseCategory
    from django.shortcuts import get_object_or_404
    from django.contrib import messages

    uni = None"""

assert target_uni_view in views_code, "target_uni_view not found in dashboard_views.py"
views_code = views_code.replace(target_uni_view, replacement_uni_view, 1)

with open(views_path, 'w', encoding='utf-8') as f:
    f.write(views_code)
print("Updated core/dashboard_views.py university_dashboard_view redirect!")

