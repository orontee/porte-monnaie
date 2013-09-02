import hashlib
import random
from django.contrib.auth import get_user_model
from django.db.models import (CharField, ForeignKey, Manager, Model)
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class RegistrationManager(Manager):
    """Manager of the ``Registration`` model.
    """

    def activate_user(self, key):
        """Activate the account related to key.

        May raise a ``Registration.DoesNotExist`` exception.
        """
        registration = self.get(key=key)
        user = registration.user
        user.is_active = True
        user.save()
        registration.delete()
        return user

    def create_registration(self, user):
        """Create an account registration.
        """
        key = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()
        return self.create(user=user, key=key)


class Registration(Model):
    """Model for account registrations.

    It relates a key to a ``User`` model.
    """
    user = ForeignKey(User)
    key = CharField(_('key'), max_length=40)

    objects = RegistrationManager()

    def __unicode__(self):
        return u'Account registration: {0}'.format(self.user)

    def send(self):
        """Send an email to the user.
        """
        var = {'key': self.key,
               'username': self.user.username}
        subject = render_to_string('users/email_subject.txt', var)
        subject = subject[:-1]
        msg = render_to_string('users/email_msg.txt', var)
        self.user.email_user(subject, msg)

    class Meta:
        verbose_name = _('account registration')
        verbose_name_plural = _('account registrations')
