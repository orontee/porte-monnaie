from datetime import date
from django.utils import six
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.contrib.auth.models import AbstractUser
from django.db.models import (AutoField, DateField, DateTimeField,
                              FloatField, ForeignKey, NullBooleanField,
                              CharField, ManyToManyField, Model,
                              SET_NULL)
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

mark_safe_lazy = lazy(mark_safe, six.text_type)


class User(AbstractUser):
    """Extend the ``User`` class with a ``Purse`` field.
    """
    default_purse = ForeignKey('Purse', verbose_name=_('default purse'),
                               null=True, default=None,
                               on_delete=SET_NULL)


class Purse(Model):
    """Class representing purses.
    """
    name = CharField(_('purse name'), max_length=80)
    users = ManyToManyField(User)
    description = CharField(_('description'), max_length=80, blank=True)
    timestamp = DateTimeField(_('timestamp'), auto_now=True, editable=False)

    def __unicode__(self):
        return u'Purse: {0}'.format(self.id)

    def usernames(self):
        """Return the comma separated list of usernames sorted.
        """
        names = [u.first_name or u.username for u in self.users.all()]
        names.sort()
        return ', '.join(names)

    class Meta(object):
        """Purse metadata.
        """
        ordering = ['name', '-timestamp']
        get_latest_by = 'timestamp'


class Expenditure(Model):
    """Class representing expenditures.
    """
    amount = FloatField(_('amount'), default=0)
    date = DateField(_('date'), default=timezone.now().date())
    description = CharField(_('description'), max_length=80, blank=True)
    author = ForeignKey(User, editable=False, verbose_name=_('author'))
    purse = ForeignKey(Purse, verbose_name=_('purse'))
    valid = NullBooleanField(_('valid'), default=True, editable=False)
    timestamp = DateTimeField(_('timestamp'), auto_now=True, editable=False)

    def __unicode__(self):
        return u'Expenditure: {0}'.format(self.id)

    class Meta(object):
        """Expenditure metadata.
        """
        ordering = ['-date', '-timestamp', 'author']
        get_latest_by = 'date'
