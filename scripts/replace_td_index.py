with open('templates/dashboard/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_course_td = """          <td style="padding:14px; text-align:right;">
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
              <form action="{% url 'university_course_delete' course.pk %}" method="POST" onsubmit="return confirm('Remove program {{ course.name|escapejs }}?');" style="display:inline; margin:0;">
                {% csrf_token %}
                <input type="hidden" name="next" value="{{ request.path }}">
                <button type="submit" style="background:#fee2e2; border:1px solid #fecaca; color:#dc2626; cursor:pointer; padding:6px 12px; border-radius:6px; font-size:12px; font-weight:700; display:inline-flex; align-items:center; gap:4px;" title="Delete Course">
                  <i data-feather="trash-2" style="width:13px; height:13px;"></i> Delete
                </button>
              </form>
            </div>
          </td>\n"""

new_sch_td = """          <td style="padding:14px; text-align:right;">
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
              <form action="{% url 'university_scholarship_delete' sch.pk %}" method="POST" onsubmit="return confirm('Remove scholarship award {{ sch.name|escapejs }}?');" style="display:inline; margin:0;">
                {% csrf_token %}
                <input type="hidden" name="next" value="{{ request.path }}">
                <button type="submit" style="background:#fee2e2; border:1px solid #fecaca; color:#dc2626; cursor:pointer; padding:6px 12px; border-radius:6px; font-size:12px; font-weight:700; display:inline-flex; align-items:center; gap:4px;" title="Delete Scholarship">
                  <i data-feather="trash-2" style="width:13px; height:13px;"></i> Delete
                </button>
              </form>
            </div>
          </td>\n"""

# Replace in lines
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if "action=\"{% url 'university_course_delete' course.pk %}\"" in line and i > 0 and "<td style=\"padding:14px; text-align:right;\">" in lines[i-1]:
        # replace td block
        new_lines.pop() # remove the <td> line
        new_lines.append(new_course_td)
        # skip until </td>
        while i < len(lines) and "</td>" not in lines[i]:
            i += 1
        i += 1 # skip </td>
        continue

    if "action=\"{% url 'university_scholarship_delete' sch.pk %}\"" in line and i > 0 and "<td style=\"padding:14px; text-align:right;\">" in lines[i-1]:
        # replace td block
        new_lines.pop() # remove the <td> line
        new_lines.append(new_sch_td)
        # skip until </td>
        while i < len(lines) and "</td>" not in lines[i]:
            i += 1
        i += 1 # skip </td>
        continue

    new_lines.append(line)
    i += 1

with open('templates/dashboard/index.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Updated table rows in templates/dashboard/index.html!")

