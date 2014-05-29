"""Models for users management.

"""
import hashlib
import random
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db.models import (CharField, DateTimeField,
                              ForeignKey, Manager, Model)
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class RegistrationManager(Manager):
    """Manager of the ``Registration`` model.

    """
    def activate_user(self, key):
        """Activate the account related to key.

        May raise a ``Registration.DoesNotExist`` exception.

        """
        reg = self.get(key=key)
        user = reg.user
        if reg.is_valid():
            user.is_active = True
            user.save()
        else:
            user = None
        reg.delete()
        return user

    def create_registration(self, user):
        """Create an account registration.

        """
        key = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()
        return self.create(user=user, key=key)


class ExpiredRegistrationManager(Manager):
    """Manager of the ``Registration`` model handling expired
    registrations only.

    """
    def get_query_set(self):
        """Return a query set for expired registrations.

        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=Registration.validity_delay)
        qs = super(ExpiredRegistrationManager, self).get_query_set()
        return qs.exclude(created__range=(start_date, end_date))


class Registration(Model):
    """Model for account registrations.

    It relates a key to a ``User`` model.

    """
    user = ForeignKey(User)
    key = CharField(_('key'), max_length=40)
    created = DateTimeField(_('created'), auto_now_add=True)
    validity_delay = 30

    objects = RegistrationManager()
    expired_objects = ExpiredRegistrationManager()

    def __str__(self):
        return u'Account registration: {0}'.format(self.user)

    def _send_email(self, subject_tmpl, msg_tmpl):
        """Send an email to the user.

        """
        var = {'key': self.key,
               'username': self.user.username}
        subject = render_to_string('users/{0}'.format(subject_tmpl),
                                   var)
        subject = subject[:-1]
        msg = render_to_string('users/{0}'.format(msg_tmpl), var)
        self.user.email_user(subject, msg)

    def send_creation_email(self):
        """Send the creation email.

        """
        self._send_email('email_creation_subject.txt',
                         'email_creation_msg.txt')

    def send_deletion_email(self):
        """Send the deletion email.

        """
        self._send_email('email_deletion_subject.txt',
                         'email_deletion_msg.txt')

    def is_valid(self):
        """Check whether it is a valid exception.

        """
        elapsed = (timezone.now() - self.created).days
        return elapsed <= self.validity_delay

    class Meta(object):
        verbose_name = _('account registration')
        verbose_name_plural = _('account registrations')
