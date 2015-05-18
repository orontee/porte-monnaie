from django.core.management.base import (LabelCommand, CommandError)
import os.path
import os
from shutil import rmtree
from zipfile import (ZipFile, is_zipfile)
import bootstrap


class Command(LabelCommand):
    """Command to unzip a Bootstrap archive into static directory."""
    help = 'Install a Bootstrap archive'

    def handle_label(self, label, **options):
        source = str(label)
        if not os.path.exists(source):
            raise CommandError('Invalid file path: {0}'.format(source))
        if not is_zipfile(source):
            raise CommandError('Invalid zip file: {0}'.format(source))
        parent = os.path.join(os.path.dirname(bootstrap.__file__),
                              'static')
        tmp = os.path.join(parent,
                           os.path.splitext(os.path.split(source)[1])
                           [0])
        if os.path.exists(tmp):
            self.stdout.write('Removing tree: {0}\n'.format(tmp))
            rmtree(tmp)
        self.stdout.write('Extracting to: {0}\n'.format(tmp))
        z = ZipFile(source)
        z.extractall(parent)
        z.close()
        target = os.path.join(parent, 'bootstrap')
        if os.path.exists(target):
            self.stdout.write('Removing tree: {0}\n'.format(target))
            rmtree(target)
        self.stdout.write('Renaming {0} to {1}\n'.format(tmp, target))
        os.rename(tmp, target)
