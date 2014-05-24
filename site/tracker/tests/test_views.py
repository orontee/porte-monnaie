"""Tests for views of tracker application.
"""

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from tracker.models import Purse

User = get_user_model()


class HomeTest(TestCase):
    """Test home view.
    """
    def setUp(self):
        self.url = reverse('tracker:home')

    def test_get(self):
        """Get home view.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


def create_user(**kwargs):
    """Create a user.
    """
    u = User.objects.create_user(**kwargs)
    u.save()
    return u


def create_purse(user=None, **kwargs):
    """Create a purse.

    If user is not None, add it to the created purse.
    """
    p = Purse.objects.create(**kwargs)
    p.save()
    if user is not None:
        p.users.add(user)
    return p
    

class ExpenditureAddTest(TestCase):
    """Test expenditure add view.
    """
    def setUp(self):
        self.url = reverse('tracker:add')

    def test_get_non_authentified(self):
        """Get page while no user is authentified.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        url = 'http://testserver/tracker/'
        self.assertEqual(response.url, url)
        
    def test_get_authentified_without_purse(self):
        """Get page while user is authentified but has no purse.
        """
        credentials = {'username': 'username',
                       'password': 'password'}
        create_user(**credentials)
        self.client.login(**credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        url = 'http://testserver/tracker/purses/create/'
        self.assertEqual(response.url, url)

    def test_get_authentified_without_default_purse(self):
        """Get page while user is authentified but has no default 
        purse.
        """
        credentials = {'username': 'username',
                       'password': 'password'}
        u = create_user(**credentials)
        self.client.login(**credentials)
        create_purse(u)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(u.default_purse, p)
        # Check messages

    def test_post_authentified_with_default_purse(self):
        """Get page while user is authentified and has a default purse.
        """
        credentials = {'username': 'username',
                       'password': 'password'}
        u = create_user(**credentials)
        self.client.login(**credentials)
        p = create_purse(u)
        u.default_purse = p
        u.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        token = response.cookies['csrftoken'].value
        data = {'amount': 100,
                'date': '24/05/2014',
                'description': 'expenditure description',
                'occurrences': '1',
                'csrftoken': token}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        url = 'http://testserver/tracker/expenditures/'
        self.assertEqual(response.url, url)
        self.assertEqual(u.expenditure_set.count(), 1)

