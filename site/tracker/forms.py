"""Tracker forms.

"""

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm as OrigAuthenticationForm,
    PasswordChangeForm as OrigPasswordChangeForm)
from django.core.exceptions import ValidationError
from django.forms import (Form, ModelForm,
                          ChoiceField, CharField)
from django.utils.translation import ugettext_lazy as _
from tracker.models import (Expenditure, Purse)
from bootstrap.forms import BootstrapWidgetMixin

User = get_user_model()

OCCURRENCES_CHOICES = (('1', _('unique')),
                       ('2', _('next two months')),
                       ('3', _('next three months')),
                       ('4', _('next four months')),
                       ('5', _('next five months')),
                       ('6', _('next six months')),
                       ('12', _('forthcoming year')))


class ExpenditureForm(BootstrapWidgetMixin, ModelForm):
    """Form to input an expenditure.

    """
    occurrences = ChoiceField(choices=OCCURRENCES_CHOICES,
                              label=_('Occurrences'))
    other_dates = []

    class Meta(object):
        model = Expenditure
        fields = ['amount', 'date', 'description']

    def __init__(self, *args, **kwargs):
        super(ExpenditureForm, self).__init__(*args, **kwargs)
        self.fields['amount'].localize = True

        # REMARK Django 1.6 will provide the localized_fields
        # attribute

    def clean_amount(self):
        """Amount field cleaning.

        It makes sure that the value is non-zero.

        """
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


class PurseForm(BootstrapWidgetMixin, ModelForm):
    """Form to input a purse.

    """
    class Meta(object):
        model = Purse
        exclude = ['users']


class PurseShareForm(BootstrapWidgetMixin, Form):
    """Form to input a user name.

    """
    user = CharField(label=_('user name'))

    def clean_user(self):
        """Name field cleaning.

        """
        data = self.cleaned_data['user']
        try:
            data = User.objects.get(username=data)
        except User.DoesNotExist:
            msg = _('This user name is unknown.')
            raise ValidationError(msg)
        return data


class AuthenticationForm(BootstrapWidgetMixin,
                         OrigAuthenticationForm):
    """Improve default authentication form with Bootstrap aware widgets.

    """
    pass


class PasswordChangeForm(BootstrapWidgetMixin,
                         OrigPasswordChangeForm):
    """Improve default password change form with Bootstrap aware widgets.

    """
    pass
