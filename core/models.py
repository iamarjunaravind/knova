from django.db import models
from django.contrib.auth.models import User


class EventLocation(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    timings = models.CharField(max_length=100)
    venue = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_upcoming = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.city}"


class Exhibitor(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='exhibitor_profile')
    company_name = models.CharField(max_length=255, db_index=True)
    event_location = models.ForeignKey(EventLocation, on_delete=models.CASCADE, related_name='exhibitors')
    profile_description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='exhibitor_logos/', blank=True, null=True)
    brochure = models.FileField(upload_to='exhibitor_brochures/', blank=True, null=True)

    # Matchmaking Criteria
    country = models.CharField(max_length=100, blank=True, db_index=True)
    tuition_range = models.CharField(max_length=50, blank=True, choices=[('Low', 'Under $10k'), ('Medium', '$10k-$30k'), ('High', 'Over $30k')])
    offered_programs = models.TextField(blank=True, help_text="Comma separated list of major programs")
    is_verified = models.BooleanField(default=False, db_index=True)

    @property
    def name(self):
        return self.company_name

    @property
    def profile(self):
        class ExhibitorProfileAdapter:
            def __init__(self, ex):
                self.location_state_country = ex.country or (ex.event_location.city if ex.event_location else 'Global')
                self.location_city = ex.event_location.city if ex.event_location else ''
                self.logo = ex.logo
                self.cover_image = None
                self.website = ex.website
                self.established_year = ""
                self.university_type = "Higher Education Institution"
                self.accreditation = "Accredited University / Exhibitor"
                self.short_description = ex.profile_description or f"{ex.company_name} is an accredited educational institution and verified exhibitor."
                self.about = ex.profile_description or f"{ex.company_name} is an accredited educational institution offering recognized undergraduate and postgraduate degree programs."
                self.campus_facilities = "Modern academic lecture halls, research facilities, student advisory desks, and digital learning suites."
                self.admission_process = "Direct applications and scholarship evaluations are conducted at the university booth. Meet with admissions representatives for portfolio reviews."
                self.description = self.short_description
        return ExhibitorProfileAdapter(self)

    @property
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
        return f"exhibitor-{self.id}"

    @property
    def courses_count(self):
        return 0

    @property
    def scholarships_count(self):
        return 0

    @property
    def booth_number(self):
        if hasattr(self, 'booth') and self.booth:
            return self.booth.booth_number
        return None

    @property
    def booth_hall(self):
        if hasattr(self, 'booth') and self.booth:
            return self.booth.hall
        return None

    def __str__(self):
        return self.company_name


class ExhibitorStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='exhibitor_staff_profile')
    exhibitor = models.ForeignKey(Exhibitor, on_delete=models.CASCADE, related_name='staff_members')
    role = models.CharField(max_length=50, choices=[('Admin', 'Admin'), ('Scanner', 'Scanner')], default='Scanner')

    def __str__(self):
        return f"{self.user.username} - {self.exhibitor.company_name}"


class ExhibitorLead(models.Model):
    RATING_CHOICES = [
        ('Hot', 'Hot'),
        ('Warm', 'Warm'),
        ('Cold', 'Cold'),
    ]
    SOURCE_CHOICES = [
        ('Punch', 'Punch'),
        ('Book', 'Book'),
        ('Punch & Book', 'Punch & Book'),
    ]
    exhibitor = models.ForeignKey(Exhibitor, on_delete=models.CASCADE, related_name='captured_leads')
    scanned_registration = models.ForeignKey('Registration', on_delete=models.CASCADE, related_name='scanned_by_exhibitors')
    scanned_at = models.DateTimeField(auto_now_add=True)
    rating = models.CharField(max_length=10, choices=RATING_CHOICES, blank=True, null=True)
    lead_source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='Punch', blank=True)
    action_tags = models.CharField(max_length=255, blank=True, help_text="Comma separated tags e.g. Send Brochure, Interview")
    notes = models.TextField(blank=True, help_text="Internal notes by the exhibitor")

    class Meta:
        unique_together = ('exhibitor', 'scanned_registration')

    def __str__(self):
        return f"{self.exhibitor.company_name} captured {self.scanned_registration.full_name}"

    @property
    def display_source(self):
        if self.lead_source in ['Punch & Book', 'Book', 'Punch']:
            return self.lead_source
        if 'Course Booking' in (self.action_tags or '') or 'Booked Course' in (self.notes or ''):
            return 'Book'
        return 'Punch'


class ExhibitorMeeting(models.Model):
    exhibitor = models.ForeignKey(Exhibitor, on_delete=models.CASCADE, related_name='scheduled_meetings')
    student_registration = models.ForeignKey('Registration', on_delete=models.CASCADE, related_name='exhibitor_meetings')
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_time']

    def __str__(self):
        return f"Meeting: {self.exhibitor.company_name} & {self.student_registration.full_name}"


class Sponsor(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sponsor_profile')
    CATEGORY_CHOICES = [
        ('Platinum', 'Platinum'),
        ('Gold', 'Gold'),
        ('Silver', 'Silver'),
        ('Bronze', 'Bronze')
    ]
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    event_location = models.ForeignKey(EventLocation, on_delete=models.CASCADE, related_name='sponsors')
    profile = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='sponsor_logos/', blank=True, null=True)
    is_verified = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


class Speaker(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='speaker_profile')
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    profile = models.TextField(blank=True)
    photo = models.ImageField(upload_to='speaker_photos/', blank=True, null=True)
    is_verified = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.name


class ProgrammeSession(models.Model):
    title = models.CharField(max_length=255)
    event_location = models.ForeignKey(EventLocation, on_delete=models.CASCADE, related_name='sessions')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    hall_name = models.CharField(max_length=100)
    speaker = models.ForeignKey(Speaker, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} at {self.event_location.city}"

    @property
    def coordinator_staff(self):
        return self.staff_members.first()

    @property
    def login_username(self):
        staff = self.coordinator_staff
        return staff.user.username if staff and staff.user else None

    @property
    def login_password(self):
        staff = self.coordinator_staff
        return staff.raw_password if staff else 'seminar123'

    @property
    def attendances_count(self):
        return self.attendances.count()


class Registration(models.Model):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Parent', 'Parent'),
        ('Exhibitor', 'Exhibitor'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Checked-in', 'Checked-in'),
    ]
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, db_index=True)
    event_location = models.ForeignKey(EventLocation, on_delete=models.SET_NULL, null=True)
    interested_in = models.ManyToManyField('Exhibitor', blank=True, related_name='interested_students')

    # Matchmaking Preferences
    preferred_country = models.CharField(max_length=100, blank=True)
    budget_range = models.CharField(max_length=50, blank=True, choices=[('Low', 'Under $10k'), ('Medium', '$10k-$30k'), ('High', 'Over $30k')])
    preferred_program = models.CharField(max_length=100, blank=True)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending', db_index=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    is_checked_in = models.BooleanField(default=False)
    registration_id = models.CharField(max_length=50, unique=True, blank=True, null=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.registration_id:
            from .utils import generate_unique_attendee_id
            self.registration_id = generate_unique_attendee_id(self.role)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class BoothVisit(models.Model):
    student = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='booth_visits')
    exhibitor = models.ForeignKey('Exhibitor', on_delete=models.CASCADE, related_name='visited_by_students')
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'exhibitor')

    def __str__(self):
        return f"{self.student.full_name} visited {self.exhibitor.company_name}"


class ChatLead(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    captured_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"


class ChatbotFAQ(models.Model):
    question = models.CharField(max_length=255, help_text="Full question or query title (e.g. 'How do I get a free ticket?')")
    chip_label = models.CharField(max_length=100, blank=True, help_text="Short label for suggestion chip carousel (e.g. '🎟️ Free Pass')")
    keywords = models.TextField(help_text="Comma-separated keywords for NLP matching (e.g. 'ticket, entry, free, pass, price, cost')")
    answer = models.TextField(help_text="Bot response text (supports HTML tags like <p>, <strong>, <a href=...>)")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_chip = models.BooleanField(default=True, help_text="Show as a quick suggestion chip button")
    is_active = models.BooleanField(default=True, help_text="Enable or disable this Q&A")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Chatbot Q&A"
        verbose_name_plural = "Chatbot Q&As"

    def __str__(self):
        return self.chip_label or self.question


class SiteConfiguration(models.Model):
    # SEO & Branding
    meta_title = models.CharField(max_length=255, default="KNOVA — Future Begins Here")
    meta_description = models.TextField(default="Meet world-class universities, discover global study opportunities and connect with education experts at KNOVA GCC.")

    # ==========================================
    # SEO, SEARCH CONSOLE & SOCIAL MEDIA SHARING
    # ==========================================
    meta_keywords = models.CharField(max_length=500, blank=True, default="KNOVA Expo, global education, study abroad, international universities, scholarships, higher education GCC, Dubai education expo, university admissions", help_text="Comma-separated SEO keywords")
    canonical_base_url = models.CharField(max_length=255, blank=True, default="http://127.0.0.1:8004", help_text="Base canonical URL (e.g. https://knovaexpo.com)")
    robots_meta = models.CharField(max_length=50, default="index, follow", choices=[
        ('index, follow', 'Index, Follow (Recommended - Allow search engines to index & follow)'),
        ('noindex, follow', 'Noindex, Follow (Do not index page, but follow links)'),
        ('index, nofollow', 'Index, Nofollow (Index page, but do not follow links)'),
        ('noindex, nofollow', 'Noindex, Nofollow (Completely block search engines)')
    ])
    robots_txt_content = models.TextField(blank=True, default="User-agent: *\nAllow: /\nDisallow: /dashboard/\nDisallow: /portal/\nDisallow: /admin/\nSitemap: /sitemap.xml", help_text="Content for robots.txt")

    # Open Graph (Social Sharing Previews)
    og_title = models.CharField(max_length=255, blank=True, default="", help_text="Leave blank to default to Meta Title")
    og_description = models.TextField(blank=True, default="", help_text="Leave blank to default to Meta Description")
    og_image = models.CharField(max_length=500, blank=True, default="/static/assets/bahrain_promo.webp", help_text="URL or static path to social share image (1200x630 recommended)")
    og_type = models.CharField(max_length=50, default="website")
    og_site_name = models.CharField(max_length=150, default="KNOVA Global Education Expo")

    # Twitter Cards
    twitter_card_type = models.CharField(max_length=50, default="summary_large_image", choices=[
        ('summary_large_image', 'Summary Card with Large Image (Recommended)'),
        ('summary', 'Standard Summary Card')
    ])
    twitter_handle = models.CharField(max_length=100, blank=True, default="@knovaexpo", help_text="Twitter @handle for the site")
    twitter_creator = models.CharField(max_length=100, blank=True, default="@knovaexpo")

    # Webmaster & Verification
    google_site_verification = models.CharField(max_length=255, blank=True, default="", help_text="Google Search Console verification code")
    bing_site_verification = models.CharField(max_length=255, blank=True, default="", help_text="Bing Webmaster verification code")

    # Analytics & Tracking Snippets
    google_analytics_id = models.CharField(max_length=50, blank=True, default="", help_text="Google Analytics 4 Measurement ID (e.g. G-XXXXXXXXXX)")
    google_tag_manager_id = models.CharField(max_length=50, blank=True, default="", help_text="Google Tag Manager ID (e.g. GTM-XXXXXXX)")
    custom_head_code = models.TextField(blank=True, default="", help_text="Custom HTML / tracking scripts injected right before </head> (e.g. Meta Pixel, TikTok Pixel, custom meta tags)")
    custom_body_code = models.TextField(blank=True, default="", help_text="Custom HTML / scripts injected right before </body>")

    # Schema.org Structured Data
    enable_schema_org = models.BooleanField(default=True, verbose_name="Enable Schema.org JSON-LD Structured Data")
    schema_org_name = models.CharField(max_length=255, default="KNOVA Global Education Expo")

    # Per-Page SEO Overrides
    seo_about_title = models.CharField(max_length=255, blank=True, default="About KNOVA | Premier Global Education Expo")
    seo_about_desc = models.TextField(blank=True, default="Learn about the mission, vision and world-class universities partnering with KNOVA across the GCC.")
    seo_courses_title = models.CharField(max_length=255, blank=True, default="Academic Programs & Degree Courses | KNOVA")
    seo_courses_desc = models.TextField(blank=True, default="Explore 1000+ accredited undergraduate, postgraduate and doctoral degree courses.")
    seo_exhibitors_title = models.CharField(max_length=255, blank=True, default="Participating Universities & Exhibitors | KNOVA")
    seo_exhibitors_desc = models.TextField(blank=True, default="Meet admissions deans from 60+ world-class universities across the USA, UK, Europe and Asia.")
    seo_events_title = models.CharField(max_length=255, blank=True, default="Event Locations, Venues & Expo Schedule | KNOVA")
    seo_events_desc = models.TextField(blank=True, default="Explore dates, convention center locations, transit maps and daily timing schedules.")
    seo_scholarships_title = models.CharField(max_length=255, blank=True, default="International Scholarships & Tuition Grants | KNOVA")
    seo_scholarships_desc = models.TextField(blank=True, default="Apply for over $5M+ in verified merit scholarships, tuition waivers and grants.")
    seo_speakers_title = models.CharField(max_length=255, blank=True, default="Keynote Speakers & University Deans | KNOVA")
    seo_speakers_desc = models.TextField(blank=True, default="Hear from global education leaders, university presidents and admissions mentors.")
    seo_map_title = models.CharField(max_length=255, blank=True, default="Interactive Expo Floor Map & Hall Directory | KNOVA")
    seo_map_desc = models.TextField(blank=True, default="Navigate university discovery pavilions, counseling hubs, and stage halls live.")
    seo_sponsors_title = models.CharField(max_length=255, blank=True, default="Official Partners & Global Sponsors | KNOVA")
    seo_sponsors_desc = models.TextField(blank=True, default="Discover our strategic education partners, corporate sponsors and government bodies.")

    # ==========================================
    # SECTION VISIBILITY TOGGLES (HOMEPAGE)
    # ==========================================
    show_hero_section = models.BooleanField(default=True, verbose_name="Hero Section & 3D Interactive Floor")
    show_university_cards = models.BooleanField(default=True, verbose_name="Show Floating University Cards in Hero Arena")
    show_hero_disclaimer = models.BooleanField(default=True, verbose_name="Hero Video Disclaimer (Right Bottom)")
    show_stats_bar = models.BooleanField(default=True, verbose_name="Quick Stats Bar")
    show_why_section = models.BooleanField(default=True, verbose_name="Why KNOVA / More Than an Expo")
    show_sponsors_marquee = models.BooleanField(default=True, verbose_name="Sponsors & Partners Marquee")
    show_events_section = models.BooleanField(default=True, verbose_name="Upcoming Events / Expos")
    show_how_section = models.BooleanField(default=True, verbose_name="Academic Majors & How It Works")
    show_exhibitors_section = models.BooleanField(default=True, verbose_name="Featured Exhibitors & Universities")
    show_programme_section = models.BooleanField(default=True, verbose_name="Programme & Masterclasses")
    show_speakers_section = models.BooleanField(default=True, verbose_name="Keynote Speakers")
    show_map_section = models.BooleanField(default=True, verbose_name="Interactive Floor Map Preview")
    show_scholarships_section = models.BooleanField(default=True, verbose_name="Scholarships & Financial Aid")
    show_experience_section = models.BooleanField(default=True, verbose_name="Experience Highlights & Testimonials Section")
    show_experience_video_card = models.BooleanField(default=True, verbose_name="Experience: Expo Highlights Video Card (Left)")
    show_experience_testimonial_card = models.BooleanField(default=True, verbose_name="Experience: Student Testimonial Quote Card (Right)")
    show_faq_section = models.BooleanField(default=True, verbose_name="Frequently Asked Questions (FAQ)")
    show_faq_support_card = models.BooleanField(default=False, verbose_name="FAQ: 1-on-1 Guidance Support Card (Left Column)")
    show_register_cta_section = models.BooleanField(default=True, verbose_name="Register Today Call-to-Action")

    # ==========================================
    # SECTION VISIBILITY TOGGLES (ABOUT US PAGE)
    # ==========================================
    show_about_hero = models.BooleanField(default=True, verbose_name="About: Hero Header & Intro")
    show_about_nav = models.BooleanField(default=True, verbose_name="About: Sticky Navigation Hub")
    show_about_overview = models.BooleanField(default=True, verbose_name="About: Executive Overview & Feature Pillars")
    show_about_spotlight = models.BooleanField(default=False, verbose_name="About: Media Spotlight & Video Card")
    show_about_metrics = models.BooleanField(default=True, verbose_name="About: Key Scale & Impact Metrics")
    show_about_mission = models.BooleanField(default=True, verbose_name="About: Mission & Foundational Pillars")
    show_about_values = models.BooleanField(default=True, verbose_name="About: Core Institutional Values")
    show_about_journey = models.BooleanField(default=True, verbose_name="About: Growth Journey Timeline")
    show_about_cta = models.BooleanField(default=True, verbose_name="About: Ready to Discover Degree Pathway CTA")

    # ==========================================
    # SECTION VISIBILITY TOGGLES (EVENTS & EXPOS PAGE)
    # ==========================================
    show_events_hero = models.BooleanField(default=True, verbose_name="Events: Hero Header & Search Bar")
    show_events_featured = models.BooleanField(default=True, verbose_name="Events: Featured Flagship Expo Card")
    show_events_calendar = models.BooleanField(default=True, verbose_name="Events: GCC City Tour Calendar")
    show_events_zones = models.BooleanField(default=True, verbose_name="Events: Inside the Expo Activity Zones")

    # ==========================================
    # SECTION VISIBILITY TOGGLES (EXHIBITORS & UNIVERSITIES PAGE)
    # ==========================================
    show_exhibitors_hero = models.BooleanField(default=True, verbose_name="Exhibitors: Hero Header & Stats")
    show_exhibitors_filters = models.BooleanField(default=True, verbose_name="Exhibitors: Filter Hub & Search")
    show_exhibitors_grid = models.BooleanField(default=True, verbose_name="Exhibitors: University Cards Grid & Results")

    # ==========================================
    # SECTION VISIBILITY TOGGLES (SCHOLARSHIPS & GRANTS PAGE)
    # ==========================================
    show_scholarships_hero = models.BooleanField(default=True, verbose_name="Scholarships: Hero Header & Stats")
    show_scholarships_filters = models.BooleanField(default=True, verbose_name="Scholarships: Filter Hub & Search")
    show_scholarships_grid = models.BooleanField(default=True, verbose_name="Scholarships: Grant Opportunities Grid")
    show_scholarships_cbt_teaser = models.BooleanField(default=True, verbose_name="Scholarships: Aptitude Exam Teaser")

    # ==========================================
    # SECTION VISIBILITY TOGGLES (KEYNOTE SPEAKERS PAGE)
    # ==========================================
    show_speakers_hero = models.BooleanField(default=True, verbose_name="Speakers: Hero Header & Search")
    show_speakers_filters = models.BooleanField(default=True, verbose_name="Speakers: Filter Tabs")
    show_speakers_grid = models.BooleanField(default=True, verbose_name="Speakers: Keynote Speakers Grid")
    show_speakers_cta = models.BooleanField(default=True, verbose_name="Speakers: Call for Speakers CTA")

    # ==========================================
    # SECTION VISIBILITY TOGGLES (PROGRAMME SCHEDULE PAGE)
    # ==========================================
    show_programme_hero = models.BooleanField(default=True, verbose_name="Programme: Hero Header")
    show_programme_filters = models.BooleanField(default=True, verbose_name="Programme: Day & Track Filters")
    show_programme_schedule = models.BooleanField(default=True, verbose_name="Programme: Sessions Timeline")
    show_programme_cta = models.BooleanField(default=True, verbose_name="Programme: Register / Calendar CTA")

    # ==========================================
    # SECTION VISIBILITY TOGGLES (SPONSORS & PARTNERS PAGE)
    # ==========================================
    show_sponsors_hero = models.BooleanField(default=True, verbose_name="Sponsors: Hero Header & Stats")
    show_sponsors_filters = models.BooleanField(default=True, verbose_name="Sponsors: Tier Filter Chips")
    show_sponsors_platinum = models.BooleanField(default=True, verbose_name="Sponsors: Platinum Tier Partners")
    show_sponsors_gold = models.BooleanField(default=True, verbose_name="Sponsors: Gold Strategic Tier")
    show_sponsors_silver = models.BooleanField(default=True, verbose_name="Sponsors: Silver & Media Tier")
    show_sponsors_cta = models.BooleanField(default=True, verbose_name="Sponsors: Partnership Deck CTA")

    # ==========================================
    # SECTION VISIBILITY TOGGLES (INTERACTIVE FLOOR MAP PAGE)
    # ==========================================
    show_map_hero = models.BooleanField(default=True, verbose_name="Map: Hero Header & Controls")
    show_map_viewer = models.BooleanField(default=True, verbose_name="Map: Interactive 2D/3D Hall Viewport")
    show_map_directory = models.BooleanField(default=True, verbose_name="Map: Hall & Booth Directory Sidebar")
    show_map_legend = models.BooleanField(default=True, verbose_name="Map: Floor Zone Legend Bar")

    # ==========================================
    # SECTION VISIBILITY TOGGLES (COURSES DIRECTORY PAGE)
    # ==========================================
    show_courses_hero = models.BooleanField(default=True, verbose_name="Courses: Hero Header & Stats")
    show_courses_filters = models.BooleanField(default=True, verbose_name="Courses: Filter Hub")
    show_courses_grid = models.BooleanField(default=True, verbose_name="Courses: Degree Courses Grid")

    # ==========================================
    # SECTION VISIBILITY TOGGLES (KNOVA CHALLENGE PAGE)
    # ==========================================
    show_challenge_hero = models.BooleanField(default=True, verbose_name="Challenge: Hero Header & Stats")
    show_challenge_flow = models.BooleanField(default=True, verbose_name="Challenge: Quest Flow Stepper Track")
    show_challenge_missions = models.BooleanField(default=True, verbose_name="Challenge: Passport 6 Missions Grid")
    show_challenge_activity = models.BooleanField(default=True, verbose_name="Challenge: Real-time Activity Log")
    show_challenge_guide = models.BooleanField(default=True, verbose_name="Challenge: How Passport Works Guide")

    # ==========================================
    # SECTION VISIBILITY TOGGLES (REGISTRATION PAGE)
    # ==========================================
    show_register_showcase = models.BooleanField(default=True, verbose_name="Register: Left Atmosphere & Feature Showcase")
    show_register_form = models.BooleanField(default=True, verbose_name="Register: Right Registration Card & Form")

    # ==========================================
    # SECTION VISIBILITY TOGGLES (LEGAL & POLICY PAGES)
    # ==========================================
    show_privacy_hero = models.BooleanField(default=True, verbose_name="Privacy: Header Banner")
    show_privacy_content = models.BooleanField(default=True, verbose_name="Privacy: Legal Body Text")
    show_terms_hero = models.BooleanField(default=True, verbose_name="Terms: Header Banner")
    show_terms_content = models.BooleanField(default=True, verbose_name="Terms: Legal Body Text")

    # ==========================================
    # NAVIGATION BAR LINKS TOGGLES
    # ==========================================
    show_nav_home = models.BooleanField(default=True, verbose_name="Nav: Home")
    show_nav_about = models.BooleanField(default=True, verbose_name="Nav: About")
    show_nav_programs = models.BooleanField(default=True, verbose_name="Nav: Programs")
    show_nav_events = models.BooleanField(default=True, verbose_name="Nav: Events")
    show_nav_exhibitors = models.BooleanField(default=True, verbose_name="Nav: Exhibitors")
    show_nav_scholarships = models.BooleanField(default=True, verbose_name="Nav: Scholarships")
    show_nav_sponsors = models.BooleanField(default=True, verbose_name="Nav: Sponsors")
    show_nav_challenge = models.BooleanField(default=True, verbose_name="Nav: Challenge")
    show_nav_my_expo = models.BooleanField(default=True, verbose_name="Nav: My Expo")

    # ==========================================
    # NAVBAR DISABLE / MAKE NOT CLICKABLE TOGGLES
    # ==========================================
    disable_navbar = models.BooleanField(default=False, verbose_name="Disable Entire Navbar")
    disable_nav_home = models.BooleanField(default=False, verbose_name="Disable Link: Home")
    disable_nav_about = models.BooleanField(default=False, verbose_name="Disable Link: About")
    disable_nav_programs = models.BooleanField(default=False, verbose_name="Disable Link: Programs")
    disable_nav_events = models.BooleanField(default=False, verbose_name="Disable Link: Events")
    disable_nav_exhibitors = models.BooleanField(default=False, verbose_name="Disable Link: Exhibitors")
    disable_nav_scholarships = models.BooleanField(default=False, verbose_name="Disable Link: Scholarships")
    disable_nav_sponsors = models.BooleanField(default=False, verbose_name="Disable Link: Sponsors")
    disable_nav_challenge = models.BooleanField(default=False, verbose_name="Disable Link: Challenge")
    disable_nav_my_expo = models.BooleanField(default=False, verbose_name="Disable Link: My Expo")

    # ==========================================
    # HOMEPAGE CONTENT
    # ==========================================
    # Hero Section
    hero_badge_text = models.CharField(max_length=100, default="KNOVA 2027", blank=True)
    hero_badge_subtext = models.CharField(max_length=100, default="Presented By", blank=True)
    hero_title_line1 = models.CharField(max_length=255, default="Your Choice.")
    hero_title_line2 = models.CharField(max_length=255, default="Your University.")
    hero_subtitle = models.TextField(default="Discover diverse academic courses, meet representatives from 50+ universities, and explore opportunities to shape your future")
    hero_primary_btn_text = models.CharField(max_length=100, default="Explore Your Future", blank=True)
    hero_primary_btn_url = models.CharField(max_length=255, default="#exhibitors", blank=True)
    hero_secondary_btn_text = models.CharField(max_length=100, default="Register for Expo", blank=True)
    hero_secondary_btn_url = models.CharField(max_length=255, default="/register/", blank=True)
    hero_search_placeholder = models.CharField(max_length=255, default="Search universities, courses or keywords...", blank=True)
    hero_video_disclaimer = models.CharField(max_length=255, default="The video is for illustration purpose only. Not real, AI generated", blank=True)
    hero_image = models.ImageField(upload_to='site_images/', blank=True, null=True, help_text="Main hero image (leave blank for default)")
    hero_logo = models.ImageField(upload_to='site_images/', blank=True, null=True, help_text="Presented-By Sponsor Logo in Hero (leave blank for default)")
    site_logo = models.ImageField(upload_to='site_images/', blank=True, null=True, help_text="Main Website Header Logo (leave blank for default)")
    site_footer_logo = models.ImageField(upload_to='site_images/', blank=True, null=True, help_text="Footer Logo (leave blank for default)")
    map_image = models.ImageField(upload_to='site_images/', blank=True, null=True, help_text="Venue Floor Plan Map Image (leave blank for default)")
    testimonial_image = models.ImageField(upload_to='site_images/', blank=True, null=True, help_text="Student Testimonial photo (leave blank for default)")
    featured_expo_image = models.ImageField(upload_to='site_images/', blank=True, null=True, help_text="Featured City Skyline photo (leave blank for default)")
    register_hero_image = models.ImageField(upload_to='site_images/', blank=True, null=True, help_text="Registration pages side cityscape photo (leave blank for default)")
    chatbot_avatar = models.ImageField(upload_to='site_images/', blank=True, null=True, help_text="Chatbot Mr. K avatar image (leave blank for default)")

    # Quick Stats Bar
    stat_1_number = models.CharField(max_length=50, default="1000+", blank=True)
    stat_1_label = models.CharField(max_length=100, default="COURSES", blank=True)
    stat_2_number = models.CharField(max_length=50, default="50+", blank=True)
    stat_2_label = models.CharField(max_length=100, default="UNIVERSITY", blank=True)
    stat_3_number = models.CharField(max_length=50, default="1-ON-1", blank=True)
    stat_3_label = models.CharField(max_length=100, default="SESSIONS", blank=True)
    stat_4_number = models.CharField(max_length=50, default="Unlock 50+", blank=True)
    stat_4_label = models.CharField(max_length=100, default="SCHOLARSHIP", blank=True)

    # Why KNOVA Section
    why_badge = models.CharField(max_length=100, default="WHY KNOVA EXPO", blank=True)
    why_title = models.CharField(max_length=255, default="More Than an Expo.")
    why_title_gradient = models.CharField(max_length=255, default="A Global Opportunity.")
    why_text = models.TextField(default="Explore programmes, meet universities, learn from global experts, and plan your education journey.")
    why_image = models.ImageField(upload_to='site_images/', blank=True, null=True, help_text="Image next to the Why section")

    # Section Headings & Subtitles across Homepage
    events_heading = models.CharField(max_length=255, default="Event Locations")
    events_subtitle = models.CharField(max_length=255, default="HOST CITIES & DATES", blank=True)
    events_view_all_text = models.CharField(max_length=100, default="View All Locations →", blank=True)
    events_view_all_url = models.CharField(max_length=255, default="/events/", blank=True)
    
    # Event Locations & Tour Expansion Section (Homepage Section 2)
    event_card_badge = models.CharField(max_length=100, default="CONFIRMED EVENT", blank=True)
    event_card_summit = models.CharField(max_length=100, default="2027 EDUCATION EXPO", blank=True)
    event_card_kicker = models.CharField(max_length=200, default="Regional and Global Education Expo", blank=True)
    event_card_entry = models.CharField(max_length=100, default="", blank=True)
    event_card_title = models.CharField(max_length=255, default="KNOVA 2027 , BAHRAIN EDITION", blank=True)
    event_card_dates = models.CharField(max_length=150, default="March 25 – 27, 2027", blank=True)
    event_card_venue = models.CharField(max_length=255, default="Crowne Plaza by IHG Bahrain, Bahrain", blank=True)
    event_card_timings = models.CharField(max_length=150, default="03:30 PM - 10:00 PM On 25th & 26th / 10:00 AM to 3:30 PM on 27th", blank=True)
    event_perk1 = models.CharField(max_length=100, default="50+ Universities", blank=True)
    event_perk2 = models.CharField(max_length=100, default="", blank=True)
    event_perk3 = models.CharField(max_length=100, default="", blank=True)
    event_btn_text = models.CharField(max_length=100, default="View My Expo Pass →", blank=True)
    event_btn_url = models.CharField(max_length=255, default="/register/", blank=True)
    event_details_btn_text = models.CharField(max_length=100, default="Full Event Details >", blank=True)
    event_details_btn_url = models.CharField(max_length=255, default="/events/", blank=True)

    # Tour Expansion Card
    tour_badge = models.CharField(max_length=100, default="", blank=True)
    tour_title = models.CharField(max_length=200, default="More Cities Coming Soon", blank=True)
    tour_desc = models.TextField(default="KNOVA is expanding across the GCC. Pre-register your city to receive early announcements and updates:", blank=True)
    tour_city1_name = models.CharField(max_length=150, default="Doha, Qatar", blank=True)
    tour_city1_status = models.CharField(max_length=100, default="Announcing Soon", blank=True)
    tour_city2_name = models.CharField(max_length=150, default="Al Khobar, Saudi Arabia", blank=True)
    tour_city2_status = models.CharField(max_length=100, default="Announcing Soon", blank=True)
    tour_city3_name = models.CharField(max_length=150, default="", blank=True)
    tour_city3_status = models.CharField(max_length=100, default="", blank=True)
    tour_btn_text = models.CharField(max_length=100, default="Pre-Register For Alerts →", blank=True)
    tour_btn_url = models.CharField(max_length=255, default="/register/", blank=True)
    exhibitors_heading = models.CharField(max_length=255, default="Featured Exhibitors")
    exhibitors_subtitle = models.CharField(max_length=255, default="Meet admissions officers and deans from world-renowned institutions.", blank=True)
    speakers_heading = models.CharField(max_length=255, default="Inspiring Speakers")
    speakers_subtitle = models.CharField(max_length=255, default="Learn from global thought leaders, academic deans and industry innovators.", blank=True)
    programme_heading = models.CharField(max_length=255, default="Programme & Seminars")
    programme_subtitle = models.CharField(max_length=255, default="Attend keynote presentations, masterclasses, and interactive workshops.", blank=True)
    scholarships_heading = models.CharField(max_length=255, default="Scholarships & Financial Aid")
    scholarships_subtitle = models.CharField(max_length=255, default="Discover merit awards, tuition grants, and financial support packages.", blank=True)
    map_heading = models.CharField(max_length=255, default="Interactive Expo Floor Map")
    map_subtitle = models.CharField(max_length=255, default="Explore the KNOVA exhibition floor plan, discover participating exhibition zones, and get a closer look at the experience awaiting you.", blank=True)
    faq_heading = models.CharField(max_length=255, default="Frequently Asked Questions")
    faq_subtitle = models.CharField(max_length=255, default="Everything you need to know about attending KNOVA 2027.", blank=True)
    cta_heading = models.CharField(max_length=255, default="Ready to Shape Your Future?")
    cta_subtitle = models.CharField(max_length=255, default="Register today to claim your fast-track digital badge and personalized expo itinerary.", blank=True)
    cta_btn_text = models.CharField(max_length=100, default="Register for Expo", blank=True)

    # ==========================================
    # SERVICES & PUBLIC PAGES CONTENT
    # ==========================================
    # About Page
    about_title = models.CharField(max_length=255, default="Bridging Aspirations <span class=\"gradient-text\">and Education</span>")
    about_subtitle = models.TextField(default="Where ambition meets opportunity. Bringing students, families and educational institutions together to connect, explore possibilities and shape the future of education.")
    about_mission = models.TextField(default="To bridge the gap between world-class global education and aspiring students across the GCC through interactive, transparent, and technology-driven expo experiences.")
    about_vision = models.TextField(default="To become the premier regional and global education expo in the Middle East, fostering cross-border academic excellence and lifelong student success.")
    about_history = models.TextField(default="Established in 2024, KNOVA has connected tens of thousands of students with leading universities from the UK, USA, Europe, Asia, and the Middle East.", blank=True)

    about_hero_badge = models.CharField(max_length=200, default="OFFICIAL MISSION & INSTITUTIONAL PROFILE", blank=True)
    about_hero_title = models.CharField(max_length=255, default="Bridging Aspirations and Education", blank=True)
    about_hero_subtitle = models.TextField(default="Where ambition meets opportunity. Bringing students, families and educational institutions together to connect, explore possibilities and shape the future of education.", blank=True)
    about_hero_btn1_text = models.CharField(max_length=100, default="Watch 2-Min Overview", blank=True)
    about_hero_btn2_text = models.CharField(max_length=100, default="Register for Expo", blank=True)
    about_hero_btn2_url = models.CharField(max_length=255, default="/register/", blank=True)

    about_overview_heading = models.CharField(max_length=255, default="Where Education Connects, Futures Take Shape.", blank=True)
    about_overview_desc = models.TextField(default="KNOVA is an integrated education platform designed to connect the diverse education ecosystem through physical experiences and digital engagement. Bringing together academic institutions, universities, education professionals, students and families, KNOVA facilitates meaningful connections across local, regional and international markets.\n\nThrough exhibitions, institutional collaborations, digital platforms and ongoing engagement, KNOVA extends the reach of education beyond traditional boundaries creating an interconnected space for knowledge exchange, opportunity discovery and informed academic decision making.", blank=True)
    about_overview_card1_title = models.CharField(max_length=200, default="Inspire Ambition", blank=True)
    about_overview_card1_desc = models.TextField(default="Be part of the conversations that encourage students to dream bigger", blank=True)
    about_overview_card2_title = models.CharField(max_length=200, default="Meaningful Connections", blank=True)
    about_overview_card2_desc = models.TextField(default="Engage with students and families exploring their educational options", blank=True)
    about_overview_card3_title = models.CharField(max_length=200, default="Open New Possibilities", blank=True)
    about_overview_card3_desc = models.TextField(default="Introduce your programmes and pathways to aspiring learners.", blank=True)
    about_overview_card4_title = models.CharField(max_length=200, default="A Commitment to Quality", blank=True)
    about_overview_card4_desc = models.TextField(default="A considered approach to planning, coordination and the exhibitor experience, led by Lumentra Ventures.", blank=True)
    about_quote_text = models.TextField(default="Higher education is the single most powerful catalyst for individual transformation and regional economic diversification. Our mission is to make world-class learning accessible without borders.", blank=True)
    about_quote_author = models.CharField(max_length=255, default="Executive Director, KNOVA Regional & Global Education Expo", blank=True)

    # About Media Spotlight & Video Card
    about_spotlight_image = models.ImageField(upload_to='site_images/', blank=True, null=True, help_text="Custom spotlight image for About page overview card")
    about_spotlight_badge = models.CharField(max_length=100, default="Expo In-Session", blank=True)
    about_spotlight_video_url = models.CharField(max_length=255, default="https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ", blank=True, help_text="YouTube embed or video URL for overview modal")
    about_spotlight_caption_top = models.CharField(max_length=150, default="KNOVA Regional & Global Education Expo", blank=True)
    about_spotlight_caption_sub = models.CharField(max_length=100, default="2027 Intake", blank=True)
    about_spotlight_stat1 = models.CharField(max_length=100, default="98.4% Match Rate", blank=True)
    about_spotlight_stat2 = models.CharField(max_length=100, default="Global Attendees", blank=True)
    about_spotlight_stat3 = models.CharField(max_length=100, default="Direct Offers", blank=True)

    about_metrics_heading = models.CharField(max_length=255, default="The KNOVA Reach", blank=True)
    about_metrics_desc = models.TextField(default="A snapshot of the reach, participation and opportunities that make KNOVA a platform for the future.", blank=True)
    about_metric1_val = models.CharField(max_length=50, default="10,000+", blank=True)
    about_metric1_label = models.CharField(max_length=100, default="Projected Visitors", blank=True)
    about_metric2_val = models.CharField(max_length=50, default="50+", blank=True)
    about_metric2_label = models.CharField(max_length=100, default="Universities", blank=True)
    about_metric3_val = models.CharField(max_length=50, default="35+", blank=True)
    about_metric3_label = models.CharField(max_length=100, default="Countries Represented", blank=True)
    about_metric4_val = models.CharField(max_length=50, default="50+", blank=True)
    about_metric4_label = models.CharField(max_length=100, default="Scholarship Opportunities", blank=True)

    about_mission_heading = models.CharField(max_length=255, default="Our Mission & Principles", blank=True)
    about_mission_title = models.CharField(max_length=200, default="Connecting Education. Creating Possibilities", blank=True)
    about_mission_desc = models.TextField(default="KNOVA was born from a simple yet powerful belief, education thrives when right people, institutions and opportunities come together.\n\nWhat began as an idea has evolved into a growing education platform designed to bring together universities, academic institutions, educators, students and families across local, regional and international landscapes.\n\nGoing beyond traditional exhibitions, KNOVA creates meaningful connections through physical experiences, digital platforms and ongoing institutional engagement. We aim to make education more accessible, knowledge more discoverable and opportunities more connected.\n\nBecause the future of education isn't shaped by institutions alone, but by the connections we build between them.", blank=True)
    about_vision_title = models.CharField(max_length=200, default="Institutional Vision", blank=True)
    about_vision_desc = models.TextField(default="A borderless knowledge society where every ambitious student in the GCC has direct access to accredited international degrees aligned with future economic and technological demands.", blank=True)
    about_pillar1_title = models.CharField(max_length=200, default="1. Democratize Access", blank=True)
    about_pillar1_desc = models.TextField(default="Removing geographic and bureaucratic barriers by bringing authorized university representatives directly to Gulf host cities.", blank=True)
    about_pillar2_title = models.CharField(max_length=200, default="2. Empower with Clarity", blank=True)
    about_pillar2_desc = models.TextField(default="Providing independent, verified insights into degree curricula, post-study work regulations, and high-value scholarships.", blank=True)
    about_pillar3_title = models.CharField(max_length=200, default="3. Foster Global Networks", blank=True)
    about_pillar3_desc = models.TextField(default="Cultivating enduring institutional partnerships between GCC educational authorities, high schools, and premier global universities.", blank=True)

    about_values_heading = models.CharField(max_length=255, default="Opportunities That Go Beyond the Expo", blank=True)
    about_values_desc = models.TextField(default="", blank=True)
    about_val1_title = models.CharField(max_length=200, default="Connect with Tomorrow's Decision Makers:", blank=True)
    about_val1_desc = models.TextField(default="Engage directly with students exploring higher education and parents who play an important role in academic decisions.", blank=True)
    about_val2_title = models.CharField(max_length=200, default="Turn Conversations into Opportunities:", blank=True)
    about_val2_desc = models.TextField(default="Discuss programmes, admissions, scholarships where available, and academic pathways face-to-face, creating opportunities for meaningful follow-up with interested students.", blank=True)
    about_val3_title = models.CharField(max_length=200, default="Extend Your Reach Beyond the Expo:", blank=True)
    about_val3_desc = models.TextField(default="Introduce your institution through KNOVA's physical exhibition and digital platform, creating opportunities for visibility and engagement beyond the event dates.", blank=True)
    about_val4_title = models.CharField(max_length=200, default="Explore Strategic Partnerships:", blank=True)
    about_val4_desc = models.TextField(default="Explore potential connections with schools, institutions, and relevant public and private sector stakeholders.", blank=True)

    about_journey_heading = models.CharField(max_length=255, default="Powered by Lumentra Ventures", blank=True)
    about_journey_desc = models.TextField(default="KNOVA is conceived, developed and organised by Lumentra Ventures, a Bahrain based events and education platform company focused on creating meaningful connections across the education ecosystem.", blank=True)
    about_step1_badge = models.CharField(max_length=100, default="Phase 1: 2024", blank=True)
    about_step1_title = models.CharField(max_length=200, default="Regional Genesis & First Expo", blank=True)
    about_step1_desc = models.TextField(default="Launched the first regional education forum, uniting 30+ premier institutions with 2,500+ attendees in Dubai.", blank=True)
    about_step2_badge = models.CharField(max_length=100, default="Phase 2: 2025", blank=True)
    about_step2_title = models.CharField(max_length=200, default="GCC Tri-City Expansion", blank=True)
    about_step2_desc = models.TextField(default="Expanded across Dubai, Riyadh, and Doha, doubling institutional participation and student delegate turnout.", blank=True)
    about_step3_badge = models.CharField(max_length=100, default="Phase 3: 2026", blank=True)
    about_step3_title = models.CharField(max_length=200, default="Digital Intelligence Platform", blank=True)
    about_step3_desc = models.TextField(default="Integrated virtual counselor matching, verified scholarship exam booking, and digital application fast-tracking.", blank=True)
    about_step4_badge = models.CharField(max_length=100, default="Present: 2027", blank=True)
    about_step4_title = models.CharField(max_length=200, default="The Premier Education Expo", blank=True)
    about_step4_desc = models.TextField(default="Connecting global universities, aspiring delegates, and verified scholarship aid pools across the GCC.", blank=True)

    about_cta_title = models.CharField(max_length=255, default="Every Journey Begins with a Possibility.", blank=True)
    about_cta_desc = models.TextField(default="", blank=True)
    about_cta_btn1_text = models.CharField(max_length=100, default="Register for Expo", blank=True)
    about_cta_btn1_url = models.CharField(max_length=255, default="/register/", blank=True)
    about_cta_btn2_text = models.CharField(max_length=100, default="Explore 1000+ Courses", blank=True)
    about_cta_btn2_url = models.CharField(max_length=255, default="/courses/", blank=True)

    # Events Page
    events_page_title = models.CharField(max_length=255, default="Regional & Global Education Expo")
    events_page_subtitle = models.CharField(max_length=255, default="Discover leading universities, explore academic opportunities, connect with education experts and take the next step towards your future.")
    events_page_notice = models.CharField(max_length=255, default="Free admission for registered attendees. Present digital QR badge at the registration gate.", blank=True)

    events_hero_badge = models.CharField(max_length=200, default="REGIONAL & GLOBAL EDUCATION EXPO TOUR", blank=True)
    events_hero_title = models.CharField(max_length=255, default="Global Education Expos & Keynote Seminars 2027", blank=True)
    events_hero_subtitle = models.TextField(default="Meet face-to-face with visiting university deans, secure direct spot offers, and explore $50M+ in international merit scholarships across premier GCC convention venues.", blank=True)
    events_search_placeholder = models.CharField(max_length=255, default="Search by city, venue, or expo title (e.g. Dubai, Riyadh, Bahrain)...", blank=True)
    events_btn_map_text = models.CharField(max_length=100, default="Explore Floorplan Map", blank=True)
    events_btn_myexpo_text = models.CharField(max_length=100, default="My Expo Pass", blank=True)

    events_featured_kicker = models.CharField(max_length=100, default="", blank=True)
    events_featured_badge = models.CharField(max_length=100, default="CONFIRMED 2027", blank=True)
    events_featured_desc = models.TextField(default="", blank=True)
    events_featured_btn1_text = models.CharField(max_length=100, default="Register for Expo", blank=True)
    events_featured_btn2_text = models.CharField(max_length=100, default="View Floor Map", blank=True)
    events_featured_btn3_text = models.CharField(max_length=100, default="Add to Google Calendar", blank=True)

    events_calendar_heading = models.CharField(max_length=255, default="GCC City Tour Calendar", blank=True)
    events_calendar_subtitle = models.CharField(max_length=255, default="Confirmed multi-city higher education exhibitions and keynote auditoriums across the Gulf region.", blank=True)
    events_card_btn_register = models.CharField(max_length=100, default="Register for Expo", blank=True)
    events_card_btn_map = models.CharField(max_length=100, default="View Map", blank=True)

    events_zones_heading = models.CharField(max_length=255, default="Inside the Expo: Activity Zones", blank=True)
    events_zones_subtitle = models.CharField(max_length=255, default="Every KNOVA expo features four specialized activity concourses for students and families.", blank=True)
    events_zone1_title = models.CharField(max_length=200, default="University Pavilions", blank=True)
    events_zone1_desc = models.TextField(default="Booths 01–60: Meet university admissions directors and deans directly.", blank=True)
    events_zone2_title = models.CharField(max_length=200, default="Counselling & Visa Hub", blank=True)
    events_zone2_desc = models.TextField(default="1-on-1 certified advisors for study abroad and embassy visa requirements.", blank=True)
    events_zone3_title = models.CharField(max_length=200, default="Aptitude & Career Lab", blank=True)
    events_zone3_desc = models.TextField(default="Psychometric evaluations and personality career guidance for students.", blank=True)
    events_zone4_title = models.CharField(max_length=200, default="Scholarship Testing", blank=True)
    events_zone4_desc = models.TextField(default="On-spot diagnostic assessments and fast-track tuition fee waiver interviews.", blank=True)


    # Exhibitors Page
    exhibitors_page_title = models.CharField(max_length=255, default="World-Class Exhibitors & Universities")
    exhibitors_page_subtitle = models.CharField(max_length=255, default="Browse accredited universities, college representatives, and educational partners attending KNOVA.")

    # Scholarships Page
    scholarships_page_title = models.CharField(max_length=255, default="Global Scholarships & Grants")
    scholarships_page_subtitle = models.CharField(max_length=255, default="Explore merit-based, need-based, and institutional financial aid grants available for 2026/2027.")
    scholarships_page_intro = models.TextField(default="Every year, KNOVA partner universities offer exclusive funding opportunities. Book your scholarship examination slot to qualify.", blank=True)

    # Speakers Page
    speakers_page_title = models.CharField(max_length=255, default="Distinguished Keynotes & Academic Leaders")
    speakers_page_subtitle = models.CharField(max_length=255, default="Hear from global education innovators, university chancellors, and career strategists.")

    # Programme Page
    programme_page_title = models.CharField(max_length=255, default="Expo Programme & Masterclass Schedule")
    programme_page_subtitle = models.CharField(max_length=255, default="Plan your expo itinerary with comprehensive session timetables, speaker panels, and workshops.")

    # Sponsors Page
    sponsors_page_title = models.CharField(max_length=255, default="Official Sponsors & Visionary Partners")
    sponsors_page_subtitle = models.CharField(max_length=255, default="Recognizing the industry leaders and philanthropic endowments powering global youth mobility.")

    # Floor Map Page
    map_page_title = models.CharField(max_length=255, default="Interactive Expo Floor Map & Hall Directory")
    map_page_subtitle = models.CharField(max_length=255, default="Locate university booths, keynote stages, counseling hubs, and sponsor pavilions across the Main Exhibition Hall.")

    # Courses Page
    courses_page_title = models.CharField(max_length=255, default="Academic Programs & Degrees")
    courses_page_subtitle = models.CharField(max_length=255, default="Filter hundreds of verified bachelor's, master's, and doctoral programs across world universities.")

    # Challenge Page
    challenge_page_title = models.CharField(max_length=255, default="KNOVA Challenge Passport")
    challenge_page_subtitle = models.CharField(max_length=255, default="Scan QR codes at exhibitor booths, complete interactive quests, and win official merchandise and grants.")

    # Exhibitors Page Content
    exhibitors_badge = models.CharField(max_length=100, default="GLOBAL EDUCATION DIRECTORY", blank=True)
    exhibitors_kpi1_val = models.CharField(max_length=50, default="50+", blank=True)
    exhibitors_kpi1_label = models.CharField(max_length=100, default="Global Universities", blank=True)
    exhibitors_kpi2_val = models.CharField(max_length=50, default="12+", blank=True)
    exhibitors_kpi2_label = models.CharField(max_length=100, default="Countries Represented", blank=True)
    exhibitors_kpi3_val = models.CharField(max_length=50, default="1,000+", blank=True)
    exhibitors_kpi3_label = models.CharField(max_length=100, default="Accredited Programs", blank=True)
    exhibitors_kpi4_val = models.CharField(max_length=50, default="100%", blank=True)
    exhibitors_kpi4_label = models.CharField(max_length=100, default="Spot Evaluation Support", blank=True)
    exhibitors_search_placeholder = models.CharField(max_length=255, default="Search by university name, country, city, or keyword...", blank=True)

    # ==========================================
    # UNIVERSITY DETAIL PUBLIC PAGE (/university/<slug>/)
    # ==========================================
    uni_detail_partner_badge = models.CharField(max_length=100, default="Verified Partner", blank=True)
    uni_detail_kpi1_label = models.CharField(max_length=100, default="Degree Programs", blank=True)
    uni_detail_kpi2_label = models.CharField(max_length=100, default="Scholarships & Aid", blank=True)
    uni_detail_kpi3_val = models.CharField(max_length=100, default="UG • PG • PhD", blank=True)
    uni_detail_kpi3_label = models.CharField(max_length=100, default="Study Levels", blank=True)
    uni_detail_kpi4_val = models.CharField(max_length=100, default="Open for 2026/27", blank=True)
    uni_detail_kpi4_label = models.CharField(max_length=100, default="Intake Status", blank=True)

    # 4 Highlights
    uni_detail_hl1_title = models.CharField(max_length=150, default="Global Standing", blank=True)
    uni_detail_hl1_desc = models.CharField(max_length=255, default="Internationally accredited degree credentials", blank=True)
    uni_detail_hl2_title = models.CharField(max_length=150, default="Expert Faculty", blank=True)
    uni_detail_hl2_desc = models.CharField(max_length=255, default="Learn directly from leading scholars & researchers", blank=True)
    uni_detail_hl3_title = models.CharField(max_length=150, default="Career Placement", blank=True)
    uni_detail_hl3_desc = models.CharField(max_length=255, default="Dedicated global internship & employment network", blank=True)
    uni_detail_hl4_title = models.CharField(max_length=150, default="Student Support", blank=True)
    uni_detail_hl4_desc = models.CharField(max_length=255, default="Comprehensive visa, housing & academic advisory", blank=True)

    # 4 Campus Facilities
    uni_detail_fac1_title = models.CharField(max_length=150, default="Smart Libraries & Archives", blank=True)
    uni_detail_fac1_desc = models.CharField(max_length=255, default="24/7 digital resource access, private study pods, and collaborative innovation zones.", blank=True)
    uni_detail_fac2_title = models.CharField(max_length=150, default="Advanced Research Labs", blank=True)
    uni_detail_fac2_desc = models.CharField(max_length=255, default="Industry-standard technology suites, computing clusters, and specialized workshops.", blank=True)
    uni_detail_fac3_title = models.CharField(max_length=150, default="Student Housing & Halls", blank=True)
    uni_detail_fac3_desc = models.CharField(max_length=255, default="Safe, comfortable residences with dining options, high-speed WiFi, and 24/7 security.", blank=True)
    uni_detail_fac4_title = models.CharField(max_length=150, default="Athletics & Recreation", blank=True)
    uni_detail_fac4_desc = models.CharField(max_length=255, default="Multi-sport complexes, fitness gyms, swimming facilities, and dynamic cultural clubs.", blank=True)

    # 3 Admissions Steps
    uni_detail_step1_title = models.CharField(max_length=150, default="Choose & Inquire", blank=True)
    uni_detail_step1_desc = models.CharField(max_length=255, default="Select your desired degree program and review specific academic prerequisites.", blank=True)
    uni_detail_step2_title = models.CharField(max_length=150, default="Counseling & Review", blank=True)
    uni_detail_step2_desc = models.CharField(max_length=255, default="Meet 1-on-1 with an authorized advisor to evaluate transcripts and scholarship chances.", blank=True)
    uni_detail_step3_title = models.CharField(max_length=150, default="Direct Submission", blank=True)
    uni_detail_step3_desc = models.CharField(max_length=255, default="Receive fast-track offer letters, accommodation booking, and visa assistance.", blank=True)

    # Sidebar Callback Card
    uni_detail_callback_title = models.CharField(max_length=150, default="Enquire & Get Call Back", blank=True)
    uni_detail_callback_sub = models.CharField(max_length=150, default="• Direct Admissions Callback", blank=True)
    uni_detail_callback_desc = models.TextField(default="Have questions about admissions, fees, or courses? Request a fast call back from our advisory team.", blank=True)
    uni_detail_callback_btn = models.CharField(max_length=100, default="Request Call Back", blank=True)
    uni_detail_callback_perk1 = models.CharField(max_length=200, default="Direct call back from authorized advisors", blank=True)
    uni_detail_callback_perk2 = models.CharField(max_length=200, default="Instant fee structure & scholarship guidance", blank=True)
    uni_detail_callback_perk3 = models.CharField(max_length=200, default="1-on-1 personalized response", blank=True)

    # Scholarships Page Content
    scholarships_badge = models.CharField(max_length=100, default="MERIT & NEED-BASED FINANCIAL AID", blank=True)
    scholarships_kpi1_val = models.CharField(max_length=50, default="$2.5M+", blank=True)
    scholarships_kpi1_label = models.CharField(max_length=100, default="Total Grant Pool", blank=True)
    scholarships_kpi2_val = models.CharField(max_length=50, default="25+", blank=True)
    scholarships_kpi2_label = models.CharField(max_length=100, default="Partner Grants", blank=True)
    scholarships_kpi3_val = models.CharField(max_length=50, default="Up to 100%", blank=True)
    scholarships_kpi3_label = models.CharField(max_length=100, default="Tuition Coverage", blank=True)
    scholarships_kpi4_val = models.CharField(max_length=50, default="48 Hrs", blank=True)
    scholarships_kpi4_label = models.CharField(max_length=100, default="Spot Decision Track", blank=True)
    scholarships_search_placeholder = models.CharField(max_length=255, default="Search scholarships by title, university, field...", blank=True)

    # Speakers Page Content
    speakers_badge = models.CharField(max_length=100, default="GLOBAL THOUGHT LEADERS & MENTORS", blank=True)
    speakers_cta_title = models.CharField(max_length=200, default="Interested in Speaking at KNOVA 2027?", blank=True)
    speakers_cta_desc = models.TextField(default="Share your expertise with thousands of aspiring students, educators, and global university deans.", blank=True)
    speakers_cta_btn_text = models.CharField(max_length=100, default="Apply as Keynote Speaker", blank=True)
    speakers_cta_btn_url = models.CharField(max_length=255, default="mailto:connect@knovaexpo.com?subject=Speaker%20Connection%20-%20KNOVA%202027", blank=True)

    # Programme Page Content
    programme_badge = models.CharField(max_length=100, default="OFFICIAL EXPO ITINERARY", blank=True)
    programme_cta_title = models.CharField(max_length=200, default="Don't Miss Any Exclusive Masterclass", blank=True)
    programme_cta_desc = models.TextField(default="Seats for VIP keynote sessions are limited. Register today to receive real-time schedule alerts.", blank=True)
    programme_cta_btn_text = models.CharField(max_length=100, default="Register for Expo", blank=True)

    # Sponsors Page Content
    sponsors_badge = models.CharField(max_length=100, default="GLOBAL INDUSTRY & EDUCATION LEADERS", blank=True)
    sponsors_kpi1_val = models.CharField(max_length=50, default="30+", blank=True)
    sponsors_kpi1_label = models.CharField(max_length=100, default="Corporate & Govt Partners", blank=True)
    sponsors_kpi2_val = models.CharField(max_length=50, default="15k+", blank=True)
    sponsors_kpi2_label = models.CharField(max_length=100, default="Target Attendees", blank=True)
    sponsors_kpi3_val = models.CharField(max_length=50, default="50+", blank=True)
    sponsors_kpi3_label = models.CharField(max_length=100, default="Media Outlets", blank=True)
    sponsors_kpi4_val = models.CharField(max_length=50, default="100%", blank=True)
    sponsors_kpi4_label = models.CharField(max_length=100, default="GCC & Regional Visibility", blank=True)
    sponsors_cta_title = models.CharField(max_length=200, default="Partner with KNOVA 2027", blank=True)
    sponsors_cta_desc = models.TextField(default="Position your brand in front of top students, universities, government bodies, and international education agencies.", blank=True)
    sponsors_cta_btn_text = models.CharField(max_length=100, default="Download Partnership Deck", blank=True)

    # Map Page Content
    map_badge = models.CharField(max_length=100, default="LIVE EXPO HALL BLUEPRINT", blank=True)
    map_search_placeholder = models.CharField(max_length=255, default="Search booths by university, hall, or stall number...", blank=True)

    # Courses Page Content
    courses_badge = models.CharField(max_length=100, default="GLOBAL DEGREE FINDER", blank=True)
    courses_kpi1_val = models.CharField(max_length=50, default="1,200+", blank=True)
    courses_kpi1_label = models.CharField(max_length=100, default="Programs Indexed", blank=True)
    courses_kpi2_val = models.CharField(max_length=50, default="45+", blank=True)
    courses_kpi2_label = models.CharField(max_length=100, default="Specializations", blank=True)
    courses_kpi3_val = models.CharField(max_length=50, default="15+", blank=True)
    courses_kpi3_label = models.CharField(max_length=100, default="Study Destinations", blank=True)
    courses_kpi4_val = models.CharField(max_length=50, default="100%", blank=True)
    courses_kpi4_label = models.CharField(max_length=100, default="Direct University Apply", blank=True)
    courses_search_placeholder = models.CharField(max_length=255, default="Search courses by title, discipline, degree level...", blank=True)

    # Challenge Page Content
    challenge_badge = models.CharField(max_length=100, default="INTERACTIVE GAMIFIED EXPO QUEST", blank=True)
    challenge_cta_text = models.CharField(max_length=255, default="Complete all missions to unlock the Grand Prize Draw & Official ID Badge!", blank=True)

    # Register Page Content
    register_showcase_title = models.CharField(max_length=255, default='Reserve Your<br><span class="reg-highlight">Expo Pass</span>', blank=True)
    register_showcase_subtitle = models.TextField(default="Where aspirations meet opportunities.\nConnect with leading universities, explore scholarships and discover the possibilities that shape your future.", blank=True)
    register_form_title = models.CharField(max_length=255, default="Register for Free Expo Pass", blank=True)
    register_form_subtitle = models.TextField(default="Instant digital badge with QR check-in sent to your email.", blank=True)

    # Privacy Policy Page Content
    privacy_page_title = models.CharField(max_length=255, default="Privacy Policy", blank=True)
    privacy_last_updated = models.CharField(max_length=100, default="November 2026", blank=True)
    privacy_body_content = models.TextField(blank=True, default="", help_text="Custom HTML or text for the privacy policy. If empty, the default legal text is shown.")

    # Terms & Conditions Page Content
    terms_page_title = models.CharField(max_length=255, default="Terms and Conditions", blank=True)
    terms_last_updated = models.CharField(max_length=100, default="November 2026", blank=True)
    terms_body_content = models.TextField(blank=True, default="", help_text="Custom HTML or text for terms and conditions. If empty, the default legal text is shown.")

    # ==========================================
    # WHY KNOVA CHECKLIST & 4 FEATURE CARDS
    # ==========================================
    why_check1 = models.CharField(max_length=255, default="Direct evaluations & fee waivers", blank=True)
    why_check2 = models.CharField(max_length=255, default="Personalized guidance for students & families", blank=True)
    why_check3 = models.CharField(max_length=255, default="Official Digital Certificate of Participation", blank=True)
    why_btn_text = models.CharField(max_length=100, default="Learn More About KNOVA →", blank=True)

    why_card1_badge = models.CharField(max_length=100, default="1000+ Courses", blank=True)
    why_card1_title = models.CharField(max_length=200, default="Explore Programmes", blank=True)
    why_card1_desc = models.TextField(default="Find the right undergraduate, PG, or doctoral course", blank=True)
    why_card1_btn = models.CharField(max_length=100, default="Explore Courses →", blank=True)

    why_card2_badge = models.CharField(max_length=100, default="50+ Top Unis", blank=True)
    why_card2_title = models.CharField(max_length=200, default="Meet Universities", blank=True)
    why_card2_desc = models.TextField(default="World-class institutions & admissions reps under one roof", blank=True)
    why_card2_btn = models.CharField(max_length=100, default="View Booths →", blank=True)

    why_card3_badge = models.CharField(max_length=100, default="1-on-1 Sessions", blank=True)
    why_card3_title = models.CharField(max_length=200, default="Learn from Experts", blank=True)
    why_card3_desc = models.TextField(default="Keynote sessions, career advisory & test masterclasses", blank=True)
    why_card3_btn = models.CharField(max_length=100, default="Meet Experts →", blank=True)

    why_card4_badge = models.CharField(max_length=100, default="50% Scholarship", blank=True)
    why_card4_title = models.CharField(max_length=200, default="Plan & Fund Studies", blank=True)
    why_card4_desc = models.TextField(default="Verified global scholarships, tuition waivers & grants", blank=True)
    why_card4_btn = models.CharField(max_length=100, default="Unlock \u2192", blank=True)

    # ==========================================
    # HOW IT WORKS 4 STEPS & FEATURE CARD
    # ==========================================
    how_kicker = models.CharField(max_length=100, default="SIMPLE 4-STEP JOURNEY", blank=True)
    how_heading = models.CharField(max_length=255, default="How to Participate", blank=True)
    how_subtitle = models.TextField(default="A streamlined, guided roadmap from registration to your university offer.", blank=True)
    
    how_step1_badge = models.CharField(max_length=100, default="STEP 01", blank=True)
    how_step1_title = models.CharField(max_length=200, default="Register for Expo", blank=True)
    how_step1_desc = models.TextField(default="Create your student ID", blank=True)

    how_step2_badge = models.CharField(max_length=100, default="STEP 02", blank=True)
    how_step2_title = models.CharField(max_length=200, default="Get Digital Pass", blank=True)
    how_step2_desc = models.TextField(default="Scan booths & keynotes", blank=True)

    how_step3_badge = models.CharField(max_length=100, default="STEP 03", blank=True)
    how_step3_title = models.CharField(max_length=200, default="Plan Your Agenda", blank=True)
    how_step3_desc = models.TextField(default="Shortlist seminars & talks", blank=True)

    how_step4_badge = models.CharField(max_length=100, default="STEP 04", blank=True)
    how_step4_title = models.CharField(max_length=200, default="Meet Universities", blank=True)
    how_step4_desc = models.TextField(default="Secure offers & funding", blank=True)

    how_card_badge = models.CharField(max_length=100, default="FEATURED EVENT", blank=True)
    how_card_title = models.CharField(max_length=200, default="The Main Expo", blank=True)
    how_card_desc = models.TextField(default="Join us at the flagship KNOVA 2027 Education Expo in 3 GCC locations.", blank=True)
    how_card_btn = models.CharField(max_length=100, default="View Event Details →", blank=True)

    # ==========================================
    # PARTICIPATE SECTION: ATTENDANCE & REACH STATS BAR
    # ==========================================
    participate_stat_1_title = models.CharField(max_length=150, default="Projected Visitors", blank=True)
    participate_stat_1_number = models.CharField(max_length=50, default="10000", blank=True)
    participate_stat_1_desc = models.CharField(max_length=255, default="Target attendance across three days", blank=True)

    participate_stat_2_title = models.CharField(max_length=150, default="Schools to Reach", blank=True)
    participate_stat_2_number = models.CharField(max_length=50, default="100+", blank=True)
    participate_stat_2_desc = models.CharField(max_length=255, default="Targeted school outreach", blank=True)

    participate_stat_3_title = models.CharField(max_length=150, default="Registration Target", blank=True)
    participate_stat_3_number = models.CharField(max_length=50, default="5,000", blank=True)
    participate_stat_3_desc = models.CharField(max_length=255, default="Advance visitor registrations", blank=True)

    participate_stat_4_title = models.CharField(max_length=150, default="Digital Campaign Reach", blank=True)
    participate_stat_4_number = models.CharField(max_length=50, default="250,000+", blank=True)
    participate_stat_4_desc = models.CharField(max_length=255, default="Planned cumulative exposure", blank=True)

    # ==========================================
    # EXPERIENCE HIGHLIGHTS SECTION
    # ==========================================
    experience_badge = models.CharField(max_length=100, default="EXPERIENCE THE EXPO", blank=True)
    experience_heading = models.CharField(max_length=255, default="Interactive Expo Experience Zones", blank=True)
    experience_subtitle = models.TextField(default="Navigate cutting-edge experiential stations, counseling hubs, and keynote masterclass stages.", blank=True)
    experience_card_badge = models.CharField(max_length=100, default="EXPO ATMOSPHERE", blank=True)
    experience_card_title = models.CharField(max_length=200, default="Immersive Venue Highlights", blank=True)
    experience_card_desc = models.TextField(default="Step into our immersive physical venue with 60+ university pavilions, AI labs, and live auditorium stages.", blank=True)
    experience_card_btn = models.CharField(max_length=100, default="Explore Expo →", blank=True)
    experience_quote = models.TextField(default="KNOVA gave me the clarity and confidence to choose the right university.", blank=True)
    experience_quote_author = models.CharField(max_length=200, default="Faisal S. — Computer Science at Imperial College London", blank=True)

    # ==========================================
    # FAQ ITEMS & SUPPORT CARD
    # ==========================================
    faq_badge = models.CharField(max_length=100, default="GOT QUESTIONS? WE'VE GOT ANSWERS", blank=True)
    faq_heading_gradient = models.CharField(max_length=200, default="About KNOVA 2027", blank=True)
    faq_desc = models.TextField(default="Everything you need to know about KNOVA 2027.", blank=True)
    faq_support_title = models.CharField(max_length=200, default="Need 1-on-1 Guidance?", blank=True)
    faq_support_desc = models.TextField(default="Have a unique question regarding international visa pathways, degree choices, or VIP keynote seats? Speak with our admissions desk.", blank=True)
    faq_support_btn1 = models.CharField(max_length=100, default="Register for Expo", blank=True)
    faq_support_btn2 = models.CharField(max_length=100, default="About Expo →", blank=True)

    faq_1_q = models.CharField(max_length=255, default="Is entry to the KNOVA 2027 Expo completely free?", blank=True)
    faq_1_a = models.TextField(default="Yes! Admission is 100% free for students, parents, and educators. Simply register online to receive your fast-track digital QR badge.", blank=True)

    faq_2_q = models.CharField(max_length=255, default="What documents should I bring to receive on-spot admissions?", blank=True)
    faq_2_a = models.TextField(default="Bring your latest high school or university transcripts, predicted grades, CV, and English proficiency test scores (IELTS/TOEFL) if available.", blank=True)

    faq_3_q = models.CharField(max_length=255, default="How do I qualify and apply for the $5M+ scholarships?", blank=True)
    faq_3_a = models.TextField(default="Visit the Scholarship & Financial Aid Atrium at the expo. Participating universities conduct on-spot merit assessments and interview eligible candidates.", blank=True)

    faq_4_q = models.CharField(max_length=255, default="Can parents attend with students?", blank=True)
    faq_4_a = models.TextField(default="Absolutely! Parents are warmly invited. Dedicated parent financial advisory sessions and family lounges are available throughout the halls.", blank=True)

    faq_5_q = models.CharField(max_length=255, default="How does the KNOVA Challenge & Student Passport work?", blank=True)
    faq_5_a = models.TextField(default="Open your attendee dashboard, scan QR codes at university booths to complete interactive quests, earn points, and claim exclusive tech prizes and swag bags.", blank=True)

    faq_6_q = models.CharField(max_length=255, default="Where is the event located and what are the opening hours?", blank=True)
    faq_6_a = models.TextField(default="The expo is hosted at the Riyadh Exhibition & Convention Center and Dubai World Trade Centre from 10:00 AM to 7:00 PM daily.", blank=True)

    faq_exh_1_q = models.CharField(max_length=255, default="How can universities and institutions register to exhibit at KNOVA 2027?", blank=True)
    faq_exh_1_a = models.TextField(default="Institutions can register by submitting an official Exhibitor Booking Application via our portal or by contacting our Partnership Desk at partners@knovaexpo.com. Once approved, you gain access to the dedicated Exhibitor Portal to configure booth shell schemes, register staff badges, and book keynote auditorium slots.", blank=True)

    faq_exh_2_q = models.CharField(max_length=255, default="What are the key benefits and ROI of exhibiting at KNOVA 2027?", blank=True)
    faq_exh_2_a = models.TextField(default="Exhibiting provides direct face-to-face access to over 25,000+ pre-screened students, parents, and high school counselors across Riyadh, Dubai, and Doha. Institutions achieve direct enrollments through on-spot credential assessments, award institutional scholarships, expand brand presence across GCC media, and collect high-intent student leads.", blank=True)

    faq_exh_3_q = models.CharField(max_length=255, default="What booth amenities, equipment, and technology assets are included?", blank=True)
    faq_exh_3_a = models.TextField(default="Standard and custom shell schemes include branded fascia boards with your university emblem, premium furniture, electrical supply, high-speed exhibitor Wi-Fi, and unlimited access to the digital QR Attendee Lead Capture Scanner app for all booth representatives.", blank=True)

    faq_exh_4_q = models.CharField(max_length=255, default="Can exhibitors host keynote seminars, masterclasses, or workshop sessions?", blank=True)
    faq_exh_4_a = models.TextField(default="Yes! Premium and Standard exhibitors can reserve dedicated 45-minute speaking sessions in our Keynote Auditoriums and Innovation Theatres. Sessions are promoted across the official timetable, mobile event app, and student push notifications to maximize attendance.", blank=True)

    faq_exh_5_q = models.CharField(max_length=255, default="How does the exhibitor lead capture & QR attendee badge scanning system work?", blank=True)
    faq_exh_5_a = models.TextField(default="Each registered student and parent wears a smart digital QR badge. Booth representatives simply open the Exhibitor Scanner on any smartphone or tablet to scan badges in real-time, instantly capturing student contact info, intended majors, predicted grades, and transcript attachments with export to CSV/Excel.", blank=True)

    # ==========================================
    # FOOTER, CONTACT & SOCIAL LINKS
    # ==========================================
    footer_tagline = models.TextField(default="KNOVA connects universities, academic institutions, students and families through engaging education experiences, meaningful institutional connections and digital opportunities across local, regional and international landscapes.", blank=True)
    footer_copyright = models.CharField(max_length=255, default="© 2027 KNOVA Regional & Global Education Expo. All rights reserved.", blank=True)
    footer_contact_email = models.EmailField(default="connect@knovaexpo.com", blank=True)
    email_partners = models.EmailField(default="partners@knovaexpo.com", blank=True, verbose_name="Exhibitors & Sponsors Email")
    email_speakers = models.EmailField(default="connect@knovaexpo.com", blank=True, verbose_name="Speakers & Keynotes Email")
    email_coordination = models.EmailField(default="coordination@knovaexpo.com", blank=True, verbose_name="Event Coordination Email")
    email_outreach = models.EmailField(default="outreach@knovaexpo.com", blank=True, verbose_name="Institutional Outreach Email")
    footer_contact_phone = models.CharField(max_length=100, default="+966 11 000 0000 / +971 4 000 0000", blank=True)
    chatbot_name = models.CharField(max_length=100, default="Mr. K - Your eBuddy", blank=True, verbose_name="Chat Assistant Name")
    chatbot_username = models.CharField(max_length=100, default="@Mr.K_YourE_Buddy", blank=True, verbose_name="WhatsApp / Chatbot Username")
    whatsapp_number = models.CharField(max_length=50, default="00973 -16171786", blank=True, verbose_name="WhatsApp Support Number")
    footer_address = models.CharField(max_length=255, default="Riyadh Exhibition & Convention Center | Dubai World Trade Centre", blank=True)
    # Social Profile Titles & Links
    social_facebook_title = models.CharField(max_length=100, default="Facebook", blank=True, verbose_name="Facebook Label")
    social_facebook_url = models.URLField(default="https://facebook.com", blank=True)
    social_twitter_title = models.CharField(max_length=100, default="Twitter / X", blank=True, verbose_name="Twitter Label")
    social_twitter_url = models.URLField(default="https://x.com", blank=True)
    social_linkedin_title = models.CharField(max_length=100, default="LinkedIn", blank=True, verbose_name="LinkedIn Label")
    social_linkedin_url = models.URLField(default="https://linkedin.com", blank=True)
    social_instagram_title = models.CharField(max_length=100, default="Instagram", blank=True, verbose_name="Instagram Label")
    social_instagram_url = models.URLField(default="https://instagram.com", blank=True)
    social_youtube_title = models.CharField(max_length=100, default="YouTube", blank=True, verbose_name="YouTube Label")
    social_youtube_url = models.URLField(default="https://youtube.com", blank=True)

    # ==========================================
    # FOOTER NAVIGATION COLUMNS & EDITABLE LINKS
    # ==========================================
    # Column 2 (Explore)
    footer_col2_title = models.CharField(max_length=120, default="Explore", blank=True, verbose_name="Footer Col 2 Title")
    footer_col2_link1_text = models.CharField(max_length=150, default="About KNOVA", blank=True, verbose_name="Col 2 Link 1 Title")
    footer_col2_link1_url = models.CharField(max_length=255, default="/about/", blank=True, verbose_name="Col 2 Link 1 URL")
    footer_col2_link2_text = models.CharField(max_length=150, default="Events & Experiences", blank=True, verbose_name="Col 2 Link 2 Title")
    footer_col2_link2_url = models.CharField(max_length=255, default="/events/", blank=True, verbose_name="Col 2 Link 2 URL")
    footer_col2_link3_text = models.CharField(max_length=150, default="Speakers", blank=True, verbose_name="Col 2 Link 3 Title")
    footer_col2_link3_url = models.CharField(max_length=255, default="", blank=True, verbose_name="Col 2 Link 3 URL")
    footer_col2_link4_text = models.CharField(max_length=150, default="Participating Institutions", blank=True, verbose_name="Col 2 Link 4 Title")
    footer_col2_link4_url = models.CharField(max_length=255, default="", blank=True, verbose_name="Col 2 Link 4 URL")
    footer_col2_link5_text = models.CharField(max_length=150, default="Education Opportunities", blank=True, verbose_name="Col 2 Link 5 Title")
    footer_col2_link5_url = models.CharField(max_length=255, default="", blank=True, verbose_name="Col 2 Link 5 URL")
    footer_col2_link6_text = models.CharField(max_length=150, default="", blank=True, verbose_name="Col 2 Link 6 Title")
    footer_col2_link6_url = models.CharField(max_length=255, default="", blank=True, verbose_name="Col 2 Link 6 URL")

    # Column 3 (Participate)
    footer_col3_title = models.CharField(max_length=120, default="Participate", blank=True, verbose_name="Footer Col 3 Title")
    footer_col3_link1_text = models.CharField(max_length=150, default="Register for Expo", blank=True, verbose_name="Col 3 Link 1 Title")
    footer_col3_link1_url = models.CharField(max_length=255, default="/register/", blank=True, verbose_name="Col 3 Link 1 URL")
    footer_col3_link2_text = models.CharField(max_length=150, default="Institutional Participation", blank=True, verbose_name="Col 3 Link 2 Title")
    footer_col3_link2_url = models.CharField(max_length=255, default="", blank=True, verbose_name="Col 3 Link 2 URL")
    footer_col3_link3_text = models.CharField(max_length=150, default="Become a Speaker", blank=True, verbose_name="Col 3 Link 3 Title")
    footer_col3_link3_url = models.CharField(max_length=255, default="", blank=True, verbose_name="Col 3 Link 3 URL")
    footer_col3_link4_text = models.CharField(max_length=150, default="Become a Sponsor", blank=True, verbose_name="Col 3 Link 4 Title")
    footer_col3_link4_url = models.CharField(max_length=255, default="mailto:partners@knovaexpo.com?subject=Sponsorship%20Inquiry%20-%20KNOVA%202027", blank=True, verbose_name="Col 3 Link 4 URL")
    footer_col3_link5_text = models.CharField(max_length=150, default="", blank=True, verbose_name="Col 3 Link 5 Title")
    footer_col3_link5_url = models.CharField(max_length=255, default="", blank=True, verbose_name="Col 3 Link 5 URL")
    footer_col3_link6_text = models.CharField(max_length=150, default="", blank=True, verbose_name="Col 2 Link 6 Title")
    footer_col3_link6_url = models.CharField(max_length=255, default="", blank=True, verbose_name="Col 3 Link 6 URL")

    # Column 4 (Connect)
    footer_col4_title = models.CharField(max_length=120, default="Connect", blank=True, verbose_name="Footer Col 4 Title")
    footer_col4_link1_text = models.CharField(max_length=150, default="Contact Us", blank=True, verbose_name="Col 4 Link 1 Title")
    footer_col4_link1_url = models.CharField(max_length=255, default="mailto:connect@knovaexpo.com?subject=Contact%20KNOVA%202027", blank=True, verbose_name="Col 4 Link 1 URL")
    footer_col4_link2_text = models.CharField(max_length=150, default="Event Coordination", blank=True, verbose_name="Col 4 Link 2 Title")
    footer_col4_link2_url = models.CharField(max_length=255, default="mailto:coordination@knovaexpo.com?subject=Event%20Coordination%20Inquiry", blank=True, verbose_name="Col 4 Link 2 URL")
    footer_col4_link3_text = models.CharField(max_length=150, default="Institutional Outreach", blank=True, verbose_name="Col 4 Link 3 Title")
    footer_col4_link3_url = models.CharField(max_length=255, default="mailto:outreach@knovaexpo.com?subject=Institutional%20Outreach%20Inquiry", blank=True, verbose_name="Col 4 Link 3 URL")
    footer_col4_link4_text = models.CharField(max_length=150, default="", blank=True, verbose_name="Col 4 Link 4 Title")
    footer_col4_link4_url = models.CharField(max_length=255, default="", blank=True, verbose_name="Col 4 Link 4 URL")
    footer_col4_link5_text = models.CharField(max_length=150, default="", blank=True, verbose_name="Col 4 Link 5 Title")
    footer_col4_link5_url = models.CharField(max_length=255, default="", blank=True, verbose_name="Col 4 Link 5 URL")

    # Column 4 Legal Sub-Links
    footer_legal_title = models.CharField(max_length=120, default="Legal & Compliance", blank=True, verbose_name="Footer Legal Title")
    footer_legal_link1_text = models.CharField(max_length=150, default="Privacy Policy", blank=True, verbose_name="Legal Link 1 Title")
    footer_legal_link1_url = models.CharField(max_length=255, default="/privacy-policy/", blank=True, verbose_name="Legal Link 1 URL")
    footer_legal_link2_text = models.CharField(max_length=150, default="Terms & Conditions", blank=True, verbose_name="Legal Link 2 Title")
    footer_legal_link2_url = models.CharField(max_length=255, default="/terms-conditions/", blank=True, verbose_name="Legal Link 2 URL")
    footer_legal_link3_text = models.CharField(max_length=150, default="", blank=True, verbose_name="Legal Link 3 Title")
    footer_legal_link3_url = models.CharField(max_length=255, default="", blank=True, verbose_name="Legal Link 3 URL")

    # Sponsors Marquee Section Heading & Subtitle
    sponsors_marquee_heading = models.CharField(max_length=255, default="Backed by World-Leading Education Giants", blank=True)
    sponsors_marquee_subtitle = models.TextField(default="Collaborating with premier education funds, testing authorities and international partners.", blank=True)

    # Who Should Attend Strip
    who_attend_heading = models.CharField(max_length=255, default="Who Should Attend?", blank=True)
    who_attend_subtitle = models.TextField(default="KNOVA is designed for all students, parents and education seekers exploring global university pathways, scholarships, and international career credentials.", blank=True)

    # Interactive Floor Map Asset Links
    map_pdf_url = models.CharField(max_length=500, blank=True, default="/static/assets/KNOVA_2027_FLOORPLAN.pdf", help_text="Direct link or path to downloadable floorplan PDF")

    # Automated Database Backup & Email Configuration
    backup_enabled = models.BooleanField(default=True, help_text="Enable or pause automated 5-minute backup email delivery")
    backup_email_recipient = models.TextField(default="arjunaravinda@gmail.com", blank=True, help_text="Destination email address(es) to receive automated database backups")
    backup_frequency_minutes = models.IntegerField(default=5, help_text="Automated backup interval in minutes")
    backup_retention_hours = models.IntegerField(default=24, help_text="Hours to retain backup archives before auto-purging")
    smtp_host = models.CharField(max_length=255, blank=True, default="smtp.gmail.com")
    smtp_port = models.IntegerField(default=587)
    smtp_user = models.CharField(max_length=255, blank=True, default="")
    smtp_password = models.CharField(max_length=255, blank=True, default="")
    smtp_use_tls = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Site Configuration"

    def __str__(self):
        return "Site Configuration"

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

    def get_footer_col2_links(self):
        links = []
        for i in range(1, 7):
            t = (getattr(self, f"footer_col2_link{i}_text", None) or "").strip()
            u = (getattr(self, f"footer_col2_link{i}_url", None) or "").strip()
            if t:
                links.append({"text": t, "url": u})
        return links

    def get_footer_col3_links(self):
        links = []
        for i in range(1, 7):
            t = (getattr(self, f"footer_col3_link{i}_text", None) or "").strip()
            u = (getattr(self, f"footer_col3_link{i}_url", None) or "").strip()
            if t:
                links.append({"text": t, "url": u})
        return links

    def get_footer_col4_links(self):
        links = []
        for i in range(1, 6):
            t = (getattr(self, f"footer_col4_link{i}_text", None) or "").strip()
            u = (getattr(self, f"footer_col4_link{i}_url", None) or "").strip()
            if t:
                links.append({"text": t, "url": u})
        return links

    def get_footer_legal_links(self):
        links = []
        for i in range(1, 4):
            t = (getattr(self, f"footer_legal_link{i}_text", None) or "").strip()
            u = (getattr(self, f"footer_legal_link{i}_url", None) or "").strip()
            if t:
                links.append({"text": t, "url": u})
        return links


# =========================================================
# DYNAMIC WEBSITE CUSTOM SECTIONS (ADD / REMOVE SECTIONS)
# =========================================================
class CustomSection(models.Model):
    name = models.CharField(max_length=150, help_text="Internal label (e.g. Special Announcement Banner)")
    badge = models.CharField(max_length=100, blank=True, default="ANNOUNCEMENT", help_text="Top pill badge")
    title = models.CharField(max_length=255, help_text="Section main title")
    subtitle = models.TextField(blank=True, help_text="Subtitle or description text")
    content_html = models.TextField(blank=True, help_text="Custom HTML or text body")
    bg_color = models.CharField(max_length=50, default="#ffffff", help_text="Background hex color or CSS (e.g. #f8fafc or linear-gradient)")
    text_color = models.CharField(max_length=50, default="#0f172a", help_text="Text hex color (e.g. #0f172a or #ffffff)")
    button_text = models.CharField(max_length=100, blank=True, help_text="Action button label (optional)")
    button_url = models.CharField(max_length=255, blank=True, help_text="Action button destination link")
    placement = models.CharField(
        max_length=50,
        choices=[
            ('after_hero', 'Directly After Hero Banner'),
            ('after_why', 'After Why KNOVA Section'),
            ('after_sponsors', 'After Sponsors Marquee'),
            ('after_events', 'After Events Section'),
            ('after_how', 'After How It Works Section'),
            ('after_exhibitors', 'After Exhibitors Section'),
            ('after_programme', 'After Programme Section'),
            ('after_speakers', 'After Speakers Section'),
            ('after_map', 'After Map Section'),
            ('after_scholarships', 'After Scholarships Section'),
            ('after_experience', 'After Experience Section'),
            ('after_faq', 'After FAQ Section'),
            ('bottom', 'Before Register CTA & Footer'),
        ],
        default='after_why',
        help_text="Where this section appears on the homepage"
    )
    order = models.PositiveIntegerField(default=1, help_text="Display order (lowest number first)")
    is_active = models.BooleanField(default=True, verbose_name="Section Active / Visible")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Custom Section"
        verbose_name_plural = "Custom Sections"

    def __str__(self):
        return self.name or self.title

# ---------------------------------------------------------
# NEW KNOVA 2027 PLATFORM MODELS (PHASE 1-4)
# ---------------------------------------------------------


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    mobile = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True)

    # Contact Details
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country_of_residence = models.CharField(max_length=100, blank=True)

    # Education & Experience
    EDUCATION_LEVEL_CHOICES = [
        ('High School (Grade 9-11)', 'High School (Grade 9-11)'),
        ('High School Senior (Grade 12)', 'High School Senior (Grade 12)'),
        ('High School Graduate', 'High School Graduate'),
        ('Diploma / Vocational', 'Diploma / Vocational'),
        ("Undergraduate (Bachelor's Student)", "Undergraduate (Bachelor's Student)"),
        ("Graduate / Bachelor's Completed", "Graduate / Bachelor's Completed"),
        ("Postgraduate (Master's Student)", "Postgraduate (Master's Student)"),
        ("Master's Degree Completed", "Master's Degree Completed"),
        ('Doctorate / Ph.D.', 'Doctorate / Ph.D.'),
        ('Working Professional', 'Working Professional'),
        ('Other', 'Other'),
    ]
    current_education = models.CharField(max_length=100, blank=True, choices=EDUCATION_LEVEL_CHOICES)
    school_college = models.CharField(max_length=255, blank=True)
    class_year = models.CharField(max_length=50, blank=True)
    grades = models.CharField(max_length=100, blank=True, help_text="e.g., GPA 3.8, 95%, A-Levels")
    work_experience = models.TextField(blank=True, help_text="Briefly describe any relevant work experience or internships.")
    english_proficiency = models.CharField(max_length=50, blank=True, choices=[('IELTS', 'IELTS'), ('TOEFL', 'TOEFL'), ('Duolingo', 'Duolingo'), ('None', 'Not taken yet')])

    qr_identifier = models.CharField(max_length=100, unique=True, blank=True, null=True)

    # AI Matchmaking Preferences
    preferred_country = models.CharField(max_length=100, blank=True, help_text="Comma separated e.g. USA, UK, Canada", db_index=True)
    budget_range = models.CharField(max_length=50, blank=True, choices=[('Low', 'Under $10k'), ('Medium', '$10k-$30k'), ('High', 'Over $30k')])
    preferred_program = models.CharField(max_length=100, blank=True, help_text="e.g. Computer Science, Business")
    preferred_degree = models.CharField(max_length=50, blank=True, choices=[('UG', 'Undergraduate (Bachelor)'), ('PG', 'Postgraduate (Master)'), ('PHD', 'PhD / Doctorate')])
    intake_year = models.CharField(max_length=4, blank=True, help_text="e.g. 2027")

    @property
    def is_profile_complete(self):
        return bool(self.mobile and self.country_of_residence and (self.current_education or self.school_college))

    def save(self, *args, **kwargs):
        if not self.qr_identifier:
            from .models import Registration
            reg = None
            if self.user and self.user.email:
                reg = Registration.objects.filter(email__iexact=self.user.email).first()
            if reg and reg.registration_id and reg.registration_id.startswith('KNOVA-ST-'):
                self.qr_identifier = reg.registration_id
            else:
                from .utils import generate_unique_attendee_id
                self.qr_identifier = generate_unique_attendee_id('Student')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Student: {self.user.get_full_name()}"


class StudentDocument(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255, help_text="e.g. High School Transcript, Passport Copy")
    document = models.FileField(upload_to='student_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} for {self.student.user.get_full_name()}"


class UniversityApplication(models.Model):
    STATUS_CHOICES = [
        ('Shortlisted', 'Shortlisted'),
        ('Applied', 'Applied'),
        ('Interviewing', 'Interviewing'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    university = models.ForeignKey('University', on_delete=models.CASCADE, related_name='student_applications')
    program_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Shortlisted')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.user.get_full_name()} -> {self.university.name} ({self.status})"


class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} at {self.timestamp}"


class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    mobile = models.CharField(max_length=20)
    linked_students = models.ManyToManyField(StudentProfile, blank=True, related_name='parents')
    qr_identifier = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.qr_identifier:
            from .models import Registration
            reg = None
            if self.user and self.user.email:
                reg = Registration.objects.filter(email__iexact=self.user.email).first()
            if reg and reg.registration_id and reg.registration_id.startswith('KNOVA-PA-'):
                self.qr_identifier = reg.registration_id
            else:
                from .utils import generate_unique_attendee_id
                self.qr_identifier = generate_unique_attendee_id('Parent')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Parent: {self.user.get_full_name()}"


class ParentSchedule(models.Model):
    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE, related_name='schedule')
    item_type = models.CharField(max_length=50) # 'University Visit', 'Session'
    related_id = models.IntegerField() # ID of University or ExpoSession
    time = models.DateTimeField()

    def __str__(self):
        return f"Schedule for {self.parent.user.get_full_name()} at {self.time}"


class University(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True)
    is_approved = models.BooleanField(default=True, db_index=True)
    hero_priority = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Hero node priority: 1-10 on main screen, 11-70 on draggable canvas, 0 for not shown in hero nodes."
    )
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['hero_priority', 'name']
        verbose_name_plural = 'Universities'

    @property
    def event_location(self):
        from .models import EventLocation
        return EventLocation.objects.first()

    @property
    def company_name(self):
        return self.name

    @property
    def country(self):
        if hasattr(self, 'profile') and self.profile.location_state_country:
            return self.profile.location_state_country
        return "International"

    @property
    def booth_number(self):
        if hasattr(self, 'booth') and self.booth:
            return self.booth.booth_number
        return "Main Pavilion"

    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        if not self.slug:
            base_slug = slugify(self.name) or 'university'
            slug = base_slug
            counter = 1
            while University.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class UniversityStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='university_staff')
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='staff_members')
    role = models.CharField(max_length=100, default='Representative')

    @property
    def company_name(self):
        return self.university.name if self.university else ''

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.university.name})"


class UniversityProfile(models.Model):
    university = models.OneToOneField(University, on_delete=models.CASCADE, related_name='profile')
    logo = models.ImageField(upload_to='university_logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='university_covers/', blank=True, null=True)
    location_city = models.CharField(max_length=100)
    location_state_country = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    university_type = models.CharField(max_length=100, blank=True) # e.g. Public, Private
    established_year = models.IntegerField(null=True, blank=True)
    accreditation = models.CharField(max_length=255, blank=True)
    short_description = models.TextField()
    about = models.TextField(blank=True)
    campus_facilities = models.TextField(blank=True)
    admission_process = models.TextField(blank=True)

    def __str__(self):
        return f"Profile: {self.university.name}"


class CourseCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Course(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=255)
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    degree_type = models.CharField(max_length=100) # e.g. UG, PG, PhD
    stream = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    mode = models.CharField(max_length=50, choices=[('Full Time', 'Full Time'), ('Part Time', 'Part Time'), ('Online', 'Online')])
    eligibility = models.TextField()
    fees = models.CharField(max_length=100)
    scholarship_available = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.CharField(max_length=50, default='Approved', db_index=True) # Draft, Pending Review, Approved

    def __str__(self):
        return f"{self.name} - {self.university.name}"


class Scholarship(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='scholarships')
    name = models.CharField(max_length=255)
    amount = models.CharField(max_length=100)
    coverage_type = models.CharField(
        max_length=50,
        default='Partial',
        choices=[
            ('Full', 'Full Tuition (100%)'),
            ('Partial', 'Partial Waiver'),
            ('Grant', 'Direct Grant'),
        ],
        db_index=True
    )
    field_of_study = models.CharField(max_length=100, default='All Fields', db_index=True)
    level = models.CharField(
        max_length=50,
        default='All Levels',
        choices=[
            ('Undergraduate', 'Undergraduate (UG)'),
            ('Postgraduate', 'Postgraduate (PG)'),
            ('PhD', 'PhD / Doctoral'),
            ('All Levels', 'All Levels'),
        ],
        db_index=True
    )
    eligibility = models.TextField()
    deadline = models.DateField(null=True, blank=True, db_index=True)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    applicable_courses = models.ManyToManyField(Course, blank=True, related_name='applicable_scholarships')
    status = models.CharField(max_length=50, default='Approved')

    def __str__(self):
        return f"{self.name} - {self.university.name}"


class FloorActivityZone(models.Model):
    name = models.CharField(max_length=150)
    tagline = models.CharField(max_length=255, blank=True)
    hall_location = models.CharField(max_length=100, default='Main Expo Hall')
    badge_label = models.CharField(max_length=100, blank=True)
    icon_class = models.CharField(max_length=50, default='ti ti-compass')
    color_accent = models.CharField(max_length=30, default='#1768ff')
    description = models.TextField()
    activities = models.TextField(help_text="Key activities or highlights separated by newlines")
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_activities_list(self):
        return [a.strip() for a in self.activities.split('\n') if a.strip()]

# ---------------------------------------------------------
# NEW KNOVA 2027 PLATFORM MODELS (PHASE 5-17)
# ---------------------------------------------------------


class StudentInterest(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='interests')
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)


class SavedUniversity(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='saved_universities')
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)


class SavedCourse(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='saved_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)


class SavedScholarship(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='saved_scholarships')
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)


class Enquiry(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='enquiries')
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='enquiries')
    message = models.TextField()
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)


class ExpoBooth(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('ASSIGNED', 'Assigned'),
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive')
    ]
    booth_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    hall = models.CharField(max_length=100, blank=True)
    university = models.OneToOneField(University, on_delete=models.SET_NULL, related_name='booth', null=True, blank=True)
    exhibitor = models.OneToOneField('Exhibitor', on_delete=models.SET_NULL, related_name='booth', null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='AVAILABLE')
    display_info = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    qr_code = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def clean(self):
        pass

    def save(self, *args, **kwargs):
        self.clean()
        if self.university or self.exhibitor:
            if self.status == 'AVAILABLE':
                self.status = 'ASSIGNED'
        else:
            self.status = 'AVAILABLE'

        if not self.qr_code:
            import uuid
            self.qr_code = f"BOOTH-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_assigned_organization(self):
        if self.university and self.exhibitor:
            return f"{self.university.name} / {self.exhibitor.company_name}"
        if self.university:
            return self.university.name
        if self.exhibitor:
            return self.exhibitor.company_name
        return "Unassigned"

    def __str__(self):
        return f"Booth {self.booth_number or self.id} - {self.get_assigned_organization()}"


class BoothInteraction(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='booth_interactions')
    booth = models.ForeignKey(ExpoBooth, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=50, default='Attendance Punched') # 'Scanned QR', 'Direct Interaction', 'Enquiry', 'Attendance Punched'
    status = models.CharField(max_length=50, default='Attended', choices=[('Attended', 'Attended / Checked-in'), ('Interested', 'Interested in Admission'), ('Follow-up', 'Follow-up Scheduled')])
    notes = models.TextField(blank=True)
    interaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-interaction_date']

    def __str__(self):
        return f"{self.student.user.get_full_name() or self.student.user.username} at {self.booth}"


class SeminarStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seminar_staff')
    session = models.ForeignKey(ProgrammeSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_members')
    event_location = models.ForeignKey(EventLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='seminar_staff_members')
    hall_name = models.CharField(max_length=100, default='Hall A', help_text="e.g. Hall A, Keynote Auditorium")
    mobile = models.CharField(max_length=20, blank=True)
    designation = models.CharField(max_length=100, default='Seminar Coordinator')
    raw_password = models.CharField(max_length=100, default='seminar123', blank=True, help_text="Visible coordinator login password")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.hall_name or 'Seminar Coordinator'})"


class SeminarAttendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='seminar_attendances', null=True, blank=True)
    registration = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, related_name='seminar_attendances')
    visitor_name = models.CharField(max_length=255, blank=True)
    session = models.ForeignKey(ProgrammeSession, on_delete=models.CASCADE, related_name='attendances')
    attended_at = models.DateTimeField(auto_now_add=True)
    punch_method = models.CharField(max_length=50, default='QR Scanner', choices=[('QR Scanner', 'QR Scanner'), ('Self Punch', 'Self Punch'), ('Staff Punch', 'Staff Punch')])
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-attended_at']

    def __str__(self):
        name = (self.student.user.get_full_name() or self.student.user.username) if (self.student and self.student.user) else (self.visitor_name or 'Visitor')
        return f"{name} attended {self.session.title}"


class EducationExpert(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='education_expert')
    name = models.CharField(max_length=150, default='Dr. Sarah Jenkins')
    title = models.CharField(max_length=150, default='Senior Academic Counsellor & Global Admissions Expert')
    desk_name = models.CharField(max_length=150, default='Academic Counselling Hub — Desk 1')
    specialization = models.CharField(max_length=200, default='Global Admissions Advisory, Career Counseling, Ivy League & Full Scholarships')
    mobile = models.CharField(max_length=30, blank=True, default='+971 50 123 4567')
    raw_password = models.CharField(max_length=100, default='expert123', blank=True, help_text="Visible expert login password")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.desk_name})"


class ExpertConsultationAttendance(models.Model):
    expert = models.ForeignKey(EducationExpert, on_delete=models.CASCADE, related_name='consultations', null=True, blank=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='expert_consultations', null=True, blank=True)
    registration = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True, related_name='expert_consultations')
    badge_id = models.CharField(max_length=50, blank=True)
    student_name = models.CharField(max_length=255, blank=True)
    attended_at = models.DateTimeField(auto_now_add=True)
    punch_method = models.CharField(max_length=50, default='QR Scanner', choices=[('QR Scanner', 'QR Scanner'), ('Manual Code', 'Manual Code'), ('Direct Link', 'Direct Link')])
    notes = models.CharField(max_length=255, blank=True, default='Official 1-on-1 Academic Advisory & Career Guidance Consultation')

    class Meta:
        ordering = ['-attended_at']

    def __str__(self):
        return f"Consultation: {self.student_name or self.badge_id} on {self.attended_at.strftime('%Y-%m-%d %H:%M')}"


class ExpoEvent(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    venue = models.CharField(max_length=255)
    registration_limit = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


class ExpoSession(models.Model):
    expo = models.ForeignKey(ExpoEvent, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255)
    speaker_name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class StudentSchedule(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='schedule')
    item_type = models.CharField(max_length=50) # 'University Visit', 'Session'
    related_id = models.IntegerField() # ID of University or ExpoSession
    time = models.DateTimeField()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

# ---------------------------------------------------------
# NEW DATA IMPORT MODELS (PHASE 4)
# ---------------------------------------------------------


class DataImportJob(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('COMPLETED_WITH_ERRORS', 'Completed with Errors'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    IMPORT_TYPE_CHOICES = [
        ('UNIVERSITY', 'University'),
        ('COURSE', 'Course'),
        ('SCHOLARSHIP', 'Scholarship')
    ]

    import_type = models.CharField(max_length=50, choices=IMPORT_TYPE_CHOICES)
    uploaded_file = models.FileField(upload_to='imports/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')

    total_rows = models.IntegerField(default=0)
    successful_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    duplicate_rows = models.IntegerField(default=0)

    error_report = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.get_import_type_display()} Import - {self.status}"


class StudentChallengePassport(models.Model):
    badge_id = models.CharField(max_length=100, db_index=True)
    student_name = models.CharField(max_length=200, default='Student Attendee')
    student_email = models.EmailField(blank=True)
    registration = models.ForeignKey('Registration', on_delete=models.SET_NULL, null=True, blank=True, related_name='challenge_passports')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='challenge_passports')

    total_points = models.IntegerField(default=10)
    profile_completed = models.BooleanField(default=True)

    # 6 Core Missions
    universities_visited_count = models.IntegerField(default=0)  # Mission 1 (Target: 3)
    visited_universities = models.JSONField(default=list, blank=True)

    aptitude_test_completed = models.BooleanField(default=False) # Mission 2

    seminars_attended_count = models.IntegerField(default=0)     # Mission 3 (Target: 1)
    attended_seminars = models.JSONField(default=list, blank=True)

    expert_meeting_completed = models.BooleanField(default=False) # Mission 4
    counselling_completed = models.BooleanField(default=False)

    tech_challenge_completed = models.BooleanField(default=False) # Mission 5
    puzzle_completed = models.BooleanField(default=False)         # Mission 6
    passport_completed = models.BooleanField(default=False)       # Full Passport (+100 pts)

    # Rewards Claimed
    claimed_reward_100 = models.BooleanField(default=False) # 100 pts: Seminar priority access
    claimed_reward_150 = models.BooleanField(default=False) # 150 pts: KNOVA merchandise
    claimed_reward_200 = models.BooleanField(default=False) # 200 pts: Special experience/ticket
    claimed_reward_300 = models.BooleanField(default=False) # 300 pts: Premium reward

    activity_log = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-total_points', '-updated_at']
        verbose_name = 'Student Challenge Passport'
        verbose_name_plural = 'Student Challenge Passports'

    def __str__(self):
        return f"{self.student_name} ({self.badge_id}) - {self.total_points} pts"

    def add_activity(self, title, points):
        from django.utils import timezone
        import datetime
        self.total_points += points
        if not isinstance(self.activity_log, list):
            self.activity_log = []
        self.activity_log.insert(0, {
            'title': title,
            'points': points,
            'timestamp': timezone.now().strftime('%b %d, %H:%M')
        })
        self.check_passport_completion()
        self.save()

    def get_latest_completed_exam(self):
        from .models import ExamAttempt
        # 35% mark (is_passed=True) is needed to complete the examination and qualify
        if self.user:
            attempt = ExamAttempt.objects.filter(
                registration__student__user=self.user,
                status='Completed',
                is_passed=True
            ).order_by('-id').first()
            if attempt:
                return attempt
        if self.student_email:
            attempt = ExamAttempt.objects.filter(
                registration__student__user__email__iexact=self.student_email,
                status='Completed',
                is_passed=True
            ).order_by('-id').first()
            if attempt:
                return attempt
        if self.registration and self.registration.email:
            attempt = ExamAttempt.objects.filter(
                registration__student__user__email__iexact=self.registration.email,
                status='Completed',
                is_passed=True
            ).order_by('-id').first()
            if attempt:
                return attempt
        return None

    def sync_exam_challenge_status(self):
        latest_exam = self.get_latest_completed_exam()
        if latest_exam:
            if not self.aptitude_test_completed:
                self.aptitude_test_completed = True
                exam_title = getattr(latest_exam.registration.exam, 'title', 'Online Aptitude Exam')
                score_str = f"Score: {latest_exam.score}" if latest_exam.score is not None else "Completed"
                self.add_activity(f"Completed {exam_title} ({score_str})", 30)
                self.save()
            return True, latest_exam
        else:
            if self.aptitude_test_completed:
                self.aptitude_test_completed = False
                if self.total_points >= 30:
                    self.total_points -= 30
                if isinstance(self.activity_log, list):
                    self.activity_log = [
                        item for item in self.activity_log
                        if not ('Aptitude' in item.get('title', '') or 'Online Exam' in item.get('title', ''))
                    ]
                self.save()
            return False, None

    def sync_attendance_status(self):
        """
        Synchronizes the challenge passport with actual database records:
        1. SeminarAttendance -> Mission 3 (seminars_attended_count, attended_seminars)
        2. BoothInteraction (University booths) -> Mission 1 (universities_visited_count, visited_universities)
        Awards points and logs activity if not already recorded.
        """
        from .models import SeminarAttendance, BoothInteraction, StudentProfile
        changed = False

        # Resolve StudentProfile
        sp = None
        if self.user and hasattr(self.user, 'student_profile'):
            sp = self.user.student_profile
        elif self.student_email:
            sp = StudentProfile.objects.filter(user__email__iexact=self.student_email).first()

        # 1. Sync Seminar Attendance (Mission 3)
        if sp:
            seminar_atts = SeminarAttendance.objects.filter(student=sp).select_related('session')
            actual_count = seminar_atts.count()
            if actual_count == 0 and self.seminars_attended_count > 0:
                self.seminars_attended_count = 0
                self.attended_seminars = []
                changed = True
            elif actual_count > self.seminars_attended_count:
                if not isinstance(self.attended_seminars, list):
                    self.attended_seminars = []
                for att in seminar_atts:
                    sess_title = att.session.title
                    if sess_title not in self.attended_seminars:
                        self.attended_seminars.append(sess_title)
                        self.add_activity(f"Seminar Attended: {sess_title}", 25)
                        changed = True
                self.seminars_attended_count = max(self.seminars_attended_count, len(self.attended_seminars), actual_count)
                changed = True

            # 2. Sync University Booth Visits (Mission 1)
            uni_interactions = BoothInteraction.objects.filter(student=sp, booth__university__isnull=False).select_related('booth__university')
            if uni_interactions.exists():
                if not isinstance(self.visited_universities, list):
                    self.visited_universities = []
                for inter in uni_interactions:
                    uni_name = inter.booth.university.name
                    if uni_name not in self.visited_universities:
                        if not self.is_elite_pass and len(self.visited_universities) >= 3:
                            continue
                        self.visited_universities.append(uni_name)
                        self.add_activity(f"Booth Attendance Punched: {uni_name}", 20)
                        changed = True
                actual_uni_count = len([u for u in self.visited_universities if not u.startswith("Exhibitor:")])
                if actual_uni_count > self.universities_visited_count:
                    self.universities_visited_count = actual_uni_count
                    changed = True

            # 3. Sync Education Expert Consultation (Mission 4)
            from .models import ExpertConsultationAttendance
            expert_punched = ExpertConsultationAttendance.objects.filter(student=sp).exists()
            if not expert_punched and self.badge_id:
                expert_punched = ExpertConsultationAttendance.objects.filter(badge_id__iexact=self.badge_id).exists()
            if expert_punched:
                if not self.expert_meeting_completed:
                    self.expert_meeting_completed = True
                    self.add_activity("Official 1-on-1 Academic Advisory & Career Guidance Consultation (+40 pts)", 40)
                    changed = True

        if changed:
            self.check_passport_completion()
            self.save()
        return changed

    @property
    def is_elite_pass(self):
        """
        True if student has completed all 6 KNOVA Challenge tasks or passport_completed is True.
        Unlocks the Elite Pass and grants unlimited university booth visits.
        """
        if self.passport_completed:
            return True
        return (
            self.universities_visited_count >= 3 and
            self.aptitude_test_completed and
            self.seminars_attended_count >= 1 and
            (self.expert_meeting_completed or self.counselling_completed) and
            self.tech_challenge_completed and
            self.puzzle_completed
        )

    @property
    def can_visit_more_booths(self):
        """
        Partially unlocked students can visit up to 3 booths.
        Elite Pass students can visit unlimited booths.
        """
        if self.is_elite_pass:
            return True
        return self.universities_visited_count < 3

    @property
    def booth_limit_label(self):
        if self.is_elite_pass:
            return "Unlimited (Elite Pass Active)"
        return "3 Booths (Standard Pass Limit)"

    def check_passport_completion(self):
        if not self.passport_completed:
            if (
                self.universities_visited_count >= 3 and
                self.aptitude_test_completed and
                self.seminars_attended_count >= 1 and
                (self.expert_meeting_completed or self.counselling_completed) and
                self.tech_challenge_completed and
                self.puzzle_completed
            ):
                self.passport_completed = True
                self.total_points += 100
                if not isinstance(self.activity_log, list):
                    self.activity_log = []
                self.activity_log.insert(0, {
                    'title': 'Grand Achievement: Full KNOVA Challenge Completed! Elite Pass Unlocked (Unlimited Booth Visits Active)',
                    'points': 100,
                    'timestamp': 'Just now'
                })

    @property
    def completed_missions_count(self):
        count = 0
        if self.universities_visited_count >= 3:
            count += 1
        if self.aptitude_test_completed:
            count += 1
        if self.seminars_attended_count >= 1:
            count += 1
        if self.expert_meeting_completed or self.counselling_completed:
            count += 1
        if self.tech_challenge_completed:
            count += 1
        if self.puzzle_completed:
            count += 1
        return count

    @property
    def rank_title(self):
        if self.is_elite_pass:
            return "Elite Pass"
        elif self.total_points >= 300:
            return "KNOVA Elite Ambassador"
        elif self.total_points >= 200:
            return "Master Explorer"
        elif self.total_points >= 150:
            return "Active Achiever"
        elif self.total_points >= 100:
            return "Rising Scholar"
        return "Novice Attendee"

    @property
    def next_milestone(self):
        if self.total_points < 100:
            return {'points': 100, 'label': 'Seminar Priority Access', 'needed': 100 - self.total_points}
        elif self.total_points < 150:
            return {'points': 150, 'label': 'KNOVA Merchandise', 'needed': 150 - self.total_points}
        elif self.total_points < 200:
            return {'points': 200, 'label': 'Special Experience / VIP Pass', 'needed': 200 - self.total_points}
        elif self.total_points < 300:
            return {'points': 300, 'label': 'Premium Reward', 'needed': 300 - self.total_points}
        return {'points': 300, 'label': 'Max Tier Reached!', 'needed': 0}


class ScholarshipExamSlot(models.Model):
    title = models.CharField(max_length=200, default='KNOVA Global Scholarship Aptitude & Assessment Exam (KG-SAAE)')
    exam_date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=200, default='KNOVA Exam Center — Hall 3, Assessment Arena')
    total_seats = models.PositiveIntegerField(default=50)
    available_seats = models.PositiveIntegerField(default=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['exam_date', 'start_time']

    def __str__(self):
        return f"{self.title} - {self.exam_date} ({self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')})"


class ScholarshipExamBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scholarship_exam_bookings')
    slot = models.ForeignKey(ScholarshipExamSlot, on_delete=models.CASCADE, related_name='bookings')
    scholarship = models.ForeignKey(Scholarship, on_delete=models.SET_NULL, null=True, blank=True, related_name='exam_bookings')
    scholarship_name = models.CharField(max_length=200, blank=True)
    hall_ticket_number = models.CharField(max_length=50, unique=True, db_index=True)
    seat_number = models.CharField(max_length=20)
    status = models.CharField(
        max_length=50,
        default='Confirmed',
        choices=[('Confirmed', 'Confirmed'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')]
    )
    booked_at = models.DateTimeField(auto_now_add=True)
    special_requirements = models.TextField(blank=True)

    class Meta:
        ordering = ['-booked_at']

    def __str__(self):
        return f"{self.user.username} - {self.hall_ticket_number} ({self.slot.exam_date})"

# ---------------------------------------------------------
# ONLINE SCHOLARSHIP EXAM PORTAL MODELS
# ---------------------------------------------------------


class ScholarshipExam(models.Model):
    title = models.CharField(max_length=255)
    scholarship = models.ForeignKey('Scholarship', on_delete=models.CASCADE, related_name='exams', null=True, blank=True)
    exhibitor = models.ForeignKey('Exhibitor', on_delete=models.CASCADE, related_name='conducted_exams', null=True, blank=True)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=60)
    total_marks = models.PositiveIntegerField(default=100)
    passing_marks = models.PositiveIntegerField(default=35, help_text="Minimum passing marks (35% required to complete exam)")
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ExamQuestion(models.Model):
    exam = models.ForeignKey(ScholarshipExam, on_delete=models.CASCADE, related_name='questions')
    section_name = models.CharField(max_length=100, default='General Section')
    text = models.TextField()
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q: {self.text[:50]}"


class QuestionChoice(models.Model):
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class ExamSlot(models.Model):
    exam = models.ForeignKey(ScholarshipExam, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=100)

    def __str__(self):
        return f"{self.date} {self.start_time} - {self.end_time}"

    def is_full(self):
        return self.registrations.count() >= self.capacity


class ExamRegistration(models.Model):
    student = models.ForeignKey('StudentProfile', on_delete=models.CASCADE, related_name='exam_registrations')
    exam = models.ForeignKey(ScholarshipExam, on_delete=models.CASCADE, related_name='registered_students')
    slot = models.ForeignKey(ExamSlot, on_delete=models.SET_NULL, null=True, blank=True, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    is_eligible = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'exam')

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.exam.title}"


class ExamAttempt(models.Model):
    registration = models.ForeignKey(ExamRegistration, on_delete=models.CASCADE, related_name='attempts')
    question_ids = models.TextField(blank=True, default='')  # Stores JSON list or comma-separated list of randomized question IDs
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    is_passed = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=[('In Progress', 'In Progress'), ('Completed', 'Completed'), ('Abandoned', 'Abandoned')], default='In Progress')

    def __str__(self):
        return f"Attempt by {self.registration.student.user.get_full_name()} on {self.registration.exam.title}"


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(QuestionChoice, on_delete=models.SET_NULL, null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer to {self.question.id} in Attempt {self.attempt.id}"


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50) # 'CREATE', 'UPDATE', 'DELETE'
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255)
    object_repr = models.CharField(max_length=255)
    changes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name} at {self.timestamp}"


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, blank=True, help_text="ISO 2 or 3 letter code, e.g. AE, US, GB")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    continent = models.CharField(max_length=50, blank=True, default="Global")
    dial_code = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    is_popular_destination = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        if not self.slug:
            base_slug = slugify(self.name) or 'country'
            slug = base_slug
            counter = 1
            while Country.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# ==========================================
# Signals: Automatic University Card & Placement Creation
# ==========================================
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=University)
def auto_create_university_card(sender, instance, created, **kwargs):
    """
    Whenever a University is added (via admin, dashboard, API or script),
    automatically create its university card (UniversityProfile), assign
    next hero banner card placement, mark as approved, and allocate a booth.
    """
    if kwargs.get('raw', False):
        return

    if created:
        from django.db.models import Max

        # 1. Automatically create UniversityProfile (University Card)
        UniversityProfile.objects.get_or_create(
            university=instance,
            defaults={
                'location_city': 'Global Campus',
                'location_state_country': 'International',
                'university_type': 'Higher Education Institution',
                'accreditation': 'Internationally Accredited Institution',
                'short_description': f"{instance.name} is a premier higher education institution offering globally recognized academic degrees and scholarship opportunities.",
                'about': f"Welcome to {instance.name}. We prepare students for global leadership, research excellence, and high-impact career pathways.",
                'campus_facilities': "Modern lecture theatres, digital research labs, interactive study suites, and student advisory desks.",
                'admission_process': "Direct consultation, portfolio evaluation, and on-spot scholarship assessment available at the university booth."
            }
        )

        # 2. Automatically assign next Hero Priority placement if unset
        updates = {}
        if not instance.hero_priority:
            max_priority = University.objects.exclude(id=instance.id).aggregate(Max('hero_priority'))['hero_priority__max'] or 0
            updates['hero_priority'] = max_priority + 1

        if updates:
            University.objects.filter(pk=instance.pk).update(**updates)

        # 3. Automatically allocate an Expo Booth for this university
        if not hasattr(instance, 'booth') or not instance.booth:
            booth_code = f"Booth U-{instance.id}"
            if not ExpoBooth.objects.filter(booth_number=booth_code).exists():
                ExpoBooth.objects.create(
                    booth_number=booth_code,
                    hall="Main Expo Hall",
                    university=instance,
                    status='ASSIGNED'
                )


@receiver(post_save, sender=ProgrammeSession)
def auto_provision_seminar_coordinator(sender, instance, created, **kwargs):
    """
    Automatically provision a dedicated coordinator User account and SeminarStaff profile
    for each seminar session.
    """
    if kwargs.get('raw', False):
        return
    try:
        from django.contrib.auth.models import User
        from django.utils.text import slugify

        # If already has staff linked to this session, update location/hall
        existing_staff = instance.staff_members.first()
        if existing_staff:
            updated = False
            if instance.event_location and existing_staff.event_location != instance.event_location:
                existing_staff.event_location = instance.event_location
                updated = True
            if instance.hall_name and existing_staff.hall_name != instance.hall_name:
                existing_staff.hall_name = instance.hall_name
                updated = True
            if updated:
                existing_staff.save()
            return

        # Derive clean username slug
        title_slug = slugify(instance.title).replace('-', '_')
        slug_parts = [p for p in title_slug.split('_') if p not in ['the', 'a', 'an', 'in', 'of', 'and', 'for', 'to']]
        keyword = slug_parts[0] if slug_parts else f"hall_{instance.id}"

        base_username = f"seminar_{keyword}"
        username = base_username
        counter = 1
        while User.objects.filter(username__iexact=username).exists():
            u = User.objects.get(username__iexact=username)
            if hasattr(u, 'seminar_staff') and u.seminar_staff.session_id == instance.id:
                return
            if hasattr(u, 'seminar_staff') and u.seminar_staff.session is None:
                u.seminar_staff.session = instance
                u.seminar_staff.event_location = instance.event_location
                u.seminar_staff.hall_name = instance.hall_name or 'Main Auditorium'
                u.seminar_staff.save()
                return
            username = f"{base_username}_{instance.id}" if counter == 1 else f"{base_username}_{counter}"
            counter += 1

        raw_pass = 'seminar123'
        user = User.objects.create_user(
            username=username,
            email=f"{username}@knova.com",
            password=raw_pass,
            first_name=instance.title[:30],
            last_name='Coordinator',
            is_staff=False
        )

        SeminarStaff.objects.create(
            user=user,
            session=instance,
            event_location=instance.event_location,
            hall_name=instance.hall_name or 'Main Auditorium',
            designation=f"Coordinator - {instance.title[:40]}",
            raw_password=raw_pass
        )
    except Exception as e:
        print(f"Error auto-provisioning seminar coordinator: {e}")
