"""
URL configuration for knova_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import index
from core import public_views, dashboard_views

from django.http import HttpResponse

def robots_txt(request):
    from core.models import SiteConfiguration
    config = SiteConfiguration.get_solo()
    if config.robots_txt_content.strip():
        content = config.robots_txt_content
    else:
        domain = config.canonical_base_url.rstrip('/') if config.canonical_base_url else 'https://knovaexpo.com'
        lines = [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            "Disallow: /dashboard/",
            "Disallow: /api/",
            f"Sitemap: {domain}/sitemap.xml",
        ]
        content = "\n".join(lines)
    return HttpResponse(content, content_type="text/plain")   

def sitemap_xml(request):
    from core.models import SiteConfiguration
    config = SiteConfiguration.get_solo()
    domain = config.canonical_base_url.rstrip('/') if config.canonical_base_url else 'https://knovaexpo.com'
    urls = [
        "",
        "/events/",
        "/exhibitors/",
        "/map/",
        "/scholarships/",
        "/speakers/",
        "/programme/",
        "/sponsors/",
        "/about/",
        "/courses/",
    ]
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        xml_lines.append(f'  <url><loc>{domain}{u}</loc><changefreq>weekly</changefreq><priority>{"1.0" if u == "" else "0.8"}</priority></url>')
    xml_lines.append('</urlset>')
    return HttpResponse("\n".join(xml_lines), content_type="application/xml")

urlpatterns = [
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap_xml, name='sitemap_xml'),
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('register/', public_views.public_register, name='public_register'),
    path('events/', public_views.public_events, name='public_events'),
    path('exhibitors/', public_views.public_exhibitors, name='public_exhibitors'),
    path('map/', public_views.public_expo_map, name='public_expo_map'),
    path('scholarships/', public_views.public_scholarships, name='public_scholarships'),
    path('scholarships/exam-booking/', public_views.scholarship_exam_booking, name='scholarship_exam_booking'),
    path('exam/', dashboard_views.dashboard_online_exam_portal, name='root_online_exam_portal'),
    path('exam/portal/', dashboard_views.dashboard_online_exam_portal, name='root_online_exam_portal_direct'),
    path('exam/<int:exam_id>/take/', dashboard_views.dashboard_take_exam, name='root_dashboard_take_exam'),
    path('exam/<int:exam_id>/register/', dashboard_views.dashboard_exam_register, name='root_dashboard_exam_register'),
    path('speakers/', public_views.public_speakers, name='public_speakers'),
    path('programme/', public_views.public_programme, name='public_programme'),
    path('sponsors/', public_views.public_sponsors, name='public_sponsors'),
    path('about/', public_views.public_about, name='public_about'),
    path('university/<slug:slug>/', public_views.university_detail, name='university_detail'),
    path('university/save/<int:pk>/', public_views.save_university, name='save_university'),
    path('university/enquire/<int:pk>/', public_views.university_enquire_callback, name='university_enquire_callback'),
    path('portal/login/', public_views.portal_login, name='portal_login'),
    path('portal/register/', public_views.portal_register, name='portal_register'),
    path('portal/register/student/', public_views.portal_register_student, name='portal_register_student'),
    path('portal/register/parent/', public_views.portal_register_parent, name='portal_register_parent'),
    path('portal/register/exhibitor/', public_views.portal_register_exhibitor, name='portal_register_exhibitor'),
    path('courses/', public_views.courses_list, name='courses_list'),
    path('register/success/<int:pk>/', public_views.register_success, name='register_success'),
    path('register/success/<int:reg_pk>/connect/', public_views.connect_family, name='connect_family'),
    path('game/', public_views.game_puzzle, name='game_puzzle'),
    path('challenge/', public_views.knova_challenge, name='knova_challenge'),
    path('my-expo/', public_views.my_expo_hub, name='my_expo'),
    path('api/challenge/action/', public_views.challenge_action_api, name='challenge_action_api'),

    path('register/badge/<int:pk>/', public_views.digital_badge, name='digital_badge'),
    path('chat/lead/', public_views.capture_chat_lead, name='capture_chat_lead'),
    path('api/check-in/', public_views.check_in_api, name='check_in_api'),
    path('api/scan-booth/', public_views.scan_booth_api, name='scan_booth_api'),
    path('api/search/', public_views.global_search, name='global_search'),
    path('privacy-policy/', public_views.privacy_policy, name='privacy_policy'),
    path('terms/', public_views.terms_conditions, name='terms_conditions'),
    path('logout/', dashboard_views.dashboard_logout_view, name='root_logout'),
    path('dashboard/', include('core.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
