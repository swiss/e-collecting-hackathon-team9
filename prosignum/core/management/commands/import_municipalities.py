import csv
from django.core.management.base import BaseCommand
from core.models import Municipality


class Command(BaseCommand):
    help = 'Import municipalities from CSV file (AMTOVZ format)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        self.stdout.write(f'Importing municipalities from {csv_file}...')

        created = 0
        updated = 0
        errors = 0

        # Track unique municipalities by BFS number
        municipalities_data = {}

        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')

                for row in reader:
                    try:
                        bfs_number = int(row['BFS-Nr'])
                        gemeindename = row['Gemeindename'].strip()
                        canton = row['Kantonskürzel'].strip()
                        postal_code = row['PLZ'].strip()

                        # Use first occurrence of each BFS number
                        if bfs_number not in municipalities_data:
                            municipalities_data[bfs_number] = {
                                'name': gemeindename,
                                'canton': canton,
                                'postal_code': postal_code
                            }

                    except (KeyError, ValueError) as e:
                        errors += 1
                        self.stdout.write(self.style.WARNING(f'Error parsing row: {e}'))
                        continue

            # Now create or update municipalities
            for bfs_number, data in municipalities_data.items():
                municipality, created_flag = Municipality.objects.update_or_create(
                    bfs_number=bfs_number,
                    defaults={
                        'name': data['name'],
                        'canton': data['canton'],
                        'postal_code': data['postal_code']
                    }
                )

                if created_flag:
                    created += 1
                else:
                    updated += 1

            self.stdout.write(self.style.SUCCESS(
                f'\nImport complete!\n'
                f'  Created: {created}\n'
                f'  Updated: {updated}\n'
                f'  Errors: {errors}\n'
                f'  Total unique municipalities: {len(municipalities_data)}'
            ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
