from django.core.management.base import BaseCommand

from users.models import Registration


class Command(BaseCommand):
    """Command to delete registrations which have expired."""
    help = 'Delete registrations that have expired'

    def handle(self, *args, **options):
        qs = Registration.expired_objects.all()
        count = qs.count()
        if count > 0:
            msg = 'Deleting {0} expired registration\n'
            self.stdout.write(msg.format(count))
            qs.delete()
        else:
            msg = 'No expired registration found\n'
            self.stdout.write(msg)
