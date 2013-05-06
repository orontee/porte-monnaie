from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (ListView, CreateView)
from tracker.models import Expenditure
    

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

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(ExpenditureAdd, self).form_valid(form)
    

class ExpenditureList(ListView):
    """List of expenditures.
    """
    model = Expenditure
    context_object_name = 'expenditures'
