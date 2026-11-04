with open('core/dashboard_views.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """    elif 'qa' in user.username.lower():
        role_label = "Admissions Officer"
        subtitle = "Global University"
        avatar_bg = "#0369a1"
        category = "university"
"""

if target in code:
    code = code.replace(target, '')
    print("Removed Global University block from _build_contact_dict.")

target_name = '        elif user.username == \'uni_qa_staff\': name = "Global University Rep"\n'
if target_name in code:
    code = code.replace(target_name, '')
    print("Removed uni_qa_staff name replacement.")

target_rep = """    elif 'qa' in rep_user.username.lower():
        uni_name = "Global University"
        rep_title = "Global University Admissions Coordinator"
"""
if target_rep in code:
    code = code.replace(target_rep, '')
    print("Removed Global University from auto reply.")

with open('core/dashboard_views.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated dashboard_views.py cleanly.")

