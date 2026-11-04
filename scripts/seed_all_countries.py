import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knova_backend.settings')
django.setup()

from core.models import Country

COUNTRIES = [
    # North America
    ("United States", "US", "North America", "+1", True, 1),
    ("Canada", "CA", "North America", "+1", True, 2),
    ("Mexico", "MX", "North America", "+52", False, 10),
    ("Costa Rica", "CR", "North America", "+506", False, 20),
    ("Cuba", "CU", "North America", "+53", False, 20),
    ("Dominican Republic", "DO", "North America", "+1", False, 20),
    ("Guatemala", "GT", "North America", "+502", False, 20),
    ("Haiti", "HT", "North America", "+509", False, 20),
    ("Honduras", "HN", "North America", "+504", False, 20),
    ("Jamaica", "JM", "North America", "+1", False, 20),
    ("Nicaragua", "NI", "North America", "+505", False, 20),
    ("Panama", "PA", "North America", "+507", False, 20),
    ("El Salvador", "SV", "North America", "+503", False, 20),
    ("Bahamas", "BS", "North America", "+1", False, 20),
    ("Barbados", "BB", "North America", "+1", False, 20),
    ("Trinidad and Tobago", "TT", "North America", "+1", False, 20),

    # Europe
    ("United Kingdom", "GB", "Europe", "+44", True, 3),
    ("Germany", "DE", "Europe", "+49", True, 4),
    ("France", "FR", "Europe", "+33", True, 5),
    ("Ireland", "IE", "Europe", "+353", True, 6),
    ("Netherlands", "NL", "Europe", "+31", True, 7),
    ("Switzerland", "CH", "Europe", "+41", True, 8),
    ("Sweden", "SE", "Europe", "+46", True, 9),
    ("Italy", "IT", "Europe", "+39", True, 11),
    ("Spain", "ES", "Europe", "+34", True, 12),
    ("Austria", "AT", "Europe", "+43", False, 15),
    ("Belgium", "BE", "Europe", "+32", False, 15),
    ("Denmark", "DK", "Europe", "+45", False, 15),
    ("Finland", "FI", "Europe", "+358", False, 15),
    ("Norway", "NO", "Europe", "+47", False, 15),
    ("Poland", "PL", "Europe", "+48", False, 15),
    ("Portugal", "PT", "Europe", "+351", False, 15),
    ("Czech Republic", "CZ", "Europe", "+420", False, 20),
    ("Greece", "GR", "Europe", "+30", False, 20),
    ("Hungary", "HU", "Europe", "+36", False, 20),
    ("Romania", "RO", "Europe", "+40", False, 20),
    ("Bulgaria", "BG", "Europe", "+359", False, 20),
    ("Croatia", "HR", "Europe", "+385", False, 20),
    ("Cyprus", "CY", "Europe", "+357", False, 20),
    ("Estonia", "EE", "Europe", "+372", False, 20),
    ("Iceland", "IS", "Europe", "+354", False, 20),
    ("Latvia", "LV", "Europe", "+371", False, 20),
    ("Lithuania", "LT", "Europe", "+370", False, 20),
    ("Luxembourg", "LU", "Europe", "+352", False, 20),
    ("Malta", "MT", "Europe", "+356", False, 20),
    ("Slovakia", "SK", "Europe", "+421", False, 20),
    ("Slovenia", "SI", "Europe", "+386", False, 20),
    ("Albania", "AL", "Europe", "+355", False, 25),
    ("Bosnia and Herzegovina", "BA", "Europe", "+387", False, 25),
    ("Georgia", "GE", "Europe", "+995", False, 25),
    ("Moldova", "MD", "Europe", "+373", False, 25),
    ("Montenegro", "ME", "Europe", "+382", False, 25),
    ("North Macedonia", "MK", "Europe", "+389", False, 25),
    ("Serbia", "RS", "Europe", "+381", False, 25),
    ("Ukraine", "UA", "Europe", "+380", False, 25),

    # Middle East & Gulf (GCC)
    ("United Arab Emirates", "AE", "Middle East", "+971", True, 1),
    ("Saudi Arabia", "SA", "Middle East", "+966", True, 10),
    ("Qatar", "QA", "Middle East", "+974", True, 12),
    ("Oman", "OM", "Middle East", "+968", False, 15),
    ("Bahrain", "BH", "Middle East", "+973", False, 15),
    ("Kuwait", "KW", "Middle East", "+965", False, 15),
    ("Jordan", "JO", "Middle East", "+962", False, 20),
    ("Lebanon", "LB", "Middle East", "+961", False, 20),
    ("Turkey", "TR", "Middle East", "+90", True, 16),
    ("Israel", "IL", "Middle East", "+972", False, 20),
    ("Iraq", "IQ", "Middle East", "+964", False, 25),
    ("Yemen", "YE", "Middle East", "+967", False, 30),

    # Asia & Pacific
    ("India", "IN", "Asia", "+91", True, 3),
    ("Australia", "AU", "Oceania", "+61", True, 4),
    ("Singapore", "SG", "Asia", "+65", True, 5),
    ("New Zealand", "NZ", "Oceania", "+64", True, 8),
    ("Japan", "JP", "Asia", "+81", True, 9),
    ("South Korea", "KR", "Asia", "+82", True, 10),
    ("Malaysia", "MY", "Asia", "+60", True, 11),
    ("China", "CN", "Asia", "+86", True, 12),
    ("Hong Kong", "HK", "Asia", "+852", True, 13),
    ("Taiwan", "TW", "Asia", "+886", False, 18),
    ("Indonesia", "ID", "Asia", "+62", False, 20),
    ("Thailand", "TH", "Asia", "+66", False, 20),
    ("Vietnam", "VN", "Asia", "+84", False, 20),
    ("Philippines", "PH", "Asia", "+63", False, 20),
    ("Pakistan", "PK", "Asia", "+92", False, 20),
    ("Bangladesh", "BD", "Asia", "+880", False, 20),
    ("Sri Lanka", "LK", "Asia", "+94", False, 20),
    ("Nepal", "NP", "Asia", "+977", False, 25),
    ("Kazakhstan", "KZ", "Asia", "+7", False, 25),
    ("Uzbekistan", "UZ", "Asia", "+998", False, 25),
    ("Azerbaijan", "AZ", "Asia", "+994", False, 25),
    ("Armenia", "AM", "Asia", "+374", False, 25),
    ("Cambodia", "KH", "Asia", "+855", False, 30),
    ("Maldives", "MV", "Asia", "+960", False, 30),
    ("Mongolia", "MN", "Asia", "+976", False, 30),
    ("Myanmar", "MM", "Asia", "+95", False, 30),
    ("Brunei", "BN", "Asia", "+673", False, 30),
    ("Fiji", "FJ", "Oceania", "+679", False, 30),
    ("Papua New Guinea", "PG", "Oceania", "+675", False, 30),

    # Africa
    ("South Africa", "ZA", "Africa", "+27", True, 15),
    ("Egypt", "EG", "Africa", "+20", True, 18),
    ("Nigeria", "NG", "Africa", "+234", False, 20),
    ("Kenya", "KE", "Africa", "+254", False, 20),
    ("Morocco", "MA", "Africa", "+212", False, 20),
    ("Ghana", "GH", "Africa", "+233", False, 20),
    ("Ethiopia", "ET", "Africa", "+251", False, 25),
    ("Tanzania", "TZ", "Africa", "+255", False, 25),
    ("Uganda", "UG", "Africa", "+256", False, 25),
    ("Algeria", "DZ", "Africa", "+213", False, 25),
    ("Tunisia", "TN", "Africa", "+216", False, 25),
    ("Rwanda", "RW", "Africa", "+250", False, 25),
    ("Mauritius", "MU", "Africa", "+230", False, 25),
    ("Senegal", "SN", "Africa", "+221", False, 30),
    ("Zambia", "ZM", "Africa", "+260", False, 30),
    ("Zimbabwe", "ZW", "Africa", "+263", False, 30),
    ("Botswana", "BW", "Africa", "+267", False, 30),
    ("Namibia", "NA", "Africa", "+264", False, 30),
    ("Ivory Coast", "CI", "Africa", "+225", False, 30),
    ("Cameroon", "CM", "Africa", "+237", False, 30),
    ("Angola", "AO", "Africa", "+244", False, 30),
    ("Mozambique", "MZ", "Africa", "+258", False, 30),
    ("Sudan", "SD", "Africa", "+249", False, 35),
    ("Libya", "LY", "Africa", "+218", False, 35),

    # South America
    ("Brazil", "BR", "South America", "+55", True, 15),
    ("Argentina", "AR", "South America", "+54", False, 20),
    ("Chile", "CL", "South America", "+56", False, 20),
    ("Colombia", "CO", "South America", "+57", False, 20),
    ("Peru", "PE", "South America", "+51", False, 20),
    ("Uruguay", "UY", "South America", "+598", False, 25),
    ("Ecuador", "EC", "South America", "+593", False, 25),
    ("Paraguay", "PY", "South America", "+595", False, 25),
    ("Bolivia", "BO", "South America", "+591", False, 25),
    ("Venezuela", "VE", "South America", "+58", False, 30),
    ("Guyana", "GY", "South America", "+592", False, 30),
    ("Suriname", "SR", "South America", "+597", False, 30),
]

def seed_countries():
    print(f"Seeding {len(COUNTRIES)} countries into the database...")
    created_count = 0
    updated_count = 0
    for name, code, continent, dial_code, is_pop, order in COUNTRIES:
        country, created = Country.objects.get_or_create(
            name=name,
            defaults={
                'code': code,
                'continent': continent,
                'dial_code': dial_code,
                'is_popular_destination': is_pop,
                'order': order,
                'is_active': True
            }
        )
        if created:
            created_count += 1
        else:
            country.code = code
            country.continent = continent
            country.dial_code = dial_code
            country.is_popular_destination = is_pop
            country.order = order
            country.is_active = True
            country.save()
            updated_count += 1

    total = Country.objects.count()
    print(f"Country seeding complete! Created: {created_count}, Updated: {updated_count}, Total in DB: {total}")

if __name__ == '__main__':
    seed_countries()

