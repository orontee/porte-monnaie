from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, UpdateView, TemplateView)
from register.forms import (UserChangeForm, UserCreationForm)
from register.models import Registration


class UserChange(UpdateView):
    """View to modify user account.
    """
    model = get_user_model()
    template_name = 'register/user_change_form.html'
    form_class = UserChangeForm
    success_url = reverse_lazy('register:user_change_done')

    def get_object(self, queryset=None):
        """Returns the user data.
        """
        return self.request.user if self.request else None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """Makes sure that a user is logged in before a request is performed.
        """
        return super(UserChange, self).dispatch(*args, **kwargs)


class UserCreation(CreateView):
    """View to create a user account.
    """
    model = get_user_model()
    template_name = 'register/user_creation_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register:user_creation_done')


class UserActivation(TemplateView):
    """View to activate a user account.
    """
    template_name = 'register/user_activate_done.html'

    def get_context_data(self, **kwargs):
        """Tries to activate the user account associated to key.
        """
        context = super(UserActivation, self).get_context_data(**kwargs)
        try:
            user = Registration.objects.activate_user(kwargs['key'])
        except (KeyError, Registration.DoesNotExist):
            user = None
        context.update({'user': user})
        return context
            
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if not context.get('user', None):
            return Http404            
        return self.render_to_response(context)


