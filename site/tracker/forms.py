from django.core.exceptions import ValidationError
from django.forms import (ModelForm, ChoiceField)
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import (UserChangeForm as OrigUserChangeForm)
from tracker.models import Expenditure


class UserChangeForm(OrigUserChangeForm):
    """Form to change a user data.
    """
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        suppress = ('password', 'is_active', 'is_superuser', 'is_staff',
                    'user_permissions', 'last_login', 'date_joined',
                    'groups')
        for k in suppress:
            del self.fields[k]

OCCURRENCES_CHOICES = (('1', _('unique')),
                       ('2', _('next two months')),
                       ('3', _('next three months')),
                       ('4', _('next four months')),
                       ('5', _('next five months')),
                       ('6', _('next six months')),
                       ('12', _('forthcoming year')))


class ExpenditureForm(ModelForm):
    """Form to input an expenditure.
    """
    occurrences = ChoiceField(choices=OCCURRENCES_CHOICES,
                              label=_('Occurrences'))
    other_dates = []

    def __init__(self, *args, **kwargs):
        super(ExpenditureForm, self).__init__(*args, **kwargs)
        self.fields['amount'].localize = True

        # REMARK Django 1.6 will provide the localized_fields
        # attribute

    def clean_amount(self):
        """"""
        data = self.cleaned_data['amount']
        if data == 0:
            msg = _('The amount must be non-zero.')
            raise ValidationError(msg)
        return data

    def clean(self):
        """Form-wide cleaning.

        The usual cleaning is extended by the generation of dates from
        the field named date by increasing its month as many times as
        specified by the field named occurences.
        """
        cleaned_data = super(ExpenditureForm, self).clean()
        count = int(cleaned_data['occurrences']) - 1
        start = cleaned_data.get('date')
        if start:
            for delta in range(count):
                month = start.month + 1 if start.month < 12 else 1
                year = start.year + 1 if month == 1 else start.year
                try:
                    start = start.replace(month=month, year=year)
                except ValueError:
                    msg = _('All expenditures must occur on valid dates.')
                    self._errors["occurrences"] = self.error_class([msg])
                    del cleaned_data['occurrences']
                    break
                else:
                    self.other_dates.append(start)
        return cleaned_data

    class Meta(object):
        """The data associated to the expenditure form.
        """
        model = Expenditure
