import os

# ==============================================================================
# 1. Update core/dashboard_views.py
# ==============================================================================
with open('core/dashboard_views.py', 'r', encoding='utf-8') as f:
    views_code = f.read()

edit_views = """

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
"""

anchor_sch_del = "def university_scholarship_delete(request, pk):"
if anchor_sch_del in views_code and "def university_course_update" not in views_code:
    # Inject before university_scholarship_delete
    views_code = views_code.replace(anchor_sch_del, edit_views + "\n" + anchor_sch_del, 1)
    with open('core/dashboard_views.py', 'w', encoding='utf-8') as f:
        f.write(views_code)
    print("Added university_course_update and university_scholarship_update to dashboard_views.py!")
else:
    print("Already added or anchor not found in dashboard_views.py!")


# ==============================================================================
# 2. Update core/urls.py
# ==============================================================================
with open('core/urls.py', 'r', encoding='utf-8') as f:
    urls_code = f.read()

target_url = "path('courses/<int:pk>/delete/', dashboard_views.university_course_delete, name='university_course_delete'),"
replacement_url = """path('courses/<int:pk>/edit/', dashboard_views.university_course_update, name='university_course_update'),
    path('universities/courses/<int:pk>/edit/', dashboard_views.university_course_update),
    path('courses/<int:pk>/delete/', dashboard_views.university_course_delete, name='university_course_delete'),"""

target_sch_url = "path('scholarships/<int:pk>/delete/', dashboard_views.university_scholarship_delete, name='university_scholarship_delete'),"
replacement_sch_url = """path('scholarships/<int:pk>/edit/', dashboard_views.university_scholarship_update, name='university_scholarship_update'),
    path('universities/scholarships/<int:pk>/edit/', dashboard_views.university_scholarship_update),
    path('scholarships/<int:pk>/delete/', dashboard_views.university_scholarship_delete, name='university_scholarship_delete'),"""

if target_url in urls_code and "university_course_update" not in urls_code:
    urls_code = urls_code.replace(target_url, replacement_url, 1)
    print("Added course edit URLs to core/urls.py!")

if target_sch_url in urls_code and "university_scholarship_update" not in urls_code:
    urls_code = urls_code.replace(target_sch_url, replacement_sch_url, 1)
    print("Added scholarship edit URLs to core/urls.py!")

with open('core/urls.py', 'w', encoding='utf-8') as f:
    f.write(urls_code)


# ==============================================================================
# 3. Update templates/dashboard/index.html
# ==============================================================================
with open('templates/dashboard/index.html', 'r', encoding='utf-8') as f:
    index_html = f.read()

# Replace Course Actions in index.html
old_course_actions = """          <td style="padding:14px; text-align:right;">
            <form action="{% url 'university_course_delete' course.pk %}" method="POST" onsubmit="return confirm('Remove program \\'{{ course.name }}\\'?');" style="display:inline;">
              {% csrf_token %}
              <input type="hidden" name="next" value="{{ request.path }}">
              <button type="submit" style="background:#fee2e2; border:1px solid #fecaca; color:#dc2626; cursor:pointer; padding:6px 12px; border-radius:6px; font-size:12px; font-weight:700; display:inline-flex; align-items:center; gap:4px; transition:0.2s;" title="Delete Course">
                <i data-feather="trash-2" style="width:13px; height:13px;"></i> Delete
              </button>
            </form>
          </td>"""

new_course_actions = """          <td style="padding:14px; text-align:right;">
            <div style="display:inline-flex; align-items:center; gap:8px; justify-content:flex-end;">
              <button type="button" class="btn" onclick="openEditCourseModal(this)"
                      data-id="{{ course.pk }}"
                      data-name="{{ course.name|escapejs }}"
                      data-degree="{{ course.degree_type|escapejs }}"
                      data-stream="{{ course.stream|escapejs }}"
                      data-duration="{{ course.duration|escapejs }}"
                      data-mode="{{ course.mode|escapejs }}"
                      data-fees="{{ course.fees|escapejs }}"
                      data-eligibility="{{ course.eligibility|escapejs }}"
                      data-scholarship="{% if course.scholarship_available %}1{% else %}0{% endif %}"
                      style="background:#eff6ff; border:1px solid #bfdbfe; color:#1d4ed8; padding:6px 12px; border-radius:6px; font-size:12px; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:4px;"
                      title="Edit Course">
                <i data-feather="edit-2" style="width:13px; height:13px;"></i> Edit
              </button>
              <form action="{% url 'university_course_delete' course.pk %}" method="POST" onsubmit="return confirm('Remove program \\'{{ course.name }}\\'?');" style="display:inline; margin:0;">
                {% csrf_token %}
                <input type="hidden" name="next" value="{{ request.path }}">
                <button type="submit" style="background:#fee2e2; border:1px solid #fecaca; color:#dc2626; cursor:pointer; padding:6px 12px; border-radius:6px; font-size:12px; font-weight:700; display:inline-flex; align-items:center; gap:4px; transition:0.2s;" title="Delete Course">
                  <i data-feather="trash-2" style="width:13px; height:13px;"></i> Delete
                </button>
              </form>
            </div>
          </td>"""

if old_course_actions in index_html:
    index_html = index_html.replace(old_course_actions, new_course_actions, 1)
    print("Added Edit button to Course rows in index.html!")
else:
    print("Could not find old_course_actions in index.html!")

# Replace Scholarship Actions in index.html
old_sch_actions = """          <td style="padding:14px; text-align:right;">
            <form action="{% url 'university_scholarship_delete' sch.pk %}" method="POST" onsubmit="return confirm('Remove scholarship award \\'{{ sch.name }}\\'?');" style="display:inline;">
              {% csrf_token %}
              <input type="hidden" name="next" value="{{ request.path }}">
              <button type="submit" style="background:#fee2e2; border:1px solid #fecaca; color:#dc2626; cursor:pointer; padding:6px 12px; border-radius:6px; font-size:12px; font-weight:700; display:inline-flex; align-items:center; gap:4px; transition:0.2s;" title="Delete Scholarship">
                <i data-feather="trash-2" style="width:13px; height:13px;"></i> Delete
              </button>
            </form>
          </td>"""

new_sch_actions = """          <td style="padding:14px; text-align:right;">
            <div style="display:inline-flex; align-items:center; gap:8px; justify-content:flex-end;">
              <button type="button" class="btn" onclick="openEditScholarshipModal(this)"
                      data-id="{{ sch.pk }}"
                      data-name="{{ sch.name|escapejs }}"
                      data-amount="{{ sch.amount|escapejs }}"
                      data-coverage="{{ sch.coverage_type|escapejs }}"
                      data-level="{{ sch.level|escapejs }}"
                      data-category="{{ sch.category|escapejs }}"
                      data-field="{{ sch.field_of_study|escapejs }}"
                      data-deadline="{% if sch.deadline %}{{ sch.deadline|date:'Y-m-d' }}{% endif %}"
                      data-eligibility="{{ sch.eligibility|escapejs }}"
                      data-description="{{ sch.description|escapejs }}"
                      style="background:#fffbeb; border:1px solid #fde68a; color:#b45309; padding:6px 12px; border-radius:6px; font-size:12px; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:4px;"
                      title="Edit Scholarship">
                <i data-feather="edit-2" style="width:13px; height:13px;"></i> Edit
              </button>
              <form action="{% url 'university_scholarship_delete' sch.pk %}" method="POST" onsubmit="return confirm('Remove scholarship award \\'{{ sch.name }}\\'?');" style="display:inline; margin:0;">
                {% csrf_token %}
                <input type="hidden" name="next" value="{{ request.path }}">
                <button type="submit" style="background:#fee2e2; border:1px solid #fecaca; color:#dc2626; cursor:pointer; padding:6px 12px; border-radius:6px; font-size:12px; font-weight:700; display:inline-flex; align-items:center; gap:4px; transition:0.2s;" title="Delete Scholarship">
                  <i data-feather="trash-2" style="width:13px; height:13px;"></i> Delete
                </button>
              </form>
            </div>
          </td>"""

if old_sch_actions in index_html:
    index_html = index_html.replace(old_sch_actions, new_sch_actions, 1)
    print("Added Edit button to Scholarship rows in index.html!")
else:
    print("Could not find old_sch_actions in index.html!")

# Inject Edit Modals and Scripts into index.html
edit_modals_and_js = """
<!-- EDIT COURSE MODAL -->
<div id="editCourseModal" style="display:none; position:fixed; inset:0; background:rgba(10,25,54,0.65); backdrop-filter:blur(6px); z-index:9999; align-items:center; justify-content:center; padding:20px;">
  <div style="background:#fff; border-radius:16px; max-width:620px; width:100%; max-height:92vh; overflow-y:auto; box-shadow:0 20px 50px rgba(0,0,0,0.3); padding:28px; position:relative;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; border-bottom:1px solid #f1f5f9; padding-bottom:14px;">
      <div>
        <h3 style="margin:0; font-size:19px; font-weight:800; color:#0a1936;"><i data-feather="edit-2" style="width:18px; height:18px; color:#1768ff; vertical-align:-2px;"></i> Edit Academic Degree Program</h3>
        <p style="margin:3px 0 0; font-size:12.5px; color:#64748b;">Update course specifications, fees, and scholarship eligibility.</p>
      </div>
      <button onclick="document.getElementById('editCourseModal').style.display='none'" style="background:#f1f5f9; border:none; border-radius:50%; width:32px; height:32px; cursor:pointer; font-size:16px; font-weight:700; color:#64748b; display:flex; align-items:center; justify-content:center;">&times;</button>
    </div>

    <form id="editCourseForm" method="POST" action="" style="display:flex; flex-direction:column; gap:16px;">
      {% csrf_token %}
      <input type="hidden" name="next" value="{{ request.path }}">

      <div>
        <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Program / Course Name *</label>
        <input type="text" id="editCourseName" name="name" required style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; box-sizing:border-box;">
      </div>

      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:14px;">
        <div>
          <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Degree Level</label>
          <select id="editCourseDegree" name="degree_type" style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; background:#fff; box-sizing:border-box;">
            <option value="Undergraduate">Undergraduate (UG / Bachelor's)</option>
            <option value="Postgraduate">Postgraduate (PG / Master's)</option>
            <option value="PhD / Doctoral">Doctoral (PhD)</option>
            <option value="Diploma">Diploma / Associate</option>
            <option value="Certificate">Certificate Program</option>
          </select>
        </div>

        <div>
          <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Academic Stream / Discipline</label>
          <input type="text" id="editCourseStream" name="stream" style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; box-sizing:border-box;">
        </div>
      </div>

      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:14px;">
        <div>
          <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Duration</label>
          <input type="text" id="editCourseDuration" name="duration" style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; box-sizing:border-box;">
        </div>

        <div>
          <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Study Mode</label>
          <select id="editCourseMode" name="mode" style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; background:#fff; box-sizing:border-box;">
            <option value="Full Time">Full Time</option>
            <option value="Part Time">Part Time</option>
            <option value="Online">Online / Hybrid</option>
          </select>
        </div>
      </div>

      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:14px;">
        <div>
          <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Annual Tuition Fees</label>
          <input type="text" id="editCourseFees" name="fees" style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; box-sizing:border-box;">
        </div>

        <div>
          <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Eligibility Standards</label>
          <input type="text" id="editCourseEligibility" name="eligibility" style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; box-sizing:border-box;">
        </div>
      </div>

      <div style="display:flex; align-items:center; gap:8px; padding:10px 14px; background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0; margin-top:4px;">
        <input type="checkbox" id="editCourseScholarship" name="scholarship_available" style="width:18px; height:18px; accent-color:#1768ff;">
        <label for="editCourseScholarship" style="font-size:13px; font-weight:600; color:#0a1936; cursor:pointer;">
          Merit / Need-based Scholarship Available for this Program
        </label>
      </div>

      <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:12px; border-top:1px solid #f1f5f9; padding-top:16px;">
        <button type="button" onclick="document.getElementById('editCourseModal').style.display='none'" class="btn" style="background:#f1f5f9; color:#64748b; font-weight:700; padding:10px 20px; border-radius:8px; border:none; cursor:pointer;">Cancel</button>
        <button type="submit" class="btn btn-primary" style="background:#1768ff; color:#fff; font-weight:700; padding:10px 24px; border-radius:8px; border:none; cursor:pointer; box-shadow:0 4px 12px rgba(23,104,255,0.25);">
          Save Changes
        </button>
      </div>
    </form>
  </div>
</div>

<!-- EDIT SCHOLARSHIP MODAL -->
<div id="editScholarshipModal" style="display:none; position:fixed; inset:0; background:rgba(10,25,54,0.65); backdrop-filter:blur(6px); z-index:9999; align-items:center; justify-content:center; padding:20px;">
  <div style="background:#fff; border-radius:16px; max-width:620px; width:100%; max-height:92vh; overflow-y:auto; box-shadow:0 20px 50px rgba(0,0,0,0.3); padding:28px; position:relative;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; border-bottom:1px solid #f1f5f9; padding-bottom:14px;">
      <div>
        <h3 style="margin:0; font-size:19px; font-weight:800; color:#0a1936;"><i data-feather="edit-2" style="width:18px; height:18px; color:#f59e0b; vertical-align:-2px;"></i> Edit Institutional Scholarship</h3>
        <p style="margin:3px 0 0; font-size:12.5px; color:#64748b;">Update award values, deadlines, and eligibility criteria.</p>
      </div>
      <button onclick="document.getElementById('editScholarshipModal').style.display='none'" style="background:#f1f5f9; border:none; border-radius:50%; width:32px; height:32px; cursor:pointer; font-size:16px; font-weight:700; color:#64748b; display:flex; align-items:center; justify-content:center;">&times;</button>
    </div>

    <form id="editScholarshipForm" method="POST" action="" style="display:flex; flex-direction:column; gap:16px;">
      {% csrf_token %}
      <input type="hidden" name="next" value="{{ request.path }}">

      <div>
        <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Scholarship Award Title *</label>
        <input type="text" id="editSchName" name="name" required style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; box-sizing:border-box;">
      </div>

      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:14px;">
        <div>
          <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Coverage / Value *</label>
          <input type="text" id="editSchAmount" name="amount" required style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; box-sizing:border-box;">
        </div>

        <div>
          <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Coverage Type</label>
          <select id="editSchCoverage" name="coverage_type" style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; background:#fff; box-sizing:border-box;">
            <option value="Partial">Partial Waiver</option>
            <option value="Full">Full Tuition Waiver (100%)</option>
            <option value="Grant">Direct Cash Grant / Stipend</option>
          </select>
        </div>
      </div>

      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:14px;">
        <div>
          <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Eligible Academic Level</label>
          <select id="editSchLevel" name="level" style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; background:#fff; box-sizing:border-box;">
            <option value="All Levels">All Levels (UG, PG, PhD)</option>
            <option value="Undergraduate">Undergraduate (UG)</option>
            <option value="Postgraduate">Postgraduate (PG)</option>
            <option value="PhD">Doctoral / PhD</option>
          </select>
        </div>

        <div>
          <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Award Category</label>
          <select id="editSchCategory" name="category" style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; background:#fff; box-sizing:border-box;">
            <option value="Merit-Based">Merit-Based Academic Excellence</option>
            <option value="Need-Based">Need-Based Financial Support</option>
            <option value="Research Fellowship">Research & Doctoral Fellowship</option>
            <option value="International Bursary">International Student Bursary</option>
            <option value="STEM Excellence">Women in STEM / Tech Leadership</option>
          </select>
        </div>
      </div>

      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:14px;">
        <div>
          <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Field / Discipline of Study</label>
          <input type="text" id="editSchField" name="field_of_study" style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; box-sizing:border-box;">
        </div>

        <div>
          <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Application Deadline</label>
          <input type="date" id="editSchDeadline" name="deadline" style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; box-sizing:border-box; background:#fff;">
        </div>
      </div>

      <div>
        <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Eligibility Standards & Criteria</label>
        <textarea id="editSchEligibility" name="eligibility" rows="2" style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; box-sizing:border-box; font-family:inherit;"></textarea>
      </div>

      <div>
        <label style="font-size:12.5px; font-weight:700; color:#0a1936; margin-bottom:4px; display:block;">Overview & Award Description</label>
        <textarea id="editSchDescription" name="description" rows="2" style="width:100%; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:8px; font-size:13.5px; box-sizing:border-box; font-family:inherit;"></textarea>
      </div>

      <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:12px; border-top:1px solid #f1f5f9; padding-top:16px;">
        <button type="button" onclick="document.getElementById('editScholarshipModal').style.display='none'" class="btn" style="background:#f1f5f9; color:#64748b; font-weight:700; padding:10px 20px; border-radius:8px; border:none; cursor:pointer;">Cancel</button>
        <button type="submit" class="btn" style="background:#f59e0b; color:#fff; font-weight:700; padding:10px 24px; border-radius:8px; border:none; cursor:pointer; box-shadow:0 4px 12px rgba(245,158,11,0.25);">
          Save Changes
        </button>
      </div>
    </form>
  </div>
</div>

<script>
function openEditCourseModal(btn) {
    var id = btn.getAttribute('data-id');
    var form = document.getElementById('editCourseForm');
    form.action = '/dashboard/courses/' + id + '/edit/';

    document.getElementById('editCourseName').value = btn.getAttribute('data-name') || '';
    document.getElementById('editCourseDegree').value = btn.getAttribute('data-degree') || 'Undergraduate';
    document.getElementById('editCourseStream').value = btn.getAttribute('data-stream') || '';
    document.getElementById('editCourseDuration').value = btn.getAttribute('data-duration') || '3 Years';
    document.getElementById('editCourseMode').value = btn.getAttribute('data-mode') || 'Full Time';
    document.getElementById('editCourseFees').value = btn.getAttribute('data-fees') || '';
    document.getElementById('editCourseEligibility').value = btn.getAttribute('data-eligibility') || '';
    document.getElementById('editCourseScholarship').checked = (btn.getAttribute('data-scholarship') === '1');

    var modal = document.getElementById('editCourseModal');
    modal.style.display = 'flex';
    if (typeof feather !== 'undefined') feather.replace();
}

function openEditScholarshipModal(btn) {
    var id = btn.getAttribute('data-id');
    var form = document.getElementById('editScholarshipForm');
    form.action = '/dashboard/scholarships/' + id + '/edit/';

    document.getElementById('editSchName').value = btn.getAttribute('data-name') || '';
    document.getElementById('editSchAmount').value = btn.getAttribute('data-amount') || '';
    document.getElementById('editSchCoverage').value = btn.getAttribute('data-coverage') || 'Partial';
    document.getElementById('editSchLevel').value = btn.getAttribute('data-level') || 'All Levels';
    document.getElementById('editSchCategory').value = btn.getAttribute('data-category') || 'Merit-Based';
    document.getElementById('editSchField').value = btn.getAttribute('data-field') || 'All Fields';
    document.getElementById('editSchDeadline').value = btn.getAttribute('data-deadline') || '';
    document.getElementById('editSchEligibility').value = btn.getAttribute('data-eligibility') || '';
    document.getElementById('editSchDescription').value = btn.getAttribute('data-description') || '';

    var modal = document.getElementById('editScholarshipModal');
    modal.style.display = 'flex';
    if (typeof feather !== 'undefined') feather.replace();
}
</script>
"""

if "{% endblock %}" in index_html and "openEditCourseModal" not in index_html:
    idx = index_html.rfind("{% endblock %}")
    index_html = index_html[:idx] + edit_modals_and_js + "\n" + index_html[idx:]
    print("Injected editCourseModal and editScholarshipModal into index.html!")

with open('templates/dashboard/index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

print("Saved templates/dashboard/index.html!")

