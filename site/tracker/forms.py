"""Tracker forms."""

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm as OrigAuthenticationForm,
    PasswordChangeForm as OrigPasswordChangeForm)
from django.core.exceptions import ValidationError
from django.forms import (ModelForm, ChoiceField, CharField)
from django.utils.translation import ugettext_lazy as _

from tracker.models import (Expenditure, Purse)
from bootstrap.forms import (BootstrapWidgetMixin, StaticControl)

User = get_user_model()

OCCURRENCES_CHOICES = (('1', _('unique')),
                       ('2', _('next two months')),
                       ('3', _('next three months')),
                       ('4', _('next four months')),
                       ('5', _('next five months')),
                       ('6', _('next six months')),
                       ('12', _('forthcoming year')))


class ExpenditureForm(BootstrapWidgetMixin, ModelForm):
    """Form to input an expenditure."""

    def clean_amount(self):
        """Amount field cleaning.

        It makes sure that the value is non-zero.

        """
        data = self.cleaned_data['amount']
        if data == 0:
            msg = _('The amount must be non-zero.')
            raise ValidationError(msg)
        return data

    def clean_description(self):
        """Description cleaning.

        It makes sure that the value is not made of whitespaces
        characters only.

        """
        data = self.cleaned_data['description'].strip()
        if data == '':
            msg = _('The description is required.')
            raise ValidationError(msg)
        return data

    class Meta(object):
        model = Expenditure
        fields = ['amount', 'date', 'description']


class MultipleExpenditureForm(ExpenditureForm):
    """Form to input multiple expenditures.

    An occurrences field is added to duplicate expenditure accross
    months.

    """
    occurrences = ChoiceField(choices=OCCURRENCES_CHOICES,
                              label=_('Occurrences'), required=True)

    def __init__(self, *args, **kwargs):
        """Initialize form."""
        super(MultipleExpenditureForm, self).__init__(*args, **kwargs)
        self.other_dates = []

    def clean(self):
        """Form-wide cleaning.

        The usual cleaning is extended by the generation of dates from
        the field named date by increasing its month as many times as
        specified by the field named occurences.

        When a build date raises a ``ValueError``, up to four previous
        days are tried to handle leap years and month with less than
        31 days.

        """
        cleaned_data = super(MultipleExpenditureForm, self).clean()
        if 'occurrences' in cleaned_data:
            count = int(cleaned_data['occurrences'])
            start = cleaned_data.get('date')
            if start:
                for delta in range(1, count):
                    total = start.month + delta
                    year = start.year if total <= 12 else start.year + 1
                    month = total if total <= 12 else total - 12
                    for i in range(4):
                        try:
                            next_date = start.replace(day=start.day - i,
                                                      month=month,
                                                      year=year)
                        except ValueError:
                            next_date = None
                        else:
                            self.other_dates.append(next_date)
                            break
                    if next_date is None:
                        msg = _('All expenditures must occur on valid dates.')
                        self._errors["occurrences"] = self.error_class([msg])
                        del cleaned_data['occurrences']
                        break
        return cleaned_data


class PurseForm(BootstrapWidgetMixin, ModelForm):
    """Form to input a purse."""

    class Meta(object):
        model = Purse
        fields = ['name', 'description']


class PurseShareForm(BootstrapWidgetMixin, ModelForm):
    """Form to input a user name."""

    user = CharField(label=_('user name'))

    def clean_user(self):
        """Clean name field."""
        data = self.cleaned_data['user']
        try:
            data = User.objects.get(username=data)
        except User.DoesNotExist:
            msg = _('This user name is unknown.')
            raise ValidationError(msg)
        return data

    def clean(self):
        """Form-wide cleaning.

        The usual cleaning is extended to check whether the user
        already owns the purse.

        """
        cleaned_data = super(PurseShareForm, self).clean()
        user = cleaned_data.get('user')
        purse = self.instance
        if user is not None and purse.users.filter(pk=user.pk).exists():
            msg = _("This user already own the purse.")
            self._errors["user"] = self.error_class([msg])
            del cleaned_data['user']
        return cleaned_data

    class Meta(object):
        model = Purse
        fields = ['name']
        widgets = {'name': StaticControl()}


class AuthenticationForm(BootstrapWidgetMixin,
                         OrigAuthenticationForm):
    """Improve default form with Bootstrap aware widgets."""
    pass


class PasswordChangeForm(BootstrapWidgetMixin,
                         OrigPasswordChangeForm):
    """Improve default form with Bootstrap aware widgets."""
    pass
