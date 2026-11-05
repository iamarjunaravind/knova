from django.contrib import admin
from .models import (
    Country,
    EventLocation, Exhibitor, Sponsor, Speaker, ProgrammeSession, Registration,
    University, UniversityProfile, CourseCategory, Course, Scholarship,
    StudentProfile, ParentProfile, UniversityStaff, SiteConfiguration, CustomSection, FloorActivityZone,
    StudentChallengePassport, ExpoBooth, BoothInteraction, SeminarStaff, SeminarAttendance,
    ChatbotFAQ, ChatLead
)


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    fieldsets = (
        ("SEO & Meta", {
            "fields": ("meta_title", "meta_description")
        }),
        ("Section Visibility Toggles (Homepage)", {
            "fields": (
                "show_hero_section", "show_stats_bar", "show_why_section",
                "show_sponsors_marquee", "show_events_section", "show_how_section",
                "show_exhibitors_section", "show_programme_section", "show_speakers_section",
                "show_map_section", "show_scholarships_section", "show_experience_section",
                "show_faq_section", "show_register_cta_section"
            )
        }),
        ("Navigation Bar Links Visibility", {
            "fields": (
                "show_nav_home", "show_nav_about", "show_nav_programs",
                "show_nav_events", "show_nav_exhibitors", "show_nav_scholarships",
                "show_nav_sponsors", "show_nav_challenge", "show_nav_my_expo"
            )
        }),
        ("Homepage Hero Content", {
            "fields": (
                "hero_badge_text", "hero_badge_subtext", "hero_title_line1",
                "hero_title_line2", "hero_subtitle", "hero_primary_btn_text",
                "hero_primary_btn_url", "hero_secondary_btn_text", "hero_secondary_btn_url",
                "hero_search_placeholder", "hero_image"
            )
        }),
        ("Homepage Stats Bar", {
            "fields": (
                ("stat_1_number", "stat_1_label"),
                ("stat_2_number", "stat_2_label"),
                ("stat_3_number", "stat_3_label"),
                ("stat_4_number", "stat_4_label"),
            )
        }),
        ("Homepage Why KNOVA Section", {
            "fields": ("why_badge", "why_title", "why_title_gradient", "why_text", "why_image")
        }),
        ("Homepage Section Headings", {
            "fields": (
                ("events_heading", "events_subtitle"),
                ("exhibitors_heading", "exhibitors_subtitle"),
                ("speakers_heading", "speakers_subtitle"),
                ("programme_heading", "programme_subtitle"),
                ("scholarships_heading", "scholarships_subtitle"),
                ("map_heading", "map_subtitle"),
                ("faq_heading", "faq_subtitle"),
                ("cta_heading", "cta_subtitle", "cta_btn_text"),
            )
        }),
        ("Services: About Page Content", {
            "fields": ("about_title", "about_subtitle", "about_mission", "about_vision", "about_history")
        }),
        ("Services: Events Page Content", {
            "fields": ("events_page_title", "events_page_subtitle", "events_page_notice")
        }),
        ("Services: Exhibitors Page Content", {
            "fields": ("exhibitors_page_title", "exhibitors_page_subtitle")
        }),
        ("Services: Scholarships Page Content", {
            "fields": ("scholarships_page_title", "scholarships_page_subtitle", "scholarships_page_intro")
        }),
        ("Services: Speakers Page Content", {
            "fields": ("speakers_page_title", "speakers_page_subtitle")
        }),
        ("Services: Programme Page Content", {
            "fields": ("programme_page_title", "programme_page_subtitle")
        }),
        ("Services: Sponsors Page Content", {
            "fields": ("sponsors_page_title", "sponsors_page_subtitle")
        }),
        ("Services: Floor Map Page Content", {
            "fields": ("map_page_title", "map_page_subtitle")
        }),
        ("Services: Courses Page Content", {
            "fields": ("courses_page_title", "courses_page_subtitle")
        }),
        ("Services: Challenge Page Content", {
            "fields": ("challenge_page_title", "challenge_page_subtitle")
        }),
    )


class UniversityProfileInline(admin.StackedInline):
    model = UniversityProfile
    can_delete = False
    extra = 0


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'hero_priority', 'is_approved', 'registration_date')
    list_editable = ('hero_priority', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('name',)
    ordering = ('hero_priority', 'name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [UniversityProfileInline]


@admin.register(UniversityProfile)
class UniversityProfileAdmin(admin.ModelAdmin):
    list_display = ('university', 'location_city')
    search_fields = ('university__name', 'location_city')


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'degree_type', 'mode', 'status')
    list_filter = ('degree_type', 'mode', 'status')
    search_fields = ('name', 'university__name')


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'amount', 'coverage_type', 'field_of_study', 'level', 'deadline', 'status')
    list_filter = ('coverage_type', 'field_of_study', 'level', 'status')
    search_fields = ('name', 'university__name', 'description')


@admin.register(FloorActivityZone)
class FloorActivityZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'hall_location', 'badge_label', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'description', 'activities')


@admin.register(EventLocation)
class EventLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'start_date', 'is_upcoming', 'is_completed', 'is_active')
    list_filter = ('is_upcoming', 'is_completed', 'is_active')
    search_fields = ('name', 'city')


@admin.register(Exhibitor)
class ExhibitorAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'event_location')
    list_filter = ('event_location',)
    search_fields = ('company_name',)


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'event_location')
    list_filter = ('category', 'event_location')
    search_fields = ('name',)


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'organization')
    search_fields = ('name', 'organization')


@admin.register(ProgrammeSession)
class ProgrammeSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'start_time', 'event_location', 'speaker')
    list_filter = ('event_location', 'date')
    search_fields = ('title',)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'role', 'event_location', 'status', 'registered_at')
    list_filter = ('role', 'status', 'event_location')
    search_fields = ('full_name', 'email')
    readonly_fields = ('registered_at',)


@admin.register(StudentChallengePassport)
class StudentChallengePassportAdmin(admin.ModelAdmin):
    list_display = ('badge_id', 'student_name', 'student_email', 'total_points', 'universities_visited_count', 'aptitude_test_completed', 'seminars_attended_count', 'expert_meeting_completed', 'tech_challenge_completed', 'puzzle_completed', 'passport_completed')
    list_filter = ('passport_completed', 'aptitude_test_completed', 'tech_challenge_completed', 'puzzle_completed')
    search_fields = ('badge_id', 'student_name', 'student_email')


@admin.register(ExpoBooth)
class ExpoBoothAdmin(admin.ModelAdmin):
    list_display = ('booth_number', 'hall', 'status', 'university', 'exhibitor', 'qr_code')
    search_fields = ('booth_number', 'university__name', 'exhibitor__company_name', 'qr_code')


@admin.register(BoothInteraction)
class BoothInteractionAdmin(admin.ModelAdmin):
    list_display = ('student', 'booth', 'interaction_type', 'status', 'interaction_date')
    list_filter = ('interaction_type', 'status', 'interaction_date')
    search_fields = ('student__user__username', 'student__user__email', 'booth__booth_number', 'booth__university__name')


@admin.register(SeminarStaff)
class SeminarStaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'hall_name', 'designation', 'mobile', 'created_at')
    search_fields = ('user__username', 'user__email', 'hall_name', 'designation')


@admin.register(SeminarAttendance)
class SeminarAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'punch_method', 'attended_at')
    list_filter = ('punch_method', 'attended_at')
    search_fields = ('student__user__username', 'student__user__email', 'session__title')


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'continent', 'dial_code', 'is_popular_destination', 'is_active', 'order')
    list_editable = ('is_popular_destination', 'is_active', 'order')
    list_filter = ('continent', 'is_active', 'is_popular_destination')
    search_fields = ('name', 'code', 'continent')
    ordering = ('order', 'name')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CustomSection)
class CustomSectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'placement', 'order', 'is_active', 'updated_at')
    list_editable = ('order', 'is_active', 'placement')
    list_filter = ('is_active', 'placement')
    search_fields = ('name', 'title', 'subtitle', 'content_html')


@admin.register(ChatbotFAQ)
class ChatbotFAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'chip_label', 'order', 'is_chip', 'is_active', 'updated_at')
    list_editable = ('order', 'is_chip', 'is_active')
    list_filter = ('is_active', 'is_chip')
    search_fields = ('question', 'chip_label', 'keywords', 'answer')
    ordering = ('order', 'id')


@admin.register(ChatLead)
class ChatLeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'captured_at')
    search_fields = ('name', 'email')
    ordering = ('-captured_at',)
