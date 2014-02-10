from django.core.management.base import (LabelCommand, CommandError)
import os.path
import os
from shutil import rmtree
from zipfile import (ZipFile, is_zipfile)
import bootstrap

class Command(LabelCommand):
    """Command to unzip a Bootstrap archive into static directory.
    """
    help = 'Install a Bootstrap archive'

    def handle_label(self, label, **options):
        source = str(label)
        target = os.path.join(os.path.dirname(bootstrap.__file__),
                              'static', 'bootstrap')
        if not os.path.exists(source):
            raise CommandError('Invalid file path: {0}'.format(source))
        if not is_zipfile(source):
            raise CommandError('Invalid zip file: {0}'.format(source))
        if os.path.exists(target):
            self.stdout.write('Removing tree: {0}\n'.format(target))
            rmtree(target)
        self.stdout.write('Creating directory: {0}\n'.format(target))
        os.mkdir(target)
        self.stdout.write('Extracting to: {0}\n'.format(target))
        with ZipFile(source) as z:
            z.extractall(target)
