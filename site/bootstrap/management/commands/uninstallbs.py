from django.core.management.base import BaseCommand
import os.path
import os
from shutil import rmtree
import bootstrap

class Command(BaseCommand):
    """Command to remove a Bootstrap tree from static directory.
    """
    help = 'Uninstall a Bootstrap tree'

    def handle(self, *args, **options):
        target = os.path.join(os.path.dirname(bootstrap.__file__),
                              'static', 'bootstrap')
        if not os.path.exists(target):
            self.stdout.write('Nothing to do')
        else:
            self.stdout.write('Removing tree: {0}\n'.format(target))
            rmtree(target)
