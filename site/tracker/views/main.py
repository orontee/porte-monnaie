"""Tracker views."""

import datetime
import json
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.urlresolvers import (reverse_lazy, reverse)
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Sum
from django.http import (HttpResponse, HttpResponseRedirect, Http404)
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (CreateView,
                                  DeleteView,
                                  ListView,
                                  MonthArchiveView,
                                  RedirectView,
                                  TemplateView,
                                  UpdateView,
                                  View)
from tracker.models import (Expenditure, Purse, Tag)
from tracker.forms import (ExpenditureForm,
                           MultipleExpenditureForm,
                           PurseForm,
                           PurseShareForm)
from tracker.utils import dictfetchall
from tracker.views.mixins import (EditableObjectMixin,
                                  FieldNamesMixin,
                                  ObjectOwnerMixin,
                                  QueryPaginationMixin,
                                  QueryFilterMixin,
                                  WithCurrentDateMixin)
from users.views.mixins import LoginRequiredMixin
from users.views.base import UserChange as UserChangeOrig

User = get_user_model()


class HomeView(TemplateView):
    """Home view."""
    template_name = 'tracker/home.html'


class PurseCreation(LoginRequiredMixin,
                    WithCurrentDateMixin,
                    CreateView):
    """View to create a purse."""
    model = Purse
    form_class = PurseForm
    success_url = reverse_lazy('tracker:purse_list')
    is_active = None

    def get_success_url(self):
        """Determine the success URL depending on purses count.

        Note that the user is added to the created purse after the
        success URL is computed.

        """
        user = self.request.user
        if self.request.method == 'POST' and user.purse_set.count() == 0:
            msg = _('You just created your first purse. Use the <q>Add</q> '
                    'button of the top bar to start adding expenditures to '
                    'that purse.')
            messages.info(self.request, msg)
            url = reverse('tracker:list')
        else:
            url = force_text(self.success_url)
        return url

    def form_valid(self, form):
        """Process a valid form.

        The user is added to the purse users and its default purse is
        set.

        """
        res = super(PurseCreation, self).form_valid(form)
        self.object.users.add(self.request.user)
        self.object.save()

        user = self.request.user
        user.default_purse = self.object
        user.save()
        return res

    def get_context_data(self, **kwargs):
        context = super(PurseCreation, self).get_context_data(**kwargs)
        context.update({'user_has_purse':
                        self.request.user.purse_set.count() > 0})
        return context


class PurseUpdate(LoginRequiredMixin,
                  WithCurrentDateMixin,
                  UpdateView):
    """View to modify a purse."""
    model = Purse
    form_class = PurseForm
    success_url = reverse_lazy('tracker:purse_list')

    def dispatch(self, *args, **kwargs):
        """Check that the logged in account belongs to the requested purse."""
        obj = self.get_object()
        if not obj.users.filter(pk=self.request.user.pk).exists():
            return HttpResponseRedirect(reverse_lazy('tracker:logout'))
        return super(PurseUpdate, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PurseUpdate, self).get_context_data(**kwargs)
        context.update({'user_has_purse': True})
        return context


class DefaultPurseMixin(object):
    """Provides an accessor to the user account default purse.

    If the user does not belong to any purse, redirect to purse
    creation page. Otherwise, if the user account default purse has
    not been set, set the default purse to one of the user purses.

    Messages notify the user of the purse creation or the change of
    default purse.

    """
    @property
    def purse(self):
        try:
            user = self.request.user
        except AttributeError:
            raise ImproperlyConfigured('DefaultPurseMixin requires the mixin '
                                       'LoginRequiredMixin')
        else:
            try:
                return user.default_purse
            except AttributeError:
                raise ImproperlyConfigured('User model does not define a '
                                           'purse_default attribute')

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        purses = Purse.objects.filter(users__pk=user.pk)
        if not purses.exists():
            msg = _('First, create a purse...')
            messages.info(self.request, msg)
            return HttpResponseRedirect(
                reverse_lazy('tracker:purse_creation'))
        if self.purse is None:
            user.default_purse = purses[0]
            user.save()
            msg = _('Your default purse is now <q>{name}</q>.')
            messages.info(self.request, msg.format(name=purses[0].name))
        return super(DefaultPurseMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DefaultPurseMixin, self).get_context_data(**kwargs)
        context.update({'shared_purse': self.purse.users.count() > 1})
        return context


class PurseList(LoginRequiredMixin,
                FieldNamesMixin,
                DefaultPurseMixin,
                WithCurrentDateMixin,
                QueryPaginationMixin,
                ListView):
    """List the purses of the logged in account."""
    model = Purse
    context_object_name = 'purses'
    field_names = ['name', 'users', 'description']

    def get_queryset(self):
        qs = super(PurseList, self).get_queryset()
        qs = qs.filter(users=self.request.user).select_related()
        return qs


class PurseDelete(LoginRequiredMixin,
                  WithCurrentDateMixin,
                  ObjectOwnerMixin,
                  DeleteView):
    """View to delete a purse."""
    model = Purse
    context_object_name = 'purse'
    success_url = reverse_lazy('tracker:purse_list')

    def is_owner(self, user, obj):
        return user in obj.users.all()


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
            raise ImproperlyConfigured('UserPurseMixin requires the mixin '
                                       'LoginRequiredMixin and FormMixin')
        else:
            f = form.fields.get(self.purse_field_name)
            f.choices = [(p.id, p.name) for p in purses]
            try:
                f.initial = self.purse
            except AttributeError:
                pass
        return form

    # TODO Do not save when the purse is not a user purse


class UserChange(UserPurseMixin,
                 WithCurrentDateMixin,
                 UserChangeOrig):
    purse_field_name = 'default_purse'
    success_url = reverse_lazy('tracker:list')


class PurseShare(LoginRequiredMixin,
                 WithCurrentDateMixin,
                 UpdateView):
    """View to invite a user to join a purse."""
    template_name = 'tracker/purse_share.html'
    context_object_name = 'purse'
    model = Purse
    form_class = PurseShareForm
    success_url = reverse_lazy('tracker:purse_list')

    def get_form_kwargs(self):
        kwargs = super(PurseShare, self).get_form_kwargs()
        del kwargs['instance']
        return kwargs

    def form_valid(self, form):
        """Process a valid form.

        The user is notified.

        """
        other = form.cleaned_data['user']
        purse = self.get_object()
        if purse.users.filter(pk=other.pk).exists():
            msg = _("The purse called <q>{purse}</q> is "
                    "already shared with {other}.")
        else:
            msg = _("The purse called <q>{purse}</q> is "
                    "now shared with {other}.")
            purse.users.add(other)
        messages.info(self.request, msg.format(other=other.get_full_name(),
                                               purse=purse.name))
        return HttpResponseRedirect(self.get_success_url())


class ObjectPurseMixin(object):
    """Extend a view with a purse attribute.

    The purse instance is taken from an ``object`` attribute.

    """
    @property
    def purse(self):
        try:
            purse = self.object.purse
        except AttributeError:
            raise ImproperlyConfigured('object attribute required by '
                                       'ObjectPurseMixin')
        else:
            return purse


class ExpenditureAdd(LoginRequiredMixin,
                     DefaultPurseMixin,
                     WithCurrentDateMixin,
                     CreateView):
    """View to add expenditures."""
    model = Expenditure
    form_class = MultipleExpenditureForm

    def get_success_url(self):
        """Handles redirection target.

        Redirection goes to the expenditures list or the expenditure
        creation page according to request post data.

        """
        if 'save_other' in self.request.POST:
            return reverse_lazy('tracker:add')
        return reverse_lazy('tracker:list')

    def form_valid(self, form):
        """Completes then saves a valid form."""
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
                        WithCurrentDateMixin,
                        ObjectOwnerMixin,
                        EditableObjectMixin,
                        DeleteView):
    """View to delete expenditures."""
    model = Expenditure
    context_object_name = 'expenditure'
    success_url = reverse_lazy('tracker:list')
    owner_field = "author"


class ExpenditureUpdate(LoginRequiredMixin,
                        WithCurrentDateMixin,
                        ObjectPurseMixin,
                        ObjectOwnerMixin,
                        EditableObjectMixin,
                        UpdateView):
    """View to update expenditures."""
    model = Expenditure
    context_object_name = 'expenditure'
    form_class = ExpenditureForm
    success_url = reverse_lazy('tracker:list')
    owner_field = "author"


class ExpenditureFilteredList(LoginRequiredMixin,
                              DefaultPurseMixin,
                              FieldNamesMixin,
                              QueryFilterMixin,
                              QueryPaginationMixin,
                              ListView):
    """Filtered list of expenditures.

    This view handles:

    - Query parameters to filter the default query set;

    - Pagination.

    """
    model = Expenditure
    context_object_name = 'expenditures'
    field_names = ['date', 'amount', 'author', 'description']
    allow_empty = True
    allow_future = True
    filter_description = _('Filter expenditures')
    template_name = 'tracker/expenditure_filtered_list.html'

    def get_queryset(self):
        """Filter the default query set.

        The query set is filtered to match expenditures belonging to
        the default purse of the authenticated user.

        """
        qs = super(ExpenditureFilteredList, self).get_queryset()
        qs = qs.filter(purse=self.purse).select_related('author__username')
        return qs

    def get_context_data(self, **kwargs):
        """Extends the context with view's specific data.

        Table field names and various data computed from the
        expenditures amounts are added.

        """
        context = super(ExpenditureFilteredList, self).get_context_data(
            **kwargs)
        user = self.request.user if self.request else None
        if user:
            qs = self.object_list.all()
            context.update(qs.aggregate(total_amount=Sum('amount')))
            context.update(qs.filter(author_id__exact=user.id)
                           .aggregate(user_amount=Sum('amount')))
        return context


class ExpenditureMonthList(LoginRequiredMixin,
                           DefaultPurseMixin,
                           FieldNamesMixin,
                           WithCurrentDateMixin,
                           QueryPaginationMixin,
                           MonthArchiveView):
    """List of expenditures in a month.

    This view handles:

    - Pagination.

    """
    model = Expenditure
    context_object_name = 'expenditures'
    date_field = 'date'
    field_names = ['date', 'amount', 'author', 'description']
    month_format = '%m'
    allow_empty = True
    allow_future = True
    template_name = 'tracker/expenditure_month_list.html'

    def get_queryset(self):
        qs = super(ExpenditureMonthList, self).get_queryset()
        qs = qs.filter(purse=self.purse).select_related('author__username')
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


class ExpenditureYearSummary(LoginRequiredMixin,
                             DefaultPurseMixin,
                             WithCurrentDateMixin,
                             TemplateView):
    """Summary of expenditures in a year."""
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
        """Extend the view context with dates and amounts."""
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
    """Start page when browsing expenditures."""
    url = reverse_lazy('tracker:archive',
                       kwargs=dict(zip(['month', 'year'],
                                       '{0:%m},{0:%Y}'.format(
                                           datetime.datetime.today())
                                       .split(','))))


class TagView(LoginRequiredMixin,
              DefaultPurseMixin,
              View):
    """List of tags.

    The query parameter `limit` can be used to limit the number of
    tags in the list.
    """
    http_method_names = ['get', 'head', 'options', 'trace']

    def get(self, request, *args, **kwargs):
        """Return list of tag names."""
        try:
            limit = request.GET['limit']
        except KeyError:
            limit = None
        try:
            ordering = request.GET['ordering']
        except KeyError:
            ordering = None
        purse = self.purse
        tags = Tag.objects.get_tags_for(purse)
        if ordering is not None:
            tags = tags.order_by(ordering)
        if limit is not None:
            tags = tags[:limit]
        data = json.dumps(list(tags.values('name', 'count', 'amount')))
        return HttpResponse(data, content_type='application/json')
