from django.forms import EmailField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import (UserChangeForm as OrigUserChangeForm,
                                       UserCreationForm as OrigUserCreationForm)


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

COMPLETE_USER_CREATION_MSG = _(
"""To complete the creation of the user "{user}" with Porte-monnaie,
please visit the following URL:

{url}
""")

# TODO Move to a file
            
            
class UserCreationForm(OrigUserCreationForm):
    """Form to create a user.
    """
    email = EmailField(label=_("Email"), max_length=254)

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_active = False
        if commit:
            user.save()
            user.email_user(_('Complete user creation to Porte-monnaie!').encode('utf-8'),
                            COMPLETE_USER_CREATION_MSG.format(
                                user=user.username, url="???").encode('utf-8'))
        return user
    
