from datetime import date
from django.contrib.auth import get_user_model
from django.db.models import (AutoField, DateField, DateTimeField,
                              FloatField, ForeignKey, NullBooleanField,
                              CharField, Model)
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


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

    class Meta(object):
        """Expenditure metadata.
        """
        ordering = ['-date', '-timestamp', 'author']
        get_latest_by = 'date'
