"""Module defining the views.
"""
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from django.http import Http404
from django.views.generic import (CreateView, UpdateView, TemplateView)
from users.forms import (UserChangeForm, UserCreationForm)
from users.models import Registration
from users.views.mixins import LoginRequiredMixin

User = get_user_model()


class UserCreation(CreateView):
    """View to create a user account.
    """
    model = User
    template_name  = 'users/user_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('users:user_creation_done')


class UserChange(LoginRequiredMixin, UpdateView):
    """View to modify the logged user account.
    """
    model = User
    form_class = UserChangeForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_change_done')

    def get_object(self, queryset=None):
        """Returns the user account.
        """
        return self.request.user if self.request else None


class UserActivation(TemplateView):
    """View to activate a user account.
    """
    template_name = 'users/user_activation_done.html'

    def get_context_data(self, **kwargs):
        """Tries to activate the user account associated to key.
        """
        context = super(UserActivation, self).get_context_data(**kwargs)
        try:
            user = Registration.objects.activate_user(kwargs['key'])
        except (KeyError, Registration.DoesNotExist):
            user = None
        context.update({'key_user': user})
        return context
            
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if not context.get('key_user', None):
            return Http404            
        return self.render_to_response(context)
