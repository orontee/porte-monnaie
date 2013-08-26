from django.forms import EmailField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import (UserChangeForm as OrigUserChangeForm,
                                       UserCreationForm as OrigUserCreationForm)
from register.models import Registration


class UserChangeForm(OrigUserChangeForm):
    """Form to change a user data.
    """
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        suppress = ('password', 'is_active', 'is_superuser', 'is_staff',
                    'user_permissions', 'last_login', 'date_joined',
                    'groups')
        for k in suppress:
            del self.fields[k]


class UserCreationForm(OrigUserCreationForm):
    """Form to create a user.
    """
    email = EmailField(label=_("Email"), max_length=254)

    def save(self, commit=True):
        """Create inactive ``User`` model and its associated ``Registration``
        model.
        """
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_active = False
        
        if commit:
            user.save()
            registration = Registration.objects.create_registration(user)
            registration.send()
        return user
    
