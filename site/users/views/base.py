"""Module defining views related to users."""

from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.http import (Http404, HttpResponseRedirect)
from django.utils.http import urlsafe_base64_decode
from django.views.generic import (CreateView, DeleteView, FormView,
                                  UpdateView, TemplateView)
from users.forms import (UserChangeForm, UserCreationForm)
from users.models import Registration
from users.views.mixins import LoginRequiredMixin

User = get_user_model()


class UserCreation(CreateView):
    """View to create a user account."""
    model = User
    template_name = 'users/user_creation.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('users:user_creation_done')


class UserChange(LoginRequiredMixin, UpdateView):
    """View to modify the logged user account."""
    model = User
    form_class = UserChangeForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_change_done')

    def get_object(self, queryset=None):
        """Returns the user account."""
        return self.request.user if self.request else None


class UserDeletion(LoginRequiredMixin, DeleteView):
    """View to delete (truly deactivate) the logged user account."""
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('users:user_delete_done')

    def get_object(self, queryset=None):
        """Returns the user account."""
        return self.request.user if self.request else None

    def delete(self, request, *args, **kwargs):
        """Sets the ``is_active`` flag to ``False`` and redirects.

        Redirection is done towards the success URL.

        """
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        registration = Registration.objects.create_registration(self.object)
        registration.send_deletion_email()
        return HttpResponseRedirect(self.get_success_url())


class UserActivation(TemplateView):
    """View to activate a user account."""
    template_name = 'users/user_activation_done.html'

    def get_context_data(self, **kwargs):
        """Tries to activate the user account associated to key."""
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
            raise Http404()
        return self.render_to_response(context)

class PasswordResetConfirm(FormView):
    """View to confirm a password reset.

    This view replaces the legacy view ``password_reset_confirm``
    because the former does not return a 404 status when the token and
    the user id doesn't match.

    """
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')
    form_class = SetPasswordForm
    token_generator = default_token_generator

    def get_context_data(self, **kwargs):
        context = super(PasswordResetConfirm, self).get_context_data(**kwargs)
        try:
            uid = urlsafe_base64_decode(self.kwargs['uidb64'])
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        token = self.kwargs['token']
        if user is not None and self.token_generator.check_token(user, token):
            validlink = True
            cls = self.get_form_class()
            if self.request == 'POST':
                form = cls(user, self.request.POST)                
            else:
                form = cls(None)                
        else:
            validlink = False
            form = None
        context.update({'form': form,
                        'validlink': validlink})
        return context            
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if not context.get('validlink', False):
            raise Http404()
        return self.render_to_response(context)

    def post(self, *args, **kwargs):
        return super(PasswordResetConfirm, self).post(*args, **kwargs)
