from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from core.models import Municipality


class Command(BaseCommand):
    help = 'Create Django groups for all existing municipalities'

    def handle(self, *args, **options):
        municipalities = Municipality.objects.all()
        created_count = 0
        existing_count = 0

        for municipality in municipalities:
            group_name = f"municipality_{municipality.name.lower().replace(' ', '_').replace('-', '_')}"
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created group: {group_name}')
                )
            else:
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: {created_count} groups created, {existing_count} already existed'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f'Total municipalities: {municipalities.count()}')
        )
