from django.contrib.auth import get_user_model
from django.forms import (ModelForm, CharField, RegexField,
                          PasswordInput, ValidationError)
from django.utils.translation import ugettext_lazy as _
from users.models import Registration
from bootstrap.forms import BootstrapWidgetMixin

User = get_user_model()


class UserCreationForm(BootstrapWidgetMixin, ModelForm):
    """A form that creates a user, with no privileges, from the given
    username, password and email.

    The implementation is copied from django.contrib.auth.forms
    """
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    username = RegexField(label=_("Username"), max_length=30,
                          regex=r'^[\w.@+-]+$',
                          help_text=_("Required. 30 characters or fewer. Letters, digits and "
                                      "@/./+/-/_ only."),
                          error_messages={
                              'invalid': _("This value may contain only letters, numbers and "
                                           "@/./+/-/_ characters.")})
    password1 = CharField(label=_("Password"), widget=PasswordInput)
    password2 = CharField(label=_("Password confirmation"),
                          widget=PasswordInput,
                          help_text=_("Enter the same password as above, "
                                      "for verification."))

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise ValidationError(self.error_messages['duplicate_username'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        if commit:
            user.save()
            registration = Registration.objects.create_registration(user)
            registration.send_creation_email()
        return user


class UserChangeForm(BootstrapWidgetMixin, ModelForm):
    """Form to change a user account.
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'default_purse')
