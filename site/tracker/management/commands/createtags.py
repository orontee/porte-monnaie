from django.core.management.base import BaseCommand
from optparse import make_option
from tracker.models import (Expenditure, Tag)

class Command(BaseCommand):
    """Create or update tags.
    """
    help = 'Create or update tags'

    def handle(self, *args, **options):
        qs = Expenditure.objects.order_by('timestamp')
        stats = [0, 0]
        for e in qs:
            Tag.objects.update_from(e, stats)
        print('Tags created: {0}, updated: {1}'.format(stats[0], stats[1]))
