from django.core.management.base import BaseCommand
from core.models import ExpoBooth, University, Exhibitor, allocate_booth_for_university

class Command(BaseCommand):
    help = "Idempotently sync official architectural 56 ExpoBooth records and allocate them to active universities."

    def handle(self, *args, **options):
        self.stdout.write("Starting synchronization of official venue floor plan booths...")

        # 1. Define all 56 official architectural booths
        official_booths = []

        # A-01: Flagship Pavilion
        official_booths.append(('Booth A-01', 'Hall 1 Main Concourse', 'Flagship University Pavilion (400x600 cm)'))

        # B-01 to B-06: Premium Island Booths
        for i in range(1, 7):
            official_booths.append((f'Booth B-{i:02d}', 'Hall 1 Main Concourse', 'Premium Island Booth (600x300 cm)'))

        # C-01 to C-24: Standard University Booths
        for i in range(1, 25):
            official_booths.append((f'Booth C-{i:02d}', 'Hall 1 Main Concourse', 'Standard University Booth (300x300 cm)'))

        # D-01 to D-20: Shell Scheme Booths
        for i in range(1, 21):
            official_booths.append((f'Booth D-{i:02d}', 'Hall 1 Main Concourse', 'Shell Scheme Booth (250x250 cm)'))

        # S-01 to S-05: Sponsor Pavilions
        for i in range(1, 6):
            official_booths.append((f'Booth S-{i:02d}', 'Hall 1 Main Concourse', 'Sponsor Pavilion (450x200 cm)'))

        # 2. Ensure each official booth exists in the database
        for b_num, hall, info in official_booths:
            booth, created = ExpoBooth.objects.get_or_create(
                booth_number=b_num,
                defaults={
                    'hall': hall,
                    'display_info': info,
                    'status': 'AVAILABLE',
                    'is_active': True,
                }
            )
            if not created:
                booth.hall = hall
                booth.display_info = info
                booth.is_active = True
                booth.save()

        self.stdout.write(self.style.SUCCESS(f"Verified all {len(official_booths)} official booths exist."))

        # 3. Clean up obsolete mock booths (e.g. U-181..U-351)
        official_numbers = [b[0] for b in official_booths]
        obsolete_booths = ExpoBooth.objects.exclude(booth_number__in=official_numbers)

        # First, if any university is currently attached to an obsolete booth, reallocate it
        for obs in obsolete_booths:
            if obs.university:
                uni = obs.university
                obs.university = None
                obs.exhibitor = None
                obs.save()
                allocate_booth_for_university(uni)
                self.stdout.write(f"Reallocated university '{uni.name}' to official booth.")

        deleted_count, _ = obsolete_booths.filter(university__isnull=True, exhibitor__isnull=True).delete()
        self.stdout.write(self.style.SUCCESS(f"Cleaned up {deleted_count} obsolete placeholder booths."))

        # 4. Allocate official booths to any universities without a booth
        for uni in University.objects.all().order_by('id'):
            if not hasattr(uni, 'booth') or not uni.booth:
                b = allocate_booth_for_university(uni)
                if b:
                    self.stdout.write(self.style.SUCCESS(f"Allocated {b.booth_number} to {uni.name}"))

        total_official = ExpoBooth.objects.count()
        assigned = ExpoBooth.objects.filter(university__isnull=False).count()
        available = ExpoBooth.objects.filter(status='AVAILABLE').count()
        self.stdout.write(self.style.SUCCESS(f"Sync complete! Total official booths: {total_official} ({assigned} assigned, {available} available)."))
