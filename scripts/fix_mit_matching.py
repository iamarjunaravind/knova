with open('core/public_views.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """        if exhibitor:
            # Check if this exhibitor corresponds to an existing University
            words = [w.lower() for w in exhibitor.company_name.replace('(', '').replace(')', '').split() if len(w) >= 3 and w.lower() not in ['university', 'global', 'admissions', 'bureau', 'desk', 'international', 'hub', 'pavilion']]
            matching_uni = None
            for w in words:
                matching_uni = University.objects.filter(name__icontains=w).first()
                if matching_uni:
                    break
            if matching_uni:
                return redirect('university_detail', slug=matching_uni.slug)"""

replacement = """        if exhibitor:
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
                return redirect('university_detail', slug=matching_uni.slug)"""

assert target in code, "Target not found in public_views.py"
code = code.replace(target, replacement)

with open('core/public_views.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated MIT matching in public_views.py!")

