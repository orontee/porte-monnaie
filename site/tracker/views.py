"""Module defining the views.
"""
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView,
                                  MonthArchiveView)
from tracker.models import Expenditure
from tracker.forms import ExpenditureForm
    
class LoginRequiredMixin(object):
    """Makes sure that a user is logged in before a request is performed.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class ExpenditureAdd(LoginRequiredMixin, CreateView):
    """View to add an expenditure.
    """
    model = Expenditure
    form_class = ExpenditureForm
    success_url = reverse_lazy('tracker:list')

    def post(self, request, *args, **kwargs):
        return super(ExpenditureAdd, self).post(request, *args, **kwargs)        

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super(ExpenditureAdd, self).form_valid(form)
        future = int(form.cleaned_data['occurrences']) - 1
        for delta in range(future):
            self.object.pk = None
            month = (self.object.date.month + 1) % 12 \
                    if self.object.date.month < 12 else 1
            year = self.object.date.year + 1 \
                   if month == 1 else self.object.date.year
            self.object.date = self.object.date.replace(month=month,
                                                        year=year)
            self.object.save()
        return response


class ExpenditureMonthList(LoginRequiredMixin, MonthArchiveView):
    """List of expenditures in a month.
    """
    model = Expenditure
    context_object_name = 'expenditures'
    date_field = 'date'
    allow_empty = True
    field_names = ['date', 'amount', 'author', 'description']
    month_format = '%m'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(ExpenditureMonthList, self).get_context_data(**kwargs)
        context['field_names'] = self.field_names
        user = self.request.user if self.request else None
        if user:
            qs = self.object_list.all()
            context.update(qs.aggregate(total_amount=Sum('amount')))
            context.update(qs.filter(author_id__exact=user.id)
                           .aggregate(user_amount=Sum('amount')))
        return context
