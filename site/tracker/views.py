"""Module defining the expenditures related views.
"""

from datetime import datetime
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ImproperlyConfigured
from django.db.models import (Sum, Count)
from django.http import HttpResponseRedirect
from django.views.generic import (CreateView,
                                  ListView,
                                  MonthArchiveView,
                                  RedirectView,
                                  UpdateView,
                                  YearArchiveView)
from tracker.models import (Expenditure, Purse)
from tracker.forms import ExpenditureForm
from tracker.utils import dictfetchall
from users.views.mixins import LoginRequiredMixin
from users.views.base import UserChange as UserChangeOrig

User = get_user_model()


class FieldNamesMixin(object):
    """Extends a view context with the ``field_names`` attribute.
    """
    def get_context_data(self, **kwargs):
        context = super(FieldNamesMixin, self).get_context_data(**kwargs)
        try:
            context['field_names'] = self.field_names
        except AttributeError:
            raise ImproperlyConfigured("field_names attribute "
                                       "required by FieldNamesMixin")
        return context



class QueryPaginationMixin(object):
    """Returns the number of items to paginate by, or None for no
    pagination.

    Query parameters are search first.
    """
    paginate_by = 15

    def get_paginate_by(self, queryset):
        if 'paginate_by' in self.request.GET:
            try:
                paginate_by = int(self.request.GET['paginate_by'])
            except ValueError:
                paginate_by = self.paginate_by
                # REMARK No pagination is not supported
        else:
            paginate_by = self.paginate_by
        return paginate_by

    def get_context_data(self, **kwargs):
        context = super(QueryPaginationMixin, self).get_context_data(**kwargs)
        context.update({'path_info': self.request.path_info})
        return context


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
    """List the logged in account purses.
    """
    model = Purse
    context_object_name = 'purses'
    field_names = ['name', 'users', 'description']

    def get_queryset(self):
        return self.request.user.purse_set.all()


class UserPurseMixin(object):
    """Set choices for the attribute whose name is ``purse_field_name``.

    The value set is the list of purses of the logged account.
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
        if not Purse.objects.filter(users__pk=user.pk).exists():
            return HttpResponseRedirect(
                reverse_lazy('tracker:purse_creation'))
        if self.purse is None:
            return HttpResponseRedirect(
                reverse_lazy('tracker:user_change'))
        return super(DefaultPurseMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        """
        context = super(DefaultPurseMixin, self).get_context_data(**kwargs)
        context.update({'shared_purse': self.purse.users.count() > 1})
        return context


class ExpenditureAdd(LoginRequiredMixin,
                     DefaultPurseMixin,
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
        form.instance.purse = self.purse
        response = super(ExpenditureAdd, self).form_valid(form)
        for date in form.other_dates:
            self.object.pk = None
            self.object.date = date
            self.object.save()
        return response


class ExpenditureMonthList(LoginRequiredMixin,
                           DefaultPurseMixin,
                           FieldNamesMixin,
                           QueryPaginationMixin,
                           MonthArchiveView):
    """List of expenditures in a month.
    """
    model = Expenditure
    context_object_name = 'expenditures'
    date_field = 'date'
    allow_empty = True
    field_names = ['date', 'amount', 'author', 'description']
    month_format = '%m'
    allow_future = True

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
        return context


class ExpenditureYearList(LoginRequiredMixin,
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
    allow_future = True

    def get_context_data(self, **kwargs):
        """"""
        context = super(ExpenditureYearList, self).get_context_data(**kwargs)
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
                        'totals':{'amount': sum(flat[0]),
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
