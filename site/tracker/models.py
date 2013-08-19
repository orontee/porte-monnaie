from datetime import date
from django.db.models import (AutoField, DateField, DateTimeField,
                              FloatField, ForeignKey, NullBooleanField,
                              CharField, Model)
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class Expenditure(Model):
    """Class representing expenditures.
    """
    id = AutoField(primary_key=True, editable=False)
    amount = FloatField(_('amount'), default=0)
    date = DateField(_('date'), default=date.today())
    description = CharField(_('description'), max_length=80, blank=True)
    author = ForeignKey(User, editable=False, verbose_name=_('author'))
    valid = NullBooleanField(_('valid'), default=True, editable=False)
    timestamp = DateTimeField(_('timestamp'), auto_now=True, editable=False)

    class Meta(object):
        """Expenditure metadata.
        """
        ordering = ['-date', '-timestamp', 'author']
        get_latest_by = 'date'
