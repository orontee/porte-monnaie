"""Tests for models of tracker application.
"""

from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import now
from tracker.models import (Purse, Expenditure)

User = get_user_model()


class PurseTest(TestCase):
    """Test purses.
    """
    def test_usernames(self):
        """Test usernames.
        """        
        u1 = User.objects.create(username='first',
                                 password='password',
                                 is_active=False)
        u2 = User.objects.create(username='other',
                                 first_name='second',
                                 password='password',
                                 is_active=False)
        u1.save()
        u2.save()
        p = Purse.objects.create(name='test')
        p.save()
        p.users.add(u1, u2)
        names = [n.strip() for n in p.usernames().split(',')]
        self.assertIn('first', names)
        self.assertIn('second', names)


class ExpenditureTest(TestCase):
    """Test expenditures.
    """
    def setUp(self):
        self.u = User.objects.create(username='test',
                                     password='password',
                                     is_active=False)
        self.u.save()
        self.p = Purse.objects.create(name='test')
        self.p.save()
        self.p.created -= timedelta(days=5)
        self.p.save()
        self.p.users.add(self.u)

    def test_is_editable(self):
        """Test expenditure edition.
        """
        e = Expenditure.objects.create(amount=100,
                                       date=now(),
                                       description='test',
                                       author=self.u,
                                       purse=self.p)        
        e.save()
        self.assertTrue(e.is_editable())

        e.created -= timedelta(days=3)
        e.save()
        self.assertFalse(e.is_editable())
        
        
