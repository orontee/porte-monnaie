"""Tests for models of the users application.
"""

from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils.timezone import now
from users.models import Registration

User = get_user_model()


class RegistrationTest(TestCase):
    def setUp(self):
        self.u = User.objects.create(username='username',
                                     password='password',
                                     is_active=False)

    def test_creation(self):
        """Test registration creation.
        """
        r = Registration.objects.create_registration(self.u)
        self.assertEqual(r.user, self.u)

    def test_activate_user(self):
        """Test account activation.
        """
        self.assertEqual(self.u.is_active, False)

        # Missing registration
        with self.assertRaises(Registration.DoesNotExist):
            Registration.objects.activate_user('key')

        # Successful activation
        reg = Registration.objects.create(user=self.u, key='key')
        user = Registration.objects.activate_user('key')
        self.assertEqual(Registration.objects.count(), 0)
        self.assertEqual(user, self.u)
        self.assertEqual(user.is_active, True)

        # Expired registration
        reg = Registration.objects.create(user=self.u, key='key')
        reg.created = now() - timedelta(days=31)
        reg.save()
        user = Registration.objects.activate_user('key')
        self.assertEqual(Registration.objects.count(), 0)
        self.assertEqual(user, None)
        
    def test_expired_registration(self):
        """Test registration expiration.
        """
        reg = Registration.objects.create(user=self.u, key='key')
        self.assertEqual(Registration.expired_objects.count(), 0)
        
        reg.created = now() - timedelta(days=31)
        reg.save()
        self.assertEqual(Registration.expired_objects.count(), 1)

    def test_send_creation_email(self):
        """Test creation email.
        """
        reg = Registration.objects.create(user=self.u, key='key')
        reg.send_creation_email()
        self.assertEqual(len(mail.outbox), 1)

    def test_send_deletion_email(self):
        """Test deletion email.
        """
        reg = Registration.objects.create(user=self.u, key='key')
        reg.send_deletion_email()
        self.assertEqual(len(mail.outbox), 1)
