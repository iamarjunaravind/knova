import os
import sys

# 1. Update core/dashboard_views.py
views_path = 'core/dashboard_views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    views_code = f.read()

target_start = """def dashboard_messages(request):
    from .models import DirectMessage
    from django.contrib.auth.models import User
    from django.db.models import Q
    from django.http import JsonResponse
    from django.utils import timezone
    
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'
    action = request.GET.get('action') or request.POST.get('action', '')"""

assert target_start in views_code, "target_start not found in dashboard_views.py"

replacement_start = """def dashboard_messages(request):
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
                        'full_name': reg.full_name,
                        'phone': reg.phone,
                        'preferred_study_level': 'Undergraduate',
                        'preferred_destination': reg.preferred_country or 'Global'
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
                    defaults={'full_name': reg.full_name, 'phone': reg.phone}
                )

    elif email_param:
        resolved_user = User.objects.filter(email__iexact=email_param.strip()).first() or User.objects.filter(username__iexact=email_param.strip()).first()

    if resolved_user:
        active_contact_id = str(resolved_user.id)"""

views_code = views_code.replace(target_start, replacement_start, 1)

# Also update the page load contact list builder in dashboard_messages
target_page_load = """    # 4. Standard View Page Load:
    sent_to = DirectMessage.objects.filter(sender=request.user).values_list('receiver', flat=True)
    received_from = DirectMessage.objects.filter(receiver=request.user).values_list('sender', flat=True)
    contact_ids = set(list(sent_to) + list(received_from))
    
    default_usernames = ['uni_staff1', 'uni_qa_staff', 'exhibitor_test', 'admin']
    if hasattr(request.user, 'university_staff') or request.user.username.startswith('uni_'):
        default_usernames = ['newstudent@test.com', 'student1', 'admin']
        
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
    
    active_contact_id = request.GET.get('contact_id')
    active_contact = None
    if active_contact_id and active_contact_id.isdigit():
        active_contact = next((c for c in contact_list if c['id'] == int(active_contact_id)), None)
        if not active_contact:
            target_user = User.objects.filter(id=int(active_contact_id)).first()
            if target_user:
                active_contact = _build_contact_dict(target_user, request.user)
                contact_list.insert(0, active_contact)
                
    if not active_contact and contact_list:
        active_contact = contact_list[0]"""

assert target_page_load in views_code, "target_page_load not found in dashboard_views.py"

replacement_page_load = """    # 4. Standard View Page Load:
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
        active_contact = contact_list[0]"""

views_code = views_code.replace(target_page_load, replacement_page_load, 1)

with open(views_path, 'w', encoding='utf-8') as f:
    f.write(views_code)

print("Updated core/dashboard_views.py dashboard_messages!")

# 2. Update templates/dashboard/exhibitor_leads.html
leads_tmpl_path = 'templates/dashboard/exhibitor_leads.html'
with open(leads_tmpl_path, 'r', encoding='utf-8') as f:
    leads_tmpl = f.read()

old_link = """<a href="{% url 'dashboard_messages' %}" style="color:var(--primary); font-size:13px; font-weight:600; text-decoration:none;">Message</a>"""
new_link = """<a href="{% url 'dashboard_messages' %}?lead_id={{ lead.id }}" 
                   class="btn-lead-msg" 
                   style="display:inline-flex; align-items:center; gap:5px; color:#1768ff; background:#eff6ff; border:1.5px solid #bfdbfe; font-size:12.5px; font-weight:750; text-decoration:none; padding:6px 14px; border-radius:8px; transition:all 0.15s ease; box-shadow:0 1px 3px rgba(23,104,255,0.08);"
                   title="Direct Message {{ lead.scanned_registration.full_name }}">
                    <i class="ti ti-message-circle" style="font-size:14px;"></i> <span>Message</span>
                </a>"""

assert old_link in leads_tmpl, "old_link not found in exhibitor_leads.html"

# Add style for hover effect
leads_tmpl = leads_tmpl.replace(old_link, new_link, 1)

style_marker = "{% block content %}"
extra_style = """<style>
.btn-lead-msg:hover {
    background: #1768ff !important;
    color: #ffffff !important;
    border-color: #1768ff !important;
    box-shadow: 0 4px 12px rgba(23,104,255,0.28) !important;
    transform: translateY(-1px);
}
</style>
"""
leads_tmpl = leads_tmpl.replace(style_marker, style_marker + "\n" + extra_style, 1)

with open(leads_tmpl_path, 'w', encoding='utf-8') as f:
    f.write(leads_tmpl)

print("Updated templates/dashboard/exhibitor_leads.html with lead_id link and styling!")

