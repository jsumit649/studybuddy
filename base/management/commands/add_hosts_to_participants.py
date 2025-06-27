from django.core.management.base import BaseCommand
from base.models import Room

class Command(BaseCommand):
    help = 'Add each room host as a participant if not already'

    def handle(self, *args, **kwargs):
        updated = 0
        for room in Room.objects.all():
            if room.host and room.host not in room.participants.all():
                room.participants.add(room.host)
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} rooms.'))
