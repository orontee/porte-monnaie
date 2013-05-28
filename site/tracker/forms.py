from django.forms import (ModelForm, ChoiceField)
from tracker.models import Expenditure
from django.utils.translation import ugettext_lazy as _

OCCURRENCES_CHOICES = (('1', _('unique')),
                       ('4', _('next four months')),
                       ('5', _('next five months')),
                       ('6', _('next six months')),
                       ('12', _('forthcoming year')))

class ExpenditureForm(ModelForm):
    """
    Form to input an expenditure.
    """
    occurrences = ChoiceField(choices=OCCURRENCES_CHOICES,
                             label=_('Occurrences'),
                             help_text=
                             _('The number of occurrences of the expenditure'))

    class Meta(object):
        model = Expenditure
        fields = ('amount', 'date', 'description', 'occurrences')

