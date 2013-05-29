from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from optparse import make_option


class Command(BaseCommand):
    """Create a user.
    """
    args = '<name email password>'
    help = 'Create a user with specified attributes'
    option_list = BaseCommand.option_list + (
        make_option('--first',
                    dest='first_name',
                    help='user first name'),
        make_option('--last',
                    dest='last_name',
                    help='user last name'))

    def handle(self, *args, **options):
        try:
            User.objects.get(username=args[0])
        except User.DoesNotExist:
            user = User.objects.create_user(*args)
            if options['first_name']:
                user.first_name = options['first_name']
            if options['last_name']:
                user.last_name = options['last_name']
            user.save()
            print('User {0} created'.format(args[0]))
        else:
            print('User {0} already exists'.format(args[0]))
