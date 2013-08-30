from datetime import date
from django.contrib.auth.models import AbstractUser
from django.db.models import (AutoField, DateField, DateTimeField,
                              FloatField, ForeignKey, NullBooleanField,
                              CharField, ManyToManyField, Model)
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    """Extend the ``User`` class with a ``Purse`` field.
    """
    default_purse = ForeignKey('Purse', verbose_name=_('default purse'),
                               null=True, default=None)


class Purse(Model):
    """Class representing purses.
    """
    id = AutoField(primary_key=True, editable=False)
    name = CharField(_('name'), max_length=80)
    users = ManyToManyField(User)
    valid = NullBooleanField(_('valid'), default=True, editable=False)
    timestamp = DateTimeField(_('timestamp'), auto_now=True, editable=False)

    def __unicode__(self):
        return u'Purse: {0}'.format(self.id)
    
    class Meta(object):
        """Purse metadata.
        """
        ordering = ['name', '-timestamp']
        get_latest_by = 'timestamp'


class Expenditure(Model):
    """Class representing expenditures.
    """
    id = AutoField(primary_key=True, editable=False)
    amount = FloatField(_('amount'), default=0)
    date = DateField(_('date'), default=timezone.now().date())
    description = CharField(_('description'), max_length=80, blank=True)
    author = ForeignKey(User, editable=False, verbose_name=_('author'))
    valid = NullBooleanField(_('valid'), default=True, editable=False)
    timestamp = DateTimeField(_('timestamp'), auto_now=True, editable=False)
    
    def __unicode__(self):
        return u'Expenditure: {0}'.format(self.id)
    
    class Meta(object):
        """Expenditure metadata.
        """
        ordering = ['-date', '-timestamp', 'author']
        get_latest_by = 'date'
