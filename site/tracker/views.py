"""Module defining the views.
"""
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.views.generic import (CreateView,
                                  MonthArchiveView,
                                  RedirectView,
                                  UpdateView)
from tracker.models import (Expenditure, Purse)
from tracker.forms import ExpenditureForm
from users.views.mixins import LoginRequiredMixin

User = get_user_model()


class HomeView(RedirectView):
    """Home view.
    """
    url = reverse_lazy('tracker:list')


class OtherUsersMixin(object):
    """Set choices for the ``users`` attribute with the list of user
    acounts but the logged in account.
    """
    def get_form(self, form_class):
        try:
            form = super(OtherUsersMixin, self).get_form(form_class)
            users = User.objects.exclude(pk=self.request.user.pk)
        except AttributeError:
            raise ImproperlyConfigured("OtherUsersMixin requires the mixins "
                                       "LoginRequiredMixin and FormMixin")
        else:
            f = form.fields.get('users')
            f.choices = [(u.id, u.username) for u in users]
            return form


class PurseCreation(LoginRequiredMixin, OtherUsersMixin, CreateView):
    """View to create a purse.
    """
    model = Purse
    success_url = reverse_lazy('tracker:home')


class PurseUpdate(LoginRequiredMixin, OtherUsersMixin, UpdateView):
    """View to modify a purse.
    """
    model = Purse
    success_url = reverse_lazy('tracker:home')


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


class ExpenditureAdd(LoginRequiredMixin,
                     DefaultPurseMixin,
                     CreateView):
    """View to add expenditures.
    """
    model = Expenditure
    form_class = ExpenditureForm
    success_url = reverse_lazy('tracker:home')

    def get_initial(self):
        """Initialize the ``purse`` form field with the user account default
        purse.
        """
        initial = super(ExpenditureAdd, self).get_initial()
        initial.update({'purse': self.purse.id})
        return initial

    def form_valid(self, form):
        """If the form is valid, save the associated model instances.
        """
        form.instance.author = self.request.user
        response = super(ExpenditureAdd, self).form_valid(form)
        for date in form.other_dates:
            self.object.pk = None
            self.object.date = date
            self.object.save()
        return response


class ExpenditureMonthList(LoginRequiredMixin,
                           DefaultPurseMixin,
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
    paginate_by = 15

    def get_paginate_by(self, queryset):
        """Returns the number of items to paginate by, or None for no
        pagination.

        Query parameters are search first.
        """
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
        """Extends the context with view's specific data.'

        Table field names and various data computed from the
        expenditures amounts are added.
        """
        context = super(ExpenditureMonthList, self).get_context_data(**kwargs)
        context['field_names'] = self.field_names
        user = self.request.user if self.request else None
        if user:
            qs = self.object_list.all()
            context.update(qs.aggregate(total_amount=Sum('amount')))
            context.update(qs.filter(author_id__exact=user.id)
                           .aggregate(user_amount=Sum('amount')))
        context['params'] = {'month': self.get_month(),
                             'year': self.get_year()}
        return context
