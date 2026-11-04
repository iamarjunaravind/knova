import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knova_backend.settings')
django.setup()

from core.models import University, UniversityProfile
from django.utils.text import slugify

images = ['dubai.webp', 'riyadh.webp', 'doha.webp']
countries = ['USA', 'UK', 'Australia', 'Canada', 'Germany', 'France', 'Japan', 'China', 'India', 'South Korea']

# Create 100 dummy universities
for i in range(1, 101):
    name = f'Global University {i}'
    loc = random.choice(countries)
    img = random.choice(images)
    
    slug = slugify(name)
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
        short_description=f"A leading institution in {loc}.",
        logo=f"assets/{img}"  # Just referencing a dummy image
    )

print("Successfully seeded 100 more universities!")
