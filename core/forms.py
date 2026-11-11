from django import forms

from .models import EventLocation, Exhibitor, Sponsor, Speaker, ProgrammeSession, Registration, ChatbotFAQ


class EventLocationForm(forms.ModelForm):

    class Meta:

        model = EventLocation

        fields = '__all__'

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ExhibitorForm(forms.ModelForm):
    booth_number = forms.ChoiceField(
        required=False,
        label="Allocated Booth Number",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_booth_number'})
    )
    custom_booth_number = forms.CharField(
        max_length=50,
        required=False,
        label="Or Custom Booth Number",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Booth EXH-99 or T-01', 'class': 'form-control', 'id': 'id_custom_booth_number'})
    )
    booth_hall = forms.CharField(
        max_length=100,
        required=False,
        label="Floor Hall / Pavilion",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Hall 1 - Global Pavilion', 'class': 'form-control', 'id': 'id_booth_hall'})
    )

    class Meta:
        model = Exhibitor
        fields = '__all__'

    def __init__(self, *args, is_admin=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not is_admin:
            if 'hero_priority' in self.fields:
                del self.fields['hero_priority']
            if 'is_approved' in self.fields:
                del self.fields['is_approved']

        from .models import ExpoBooth
        current_booth = None
        if self.instance and self.instance.pk:
            if hasattr(self.instance, 'booth') and self.instance.booth:
                current_booth = self.instance.booth
            elif self.instance.university and hasattr(self.instance.university, 'booth') and self.instance.university.booth:
                current_booth = self.instance.university.booth

        # Build dropdown choices
        choices = [('', '-- No Booth (Unallocated) --')]
        if current_booth:
            choices.append((current_booth.booth_number, f"{current_booth.booth_number} (Current Allocation) - {current_booth.hall or 'Main Hall'}"))
            self.fields['booth_number'].initial = current_booth.booth_number
            self.fields['booth_hall'].initial = current_booth.hall

        available_booths = ExpoBooth.objects.filter(status='AVAILABLE', is_active=True).order_by('hall', 'booth_number')
        for b in available_booths:
            if not current_booth or b.booth_number != current_booth.booth_number:
                choices.append((b.booth_number, f"{b.booth_number} ({b.hall or 'Main Hall'})"))

        choices.append(('__custom__', '+ Enter Custom Booth Code...'))
        self.fields['booth_number'].choices = choices

    def save(self, commit=True):
        exhibitor = super().save(commit=commit)
        booth_num = self.cleaned_data.get('booth_number')
        custom_booth = self.cleaned_data.get('custom_booth_number')
        if booth_num == '__custom__' and custom_booth:
            booth_num = custom_booth
        elif booth_num == '__custom__':
            booth_num = ''

        booth_hall = self.cleaned_data.get('booth_hall')
        hall_name = booth_hall.strip() if booth_hall else 'Hall 1 - Global Pavilion'

        if commit:
            from .models import ExpoBooth, University
            from django.db.models import Q
            uni = exhibitor.university
            if not uni:
                uni = University.objects.filter(name__iexact=exhibitor.company_name).first()
                if uni:
                    exhibitor.university = uni
                    exhibitor.save(update_fields=['university'])

            # Clear old booths
            old_booths_q = Q(exhibitor=exhibitor)
            if uni:
                old_booths_q |= Q(university=uni)
            old_booths = ExpoBooth.objects.filter(old_booths_q)
            for old_b in old_booths:
                if not booth_num or old_b.booth_number.strip().lower() != booth_num.strip().lower():
                    old_b.exhibitor = None
                    old_b.university = None
                    old_b.status = 'AVAILABLE'
                    old_b.save()

            if booth_num and booth_num.strip():
                booth_num = booth_num.strip()
                target_booth = ExpoBooth.objects.filter(booth_number__iexact=booth_num).first()
                if not target_booth:
                    import uuid
                    target_booth = ExpoBooth.objects.create(
                        booth_number=booth_num,
                        hall=hall_name,
                        status='ASSIGNED',
                        qr_code=f"BOOTH-{uuid.uuid4().hex[:8].upper()}"
                    )
                if target_booth.exhibitor and target_booth.exhibitor != exhibitor:
                    target_booth.exhibitor = None
                if target_booth.university and target_booth.university != uni:
                    target_booth.university = None

                if hall_name:
                    target_booth.hall = hall_name
                target_booth.exhibitor = exhibitor
                target_booth.university = uni
                target_booth.status = 'ASSIGNED'
                target_booth.save()
        return exhibitor


class SponsorForm(forms.ModelForm):

    class Meta:

        model = Sponsor

        fields = '__all__'


class SpeakerForm(forms.ModelForm):

    class Meta:

        model = Speaker

        fields = '__all__'


class ProgrammeSessionForm(forms.ModelForm):

    class Meta:

        model = ProgrammeSession

        fields = '__all__'

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class RegistrationForm(forms.ModelForm):

    class Meta:

        model = Registration

        fields = '__all__'

from .models import SiteConfiguration, University, UniversityProfile


class SiteConfigurationForm(forms.ModelForm):

    class Meta:

        model = SiteConfiguration

        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


class UniversityForm(forms.ModelForm):

    location_city = forms.CharField(max_length=100, required=False, label="City Location (e.g. Thiruvananthapuram, Cambridge, Boston)")

    location_state_country = forms.CharField(max_length=255, required=False, label="Country (e.g. India, USA, UK, UAE)")

    website = forms.URLField(required=False, label="Official Website URL")

    established_year = forms.IntegerField(required=False, label="Established Year (e.g. 1937)")

    university_type = forms.CharField(max_length=100, required=False, label="University Type (e.g. Public State University, Private Research)")

    accreditation = forms.CharField(max_length=255, required=False, label="Accreditation & Approvals (e.g. NAAC A++, UGC, Privy Council)")

    logo = forms.ImageField(required=False, label="University Logo / Emblem")

    cover_image = forms.ImageField(required=False, label="Campus Banner / Cover Image")

    short_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label="Short Card Summary (Quick Overview)")

    about = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label="About the University")

    campus_facilities = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Campus & Facilities")

    academic_programmes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Academic Programmes & Areas of Specialisation")

    admission_process = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Admission Process & Entry Criteria")

    scholarships_assistance = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Scholarships & Financial Assistance")

    international_support = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="International Student Support")

    career_opportunities = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Career Opportunities & Industry Partnerships")

    why_choose_us = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Why Choose Our University?")

    class Meta:

        model = University

        fields = ['name', 'is_approved', 'hero_priority']

        labels = {
            'name': 'University Name',
            'is_approved': 'Approved (Display on Homepage & Public Directory)',
            'hero_priority': 'Homepage Hero Card Priority (1-3: Left Hero, 4-6: Right Hero, 7-15: Orbit Canvas, 0: Hidden)',
        }

        widgets = {
            'hero_priority': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 99, 'style': 'padding: 10px 14px; border-radius: 8px; border: 1.5px solid #cbd5e1; font-weight: 700; width: 100%;'}),
        }

    def __init__(self, *args, **kwargs):
        is_admin = kwargs.pop('is_admin', True)
        super().__init__(*args, **kwargs)
        if not is_admin:
            if 'hero_priority' in self.fields:
                del self.fields['hero_priority']
            if 'is_approved' in self.fields:
                del self.fields['is_approved']
        if self.instance and self.instance.pk:
            try:
                profile = self.instance.profile
                self.fields['location_city'].initial = profile.location_city
                self.fields['location_state_country'].initial = profile.location_state_country
                self.fields['website'].initial = profile.website
                self.fields['established_year'].initial = profile.established_year
                self.fields['university_type'].initial = profile.university_type
                self.fields['accreditation'].initial = profile.accreditation
                self.fields['short_description'].initial = profile.short_description
                self.fields['about'].initial = profile.about
                self.fields['campus_facilities'].initial = profile.campus_facilities
                self.fields['academic_programmes'].initial = profile.academic_programmes
                self.fields['admission_process'].initial = profile.admission_process
                self.fields['scholarships_assistance'].initial = profile.scholarships_assistance
                self.fields['international_support'].initial = profile.international_support
                self.fields['career_opportunities'].initial = profile.career_opportunities
                self.fields['why_choose_us'].initial = profile.why_choose_us
            except Exception:
                pass
        else:
            self.fields['is_approved'].initial = True
            from django.db.models import Max
            max_pri = University.objects.aggregate(Max('hero_priority'))['hero_priority__max'] or 0
            self.fields['hero_priority'].initial = max_pri + 1
            self.fields['location_city'].initial = 'Global Campus'
            self.fields['location_state_country'].initial = 'International'
            self.fields['university_type'].initial = 'Higher Education Institution'
            self.fields['established_year'].initial = 2000


class ChatbotFAQForm(forms.ModelForm):
    class Meta:
        model = ChatbotFAQ
        fields = ['question', 'chip_label', 'keywords', 'answer', 'order', 'is_chip', 'is_active']
        widgets = {
            'question': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "e.g. How do I get a free ticket?"
            }),
            'chip_label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "e.g. 🎟️ Free Pass (short label for quick suggestion chip)"
            }),
            'keywords': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': "e.g. ticket, entry, free, pass, price, cost, fee (comma-separated)"
            }),
            'answer': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': "Bot answer. Basic HTML allowed, e.g. <p class='mrk-bubble-text'>...</p><a href='/register/' class='mrk-action-link'>Get Free Pass</a>"
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': "0"
            }),
            'is_chip': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'width: 18px; height: 18px; cursor: pointer;'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'width: 18px; height: 18px; cursor: pointer;'
            }),
        }
