import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knova_backend.settings')
django.setup()

from core.models import University, UniversityProfile
from django.utils.text import slugify

unis = [
    ('Harvard University', 'USA', 'dubai.webp'), ('Oxford University', 'UK', 'riyadh.webp'),
    ('MIT', 'USA', 'doha.webp'), ('Stanford University', 'USA', 'dubai.webp'),
    ('Cambridge Univ.', 'UK', 'riyadh.webp'), ('ETH Zurich', 'Switzerland', 'doha.webp'),
    ('University of Toronto', 'Canada', 'dubai.webp'), ('National Univ of SG', 'Singapore', 'riyadh.webp'),
    ('Imperial College', 'UK', 'doha.webp'), ('Univ College London', 'UK', 'dubai.webp'),
    ('University of Tokyo', 'Japan', 'riyadh.webp'), ('Tsinghua University', 'China', 'doha.webp'),
    ('Sorbonne University', 'France', 'dubai.webp'), ('LMU Munich', 'Germany', 'riyadh.webp'),
    ('Melbourne University', 'Australia', 'doha.webp'), ('Sydney University', 'Australia', 'dubai.webp'),
    ('IIT Bombay', 'India', 'riyadh.webp'), ('Seoul National Univ', 'South Korea', 'doha.webp'),
    ('Cornell University', 'USA', 'dubai.webp'), ('Yale University', 'USA', 'riyadh.webp'),
    ('Princeton Univ', 'USA', 'doha.webp'), ('Peking University', 'China', 'dubai.webp'),
    ('Kyoto University', 'Japan', 'riyadh.webp'), ('King\'s College', 'UK', 'doha.webp'),
    ('McGill University', 'Canada', 'dubai.webp'),
    ('Columbia University', 'USA', 'riyadh.webp'), ('UCLA', 'USA', 'doha.webp'),
    ('Univ of Chicago', 'USA', 'dubai.webp'), ('NYU', 'USA', 'riyadh.webp'),
    ('Univ of Pennsylvania', 'USA', 'doha.webp'), ('Johns Hopkins Univ', 'USA', 'dubai.webp'),
    ('Univ of Michigan', 'USA', 'riyadh.webp'), ('UC Berkeley', 'USA', 'doha.webp'),
    ('Northwestern Univ', 'USA', 'dubai.webp'), ('Duke University', 'USA', 'riyadh.webp'),
    ('Univ of Washington', 'USA', 'doha.webp'), ('Univ of Edinburgh', 'UK', 'dubai.webp'),
    ('Univ of Manchester', 'UK', 'riyadh.webp'), ('Univ of Bristol', 'UK', 'doha.webp'),
    ('Univ of Amsterdam', 'Netherlands', 'dubai.webp'), ('KU Leuven', 'Belgium', 'riyadh.webp'),
    ('Univ of Copenhagen', 'Denmark', 'doha.webp'), ('Karolinska Institute', 'Sweden', 'dubai.webp'),
    ('Univ of Hong Kong', 'Hong Kong', 'riyadh.webp'), ('Nanyang Tech Univ', 'Singapore', 'doha.webp'),
    ('Fudan University', 'China', 'dubai.webp'), ('Shanghai Jiao Tong', 'China', 'riyadh.webp'),
    ('Univ of British Columbia', 'Canada', 'doha.webp'), ('Univ of Sydney', 'Australia', 'dubai.webp'),
    ('Monash University', 'Australia', 'riyadh.webp')
]

for name, loc, img in unis:
    slug = slugify(name)
    # Ensure unique slug
    base_slug = slug
    counter = 1
    while University.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
        
    u = University.objects.create(name=name, slug=slug, is_approved=True)
    UniversityProfile.objects.create(
        university=u,
        location_city=loc,
        location_state_country=loc,
        short_description=f"A leading institution in {loc}."
    )
    
print("Successfully seeded database with 50 universities!")
