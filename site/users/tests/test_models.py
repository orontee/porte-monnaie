"""Tests for models of the users application.
"""

from django.contrib.auth import get_user_model
from django.utils.unittest import TestCase
from users.models import Registration

User = get_user_model()


class RegistrationTest(TestCase):
    def setUp(self):
        self.u = User.objects.create_user(username='username',
                                          password='password')
        self.u.save()

    def test_creation(self):
        """
        Check that key and user are set.
        """
        r = Registration.objects.create_registration(self.u)
        self.assertEqual(r.user, self.u)
