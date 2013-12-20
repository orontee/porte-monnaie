"""Module defining the expenditures related views.
"""

import datetime
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Sum
from django.http import (HttpResponseRedirect, Http404)
from django.views.generic import (CreateView,
                                  DeleteView,
                                  ListView,
                                  MonthArchiveView,
                                  RedirectView,
                                  UpdateView,
                                  TemplateView)
from tracker.models import (Expenditure, Purse, Tag)
from tracker.forms import ExpenditureForm
from tracker.utils import dictfetchall
from django.utils.datastructures import SortedDict
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
        qs = super(PurseList, self).get_queryset()
        qs = qs.filter(users=self.request.user)
        return qs


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

    # TODO Do not save when the purse is not a user purse


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
                                           "purse_default attribute")
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
            raise ImproperlyConfigured("object attribute required by"
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
        form.instance.purse = self.purse
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
    template_name = 'tracker/expenditure_month_list.html'

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


class ExpenditureMonthTags(LoginRequiredMixin,
                           DefaultPurseMixin,
                           FieldNamesMixin,
                           QueryFilterMixin,
                           QueryPaginationMixin,
                           ListView):
    """Statistics on expenditures in a month.
    """
    model = Tag
    context_object_name = 'tags'
    field_names = ['name', 'amount']
    allow_empty = True
    filter_description = _('Filter tags')
    filter_attr = 'name'
    template_name = 'tracker/expenditure_month_tags.html'

    def get_date(self):
        try:
            year = int(self.kwargs['year'])
        except KeyError:
            raise Http404("No year specified")
        try:
            month = int(self.kwargs['month'])
        except KeyError:
            raise Http404("No month specified")
        try:
            date = datetime.date(year=year, month=month, day=1)
        except ValueError:
            raise Http404("Invalid date string '{0}' or '{1}'".format(year, month))
        return date
            
    def get_queryset(self):
        """Build query for tags of a given purse, with expenditures in a given
        month.
        """
        qs = super(ExpenditureMonthTags, self).get_queryset()
        qs = qs.filter(purse=self.purse)        
        qs = qs.extra(where=["""UPPER("tracker_expenditure"."description"::text) """
                             """LIKE UPPER('%%'||"tracker_tag"."name"||'%%')"""])
        date = self.get_date()
        qs = qs.filter(purse__expenditure__date__year=date.year,
                       purse__expenditure__date__month=date.month)

        return qs
        
    def get_context_data(self, **kwargs):
        """Extend the view context with the month tags.
        """
        context = super(ExpenditureMonthTags,
                        self).get_context_data(**kwargs)       
        date = self.get_date()
        previous_month = date.replace(year=date.year + (date.month - 2) / 12, month=(date.month - 2) % 12 + 1, day=1)
        next_month = date.replace(year=date.year + date.month / 12, month=date.month % 12 + 1, day=1)
        context.update({'month': date,
                        'next_month': next_month,
                        'previous_month': previous_month})

        
        qs = context['object_list']
        amounts = list(qs.values('name').annotate(amount=Sum('purse__expenditure__amount')))
        amounts.sort(cmp=lambda x,y: -cmp(x['amount'], y['amount']))
        context['amounts'] = amounts
        return context


class ExpenditureYearSummary(LoginRequiredMixin,
                             DefaultPurseMixin,
                             TemplateView):
    """Summary of expenditures in a year.
    """
    template_name = 'tracker/expenditure_year_summary.html'

    def get_date(self):
        try:
            year = int(self.kwargs['year'])
        except KeyError:
            raise Http404("No year specified")
        try:
            date = datetime.date(year=year, month=1, day=1)
        except ValueError:
            raise Http404("Invalid year string '{0}'".format(year))
        return date
    
    def get_context_data(self, **kwargs):
        """Extend the view context with dates and amounts.
        """
        context = super(ExpenditureYearSummary,
                        self).get_context_data(**kwargs)
        date = self.get_date()
        next_year = date.replace(year=date.year + 1, month=1, day=1)
        previous_year = date.replace(year=date.year - 1, month=1, day=1)
        context.update({'year': date,
                        'next_year': next_year,
                        'previous_year': previous_year})

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
                        date.year,
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
                                           datetime.datetime.today()).split(','))))
