from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from users.models import Registration

User = get_user_model()


class Command(BaseCommand):
    """Command to delete inactive accounts without registration."""
    help = 'Delete inactive account without registration'

    def handle(self, *args, **options):
        qs = User.objects.filter(is_active=False)
        qs = qs.filter(registration__lte=0)
        count = qs.count()
        if count > 0:
            msg = 'Deleting {0} expired user account\n'
            self.stdout.write(msg.format(count))
            qs.delete()
        else:
            msg = 'No user account as expired\n'
            self.stdout.write(msg)
