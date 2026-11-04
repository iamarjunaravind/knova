pub_path = 'core/public_views.py'
with open(pub_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Replace lines 1183-1190 (pop_sch)
start_sch = None
end_sch = None
for i, l in enumerate(lines):
    if "'type': 'Scholarship', 'title': '100% Full Tuition" in l:
        start_sch = i
    if start_sch and "return JsonResponse({'results': popular})" in l:
        end_sch = i
        break

assert start_sch and end_sch, "Scholarship block not found"

new_sch_lines = [
    "            popular = []\n",
    "            for s in Scholarship.objects.select_related('university')[:6]:\n",
    "                popular.append({\n",
    "                    'type': 'Scholarship',\n",
    "                    'title': s.name,\n",
    "                    'subtitle': f\"{s.university.name if s.university else 'Open Grant'} • {s.coverage_type}\",\n",
    "                    'query_val': s.name,\n",
    "                    'url': f\"{reverse('public_scholarships')}?q={s.name}\",\n",
    "                    'icon': 'ti ti-medal'\n",
    "                })\n"
]

lines = lines[:start_sch-1] + new_sch_lines + lines[end_sch:]

# 2. Replace popular exhibitors
start_exh = None
end_exh = None
for i, l in enumerate(lines):
    if "if scope == 'exhibitors':" in l and "if not query:" in lines[i+1]:
        start_exh = i + 2
    if start_exh and "return JsonResponse({'results': popular})" in l:
        end_exh = i
        break

assert start_exh and end_exh, "Exhibitors block not found"

new_exh_lines = [
    "            popular = []\n",
    "            for u in University.objects.filter(is_approved=True).select_related('profile')[:6]:\n",
    "                loc = u.profile.location_city if hasattr(u, 'profile') and u.profile.location_city else 'International'\n",
    "                popular.append({\n",
    "                    'type': 'University',\n",
    "                    'title': u.name,\n",
    "                    'subtitle': f\"{loc} • Exhibitor\",\n",
    "                    'query_val': u.name,\n",
    "                    'url': f\"{reverse('public_exhibitors')}?q={u.name}\",\n",
    "                    'icon': 'ti ti-building-bank'\n",
    "                })\n",
    "            for exh in Exhibitor.objects.all()[:4]:\n",
    "                popular.append({\n",
    "                    'type': 'Exhibitor',\n",
    "                    'title': exh.company_name,\n",
    "                    'subtitle': f\"{exh.booth_number or 'Booth'} • Partner\",\n",
    "                    'query_val': exh.company_name,\n",
    "                    'url': f\"{reverse('public_exhibitors')}?q={exh.company_name}\",\n",
    "                    'icon': 'ti ti-briefcase'\n",
    "                })\n"
]

lines = lines[:start_exh] + new_exh_lines + lines[end_exh:]

# 3. Replace popular courses
start_cou = None
end_cou = None
for i, l in enumerate(lines):
    if "if scope == 'courses':" in l and "popular = [" in lines[i+1]:
        start_cou = i + 1
    if start_cou and "return JsonResponse({'results': popular})" in l:
        end_cou = i
        break

assert start_cou and end_cou, "Courses block not found"

new_cou_lines = [
    "            popular = []\n",
    "            for c in Course.objects.select_related('university')[:6]:\n",
    "                popular.append({\n",
    "                    'type': 'Course',\n",
    "                    'title': c.name,\n",
    "                    'subtitle': f\"{c.university.name if c.university else 'Degree'} • {c.degree_level}\",\n",
    "                    'query_val': c.name,\n",
    "                    'url': f\"{reverse('courses_list')}?q={c.name}\",\n",
    "                    'icon': 'ti ti-sparkles'\n",
    "                })\n"
]

lines = lines[:start_cou] + new_cou_lines + lines[end_cou:]

with open(pub_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Successfully replaced all 3 popular search fallback blocks in public_views.py!")

