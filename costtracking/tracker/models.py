from datetime import date
from django.db.models import (AutoField, DateField, DateTimeField,
                              FloatField, ForeignKey, NullBooleanField,
                              TextField, Model)
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class Expenditure(Model):
    """
    Class representing expenditures.
    """
    id = AutoField(primary_key=True, editable=False)
    amount = FloatField(default=0,
                        verbose_name=_('amount'),
                        help_text=_('amount of the expenditure'))
    date = DateField(default=date.today(),
                     verbose_name=_('date'),
                     help_text=_('date of the expenditure'))
    description = TextField(blank=True,
                            verbose_name=_('description'),
                            help_text=_('description, remark or whatever else related to the expenditure'))
    author = ForeignKey(User,
                        editable=False,
                        verbose_name=_('author'),
                        help_text=_('author of the expenditure'))
    valid = NullBooleanField(default=True,
                             editable=False,
                             verbose_name=_('valid'))
    timestamp = DateTimeField(auto_now=True,
                              verbose_name=_('timestamp'),
                              help_text=_('timestamp of the expenditure input'))

    class Meta(object):
        """
        Expenditure metadata.
        """
        ordering = ['date', 'timestamp', 'author']
    
