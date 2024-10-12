from django.core.management.base import BaseCommand
from crmapp.models import Material
import csv

class Command(BaseCommand):
    help = 'Load dummy materials from a CSV file'

    def handle(self, *args, **options):
        file_path = '/home/ubuntu/crmsamnan/crm/crmapp/management/commands/dummy_materials.csv'  # Update the path
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            materials_created = 0
            for row in reader:
                material, created = Material.objects.get_or_create(
                    code=row['code'],
                    defaults={
                        'description': row['description'],
                        'quantity': int(row['quantity']),
                    }
                )
                if created:
                    materials_created += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {materials_created} materials.'))
