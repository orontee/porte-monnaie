from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, UpdateView)
from register.forms import (UserChangeForm, UserCreationForm)


class UserChange(UpdateView):
    """View to modify user data.
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
    """View to create a user.
    """
    model = get_user_model()
    template_name = 'register/user_creation_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register:user_creation_done')

