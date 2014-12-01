"""Tests for users forms."""

from django.core import mail
from django.test import TestCase
from users.models import User
from users.forms import UserCreationForm


class UserCreationFormTest(TestCase):
    """Test form to create a user account."""

    def test_valid(self):
        """Check a valid form."""
        data = {'username': 'test',
                'email': 'test@example.com',
                'password1': 'test',
                'password2': 'test'}
        form = UserCreationForm(data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_password_missmatch(self):
        """Check that a form with different passwords is not valid."""
        data = {'username': 'test',
                'email': 'test@example.com',
                'password1': 'test1',
                'password2': 'test2'}
        form = UserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('password2' in form.errors)

    def test_dupplicated_username(self):
        """Check that a form with an existing username is not valid."""
        User.objects.create(username='test').save()
        data = {'username': 'test',
                'email': 'test@example.com',
                'password1': 'test',
                'password2': 'test'}
        form = UserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('username' in form.errors)


# Local Variables:
# compile-command: "source share/setup_debug_env && make test"
# End:
