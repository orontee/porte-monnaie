"""Module defining the expenditures related views.
"""

from datetime import datetime
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.views.generic import (CreateView,
                                  DeleteView,
                                  ListView,
                                  MonthArchiveView,
                                  RedirectView,
                                  UpdateView,
                                  YearArchiveView)
from tracker.models import (Expenditure, Purse, Tag)
from tracker.forms import ExpenditureForm
from tracker.utils import dictfetchall
from django.utils.translation import ugettext_lazy as _
from tracker.views.mixins import (FieldNamesMixin,
                                  QueryPaginationMixin,
                                  QueryFilterMixin,
                                  ObjectOwnerMixin,
                                  EditableObjectMixin)
from users.views.mixins import LoginRequiredMixin
from users.views.base import UserChange as UserChangeOrig

User = get_user_model()


class HomeView(RedirectView):
    """Home view.
    """
    url = reverse_lazy('tracker:list')


class PurseCreation(LoginRequiredMixin, CreateView):
    """View to create a purse.
    """
    model = Purse
    success_url = reverse_lazy('tracker:home')


class PurseUpdate(LoginRequiredMixin, UpdateView):
    """View to modify a purse.
    """
    model = Purse
    success_url = reverse_lazy('tracker:home')

    def dispatch(self, *args, **kwargs):
        """Check that the logged in account belongs to the requested purse.
        """
        obj = self.get_object()
        if not obj.users.filter(pk=self.request.user.pk).exists():
            return HttpResponseRedirect(reverse_lazy('tracker:logout'))
        return super(PurseUpdate, self).dispatch(*args, **kwargs)


class PurseList(LoginRequiredMixin,
                FieldNamesMixin,
                QueryPaginationMixin,
                ListView):
    """List the purses of the logged in account.
    """
    model = Purse
    context_object_name = 'purses'
    field_names = ['name', 'users', 'description']

    def get_queryset(self):
        return self.request.user.purse_set.all()


class UserPurseMixin(object):
    """Set choices for the attribute whose name is ``purse_field_name``.

    The value set is the list of purses of the logged account. The
    initial value rendered in an unbounded form is read from the
    ``purse`` attribute if it exists.
    """
    purse_field_name = 'purse'

    def get_form(self, form_class):
        try:
            form = super(UserPurseMixin, self).get_form(form_class)
            purses = self.request.user.purse_set.all()
        except AttributeError:
            raise ImproperlyConfigured("UserPurseMixin requires the mixin"
                                       "LoginRequiredMixin and FormMixin")
        else:
            f = form.fields.get(self.purse_field_name)
            f.choices = [(p.id, p.name) for p in purses]
            try:
                f.initial = self.purse
            except AttributeError:
                pass
            return form


class UserChange(UserPurseMixin, UserChangeOrig):
    purse_field_name = 'default_purse'


class DefaultPurseMixin(object):
    """Provides an accessor to the user account default purse.

    If the user does not belong to any purse, redirect to purse
    creation page. Otherwise, if the user account default purse has
    not been set, redirect to the user change page.
    """
    @property
    def purse(self):
        try:
            user = self.request.user
        except AttributeError:
            raise ImproperlyConfigured("DefaultPurseMixin requires the mixin"
                                       "LoginRequiredMixin")
        else:
            try:
                purse = user.default_purse
            except AttributeError:
                raise ImproperlyConfigured("User model does not define a "
                                           "purse attribute")
            else:
                return purse

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        purses = Purse.objects.filter(users__pk=user.pk)
        if not purses.exists():
            return HttpResponseRedirect(
                reverse_lazy('tracker:purse_creation'))
        if self.purse is None:
            return HttpResponseRedirect(
                reverse_lazy('tracker:user_change'))
        return super(DefaultPurseMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DefaultPurseMixin, self).get_context_data(**kwargs)
        context.update({'shared_purse': self.purse.users.count() > 1})
        return context


class ObjectPurseMixin(object):
    """Extend a view with a property referring to the object purse.
    """
    @property
    def purse(self):
        try:
            purse = self.object.purse
        except AttributeError:
            raise ImproperlyConfigured("object attribute required "
                                       "ObjectPurseMixin")
        else:
            return purse


class TagNamesMixin(object):
    """Extend a view context with the list of tags associated to a given
    purse.
    """
    def get_context_data(self, **kwargs):
        context = super(TagNamesMixin, self).get_context_data(**kwargs)
        try:
            purse = self.purse
        except AttributeError:
            raise ImproperlyConfigured("purse attribute required "
                                       "by TagNamesMixin")
        context.update({'tagnames': Tag.objects.get_names_for(purse)})
        return context


class ExpenditureAdd(LoginRequiredMixin,
                     UserPurseMixin,
                     DefaultPurseMixin,
                     TagNamesMixin,
                     CreateView):
    """View to add expenditures.
    """
    model = Expenditure
    form_class = ExpenditureForm
    success_url = reverse_lazy('tracker:home')

    def form_valid(self, form):
        """If the form is valid, save the associated model instances.
        """
        form.instance.author = self.request.user
        form.instance.purse = form.instance.purse or self.purse
        response = super(ExpenditureAdd, self).form_valid(form)
        for date in form.other_dates:
            self.object.pk = None
            self.object.date = date
            self.object.generated = True
            self.object.save()
        return response


class ExpenditureDelete(LoginRequiredMixin,
                        ObjectOwnerMixin,
                        EditableObjectMixin,
                        DeleteView):
    """View to delete expenditures.
    """
    model = Expenditure
    context_object_name = 'expenditure'
    success_url = reverse_lazy('tracker:home')


class ExpenditureUpdate(LoginRequiredMixin,
                        ObjectPurseMixin,
                        ObjectOwnerMixin,
                        EditableObjectMixin,
                        TagNamesMixin,
                        UpdateView):
    """View to update expenditures.
    """
    model = Expenditure
    context_object_name = 'expenditure'
    form_class = ExpenditureForm
    success_url = reverse_lazy('tracker:home')


class ExpenditureList(LoginRequiredMixin,
                      DefaultPurseMixin,
                      FieldNamesMixin,
                      QueryPaginationMixin,
                      ListView):
    """List of latest expenditures.
    """
    model = Expenditure
    context_object_name = 'expenditures'
    field_names = ['date', 'amount', 'author', 'description']
    allow_empty = True
    allow_future = True

    def get_queryset(self):
        qs = super(ExpenditureList, self).get_queryset()
        qs = qs.filter(purse=self.purse)
        return qs

    def get_context_data(self, **kwargs):
        """Extends the context with view's specific data.

        Table field names and various data computed from the
        expenditures amounts are added.
        """
        context = super(ExpenditureMonthList, self).get_context_data(**kwargs)
        user = self.request.user if self.request else None
        if user:
            qs = self.object_list.all()
            context.update(qs.aggregate(total_amount=Sum('amount')))
            context.update(qs.filter(author_id__exact=user.id)
                           .aggregate(user_amount=Sum('amount')))
        context['params'] = {'month': self.get_month(),
                             'year': self.get_year()}
        context['edit_delay'] = Expenditure.edit_delay
        return context


class ExpenditureMonthList(LoginRequiredMixin,
                           DefaultPurseMixin,
                           FieldNamesMixin,
                           QueryFilterMixin,
                           QueryPaginationMixin,
                           MonthArchiveView):
    """List of expenditures in a month.
    """
    model = Expenditure
    context_object_name = 'expenditures'
    date_field = 'date'
    field_names = ['date', 'amount', 'author', 'description']
    month_format = '%m'
    allow_empty = True
    allow_future = True
    filter_description = _('Filter expenditures')

    def get_queryset(self):
        qs = super(ExpenditureMonthList, self).get_queryset()
        qs = qs.filter(purse=self.purse)
        return qs

    def get_context_data(self, **kwargs):
        """Extends the context with view's specific data.

        Table field names and various data computed from the
        expenditures amounts are added.
        """
        context = super(ExpenditureMonthList, self).get_context_data(**kwargs)
        user = self.request.user if self.request else None
        if user:
            qs = self.object_list.all()
            context.update(qs.aggregate(total_amount=Sum('amount')))
            context.update(qs.filter(author_id__exact=user.id)
                           .aggregate(user_amount=Sum('amount')))
        context['params'] = {'month': self.get_month(),
                             'year': self.get_year()}
        context['edit_delay'] = Expenditure.edit_delay

        return context


class ExpenditureYearSummary(LoginRequiredMixin,
                             DefaultPurseMixin,
                             FieldNamesMixin,
                             YearArchiveView):
    """Summary of expenditures in a year.
    """
    model = Expenditure
    make_object_list = True
    context_object_name = 'expenditures'
    field_names = ['date', 'amount', 'author', 'description']
    date_field = 'date'
    allow_empty = True
    allow_future = True

    def get_context_data(self, **kwargs):
        """"""
        context = super(ExpenditureYearSummary,
                        self).get_context_data(**kwargs)
        users = self.purse.users.count()
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute('SELECT t.*, t.average - t.amount AS delta FROM '
                       '(SELECT date_trunc(\'month\', date) AS month, '
                       'SUM(CASE WHEN author_id=%s THEN amount ELSE 0 END)'
                       ' AS amount, '
                       'SUM(amount)/%s AS average, '
                       'COUNT(id) AS count '
                       'FROM tracker_expenditure '
                       'WHERE EXTRACT(YEAR FROM date)=%s AND purse_id=%s '
                       'GROUP BY month ORDER BY month) AS t;',
                       [self.request.user.id,
                        users,
                        self.get_year(),
                        self.purse.id])
        values = dictfetchall(cursor)
        flat = [[d['amount'] for d in values],
                [d['average'] for d in values],
                [d['delta'] for d in values]]
        context.update({'amounts': values,
                        'totals': {'amount': sum(flat[0]),
                                   'average': sum(flat[1]),
                                   'delta': sum(flat[2])}})
        return context


class ExpenditureHome(RedirectView):
    """Start page when browsing expenditures.
    """
    url = reverse_lazy('tracker:archive',
                       kwargs=dict(zip(['month', 'year'],
                                       '{0:%m},{0:%Y}'.format(
                                           datetime.today()).split(','))))
