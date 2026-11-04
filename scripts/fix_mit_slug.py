with open('core/models.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """    @property
    def slug(self):
        try:
            from .models import University
            words = [w.lower() for w in self.company_name.replace('(', '').replace(')', '').split() if len(w) >= 3 and w.lower() not in ['university', 'global', 'admissions', 'bureau', 'desk', 'international', 'hub', 'pavilion']]
            for w in words:
                uni = University.objects.filter(name__icontains=w).first()
                if uni:
                    return uni.slug
        except Exception:
            pass
        return f"exhibitor-{self.id}\""""

replacement = """    @property
    def slug(self):
        try:
            from .models import University
            if 'mit' in self.company_name.lower().split():
                return 'mit'
            words = [w.lower() for w in self.company_name.replace('(', '').replace(')', '').split() if len(w) >= 3 and w.lower() not in ['university', 'global', 'admissions', 'bureau', 'desk', 'international', 'hub', 'pavilion']]
            for w in words:
                uni = University.objects.filter(name__icontains=w).first()
                if uni:
                    return uni.slug
        except Exception:
            pass
        return f"exhibitor-{self.id}\""""

assert target in code, "Target not found in core/models.py"
code = code.replace(target, replacement)

with open('core/models.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated Exhibitor.slug with mit check!")

