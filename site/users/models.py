"""Models for users management."""

import hashlib
import random
from datetime import timedelta
from django.conf import settings
from django.db.models import (CharField, DateTimeField,
                              ForeignKey, Manager, Model)
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class RegistrationManager(Manager):
    """Manager of the ``Registration`` model."""
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
        """Create an account registration."""
        key = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()
        return self.create(user=user, key=key)


class ExpiredRegistrationManager(Manager):
    """Manager handling expired registrations only."""
    def get_queryset(self):
        """Return a query set for expired registrations."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=Registration.validity_delay)
        qs = super(ExpiredRegistrationManager, self).get_queryset()
        return qs.exclude(created__range=(start_date, end_date))


class Registration(Model):
    """Model for account registrations.

    It relates a key to a ``User`` model.

    """
    user = ForeignKey(settings.AUTH_USER_MODEL)
    key = CharField(_('key'), max_length=40)
    created = DateTimeField(_('created'), auto_now_add=True)
    validity_delay = 30

    objects = RegistrationManager()
    expired_objects = ExpiredRegistrationManager()

    def __str__(self):
        return u'Account registration: {0}'.format(self.user)

    def is_valid(self):
        """Check whether it is a valid registration."""
        elapsed = (timezone.now() - self.created).days
        return elapsed <= self.validity_delay

    class Meta(object):
        verbose_name = _('account registration')
        verbose_name_plural = _('account registrations')
