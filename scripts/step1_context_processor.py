with open('core/context_processors.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_func = """def user_university(request):
    uni = None
    if hasattr(request, 'user') and request.user.is_authenticated:
        if hasattr(request.user, 'university_staff') and request.user.university_staff:
            uni = getattr(request.user.university_staff, 'university', None)
        if not uni and hasattr(request.user, 'exhibitor_profile') and request.user.exhibitor_profile:
            from .models import University
            exh = request.user.exhibitor_profile
            uni = University.objects.filter(name__iexact=exh.company_name).first()
            if not uni:
                first_word = exh.company_name.split()[0]
                if len(first_word) >= 3:
                    uni = University.objects.filter(name__icontains=first_word).first()
    return {'user_university': uni}
"""

if 'def user_university' not in text:
    text = text.strip() + "\n\n" + new_func + "\n"
    with open('core/context_processors.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Added user_university to core/context_processors.py")

with open('knova_backend/settings.py', 'r', encoding='utf-8') as f:
    settings_code = f.read()

if "'core.context_processors.user_university'" not in settings_code:
    settings_code = settings_code.replace(
        "'core.context_processors.base_template',",
        "'core.context_processors.base_template',\n                'core.context_processors.user_university',"
    )
    with open('knova_backend/settings.py', 'w', encoding='utf-8') as f:
        f.write(settings_code)
    print("Added user_university to knova_backend/settings.py TEMPLATES")

