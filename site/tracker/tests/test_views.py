"""Tests for views of tracker application."""

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from tracker.models import (Expenditure, Purse)

User = get_user_model()


class HomeTest(TestCase):
    """Test home view."""
    def setUp(self):
        self.url = reverse('tracker:home')

    def test_get(self):
        """Get home view."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


def create_user(**kwargs):
    """Create a user."""
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


def create_expenditure(**kwargs):
    """Create an expenditure."""
    e = Expenditure.objects.create(**kwargs)
    e.save()
    return e


class ExpenditureAddTest(TestCase):
    """Test expenditure add view."""
    def setUp(self):
        self.url = reverse('tracker:add')

    def test_get_non_authentified(self):
        """Get page while no user is authentified."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        url = 'http://testserver/tracker/login?next=/tracker/expenditures/add/'
        self.assertEqual(response.url, url)

    def test_get_authentified_without_purse(self):
        """Get page while user is authentified but has no purse.

        """
        credentials = {'username': 'username',
                       'password': 'password'}
        create_user(**credentials)
        self.client.login(**credentials)
        response = self.client.get(self.url)
        expected_url = 'http://testserver/tracker/purses/create/'
        self.assertRedirects(response, expected_url)

    def test_get_authentified_without_default_purse(self):
        """Get page while user is authentified but has no default purse."""
        credentials = {'username': 'username',
                       'password': 'password'}
        u = create_user(**credentials)
        self.client.login(**credentials)
        create_purse(u)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(u.default_purse, p)
        # TODO Check messages

    def test_post(self):
        """Get page then post."""
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

    def test_post_and_save_other(self):
        """Get page then post and save other."""
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
        data = {'amount': 300,
                'date': '25/05/2014',
                'description': 'other expenditure description',
                'occurrences': '1',
                'save_other': True,
                'csrftoken': token}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        url = 'http://testserver'
        url += self.url + '?date=2014-05-25'
        self.assertEqual(response.url, url)
        self.assertEqual(u.expenditure_set.count(), 1)

    def test_post_with_multiple_occurence(self):
        """Get page then post to create multiple expenditures."""
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
                'occurrences': '3',
                'csrftoken': token}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        url = 'http://testserver/tracker/expenditures/'
        self.assertEqual(response.url, url)
        self.assertEqual(u.expenditure_set.count(), 3)


class ExpenditureDeleteTest(TestCase):
    """Test expenditure delete view."""
    def setUp(self):
        credentials = {'username': 'username',
                       'password': 'password'}
        u = create_user(**credentials)
        p = create_purse(u)
        u.default_purse = p
        u.save()
        e = Expenditure.objects.create(amount=199,
                                       author=u,
                                       purse=p)
        self.url = reverse('tracker:delete', kwargs={'pk': e.pk})

    def test_get_non_authentified(self):
        """Get page while no user is authentified."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        expected_url = 'http://testserver/tracker/login?next='
        expected_url += self.url
        self.assertEqual(response.url, expected_url)

    def test_get_authentified(self):
        """Get page then delete resource while user is authentified."""
        credentials = {'username': 'username',
                       'password': 'password'}
        self.client.login(**credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expenditure.objects.count(), 0)
        self.assertEqual(response.url,
                         'http://testserver/tracker/expenditures/')


class ExpenditureUpdateTest(TestCase):
    """Test expenditure update view."""
    def setUp(self):
        credentials = {'username': 'username',
                       'password': 'password'}
        self.u = create_user(**credentials)
        p = create_purse(self.u)
        self.u.default_purse = p
        self.u.save()
        e = Expenditure.objects.create(amount=199,
                                       author=self.u,
                                       purse=p)
        self.url = reverse('tracker:update', kwargs={'pk': e.pk})

    def test_get_non_authentified(self):
        """Get page while no user is authentified."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        expected_url = 'http://testserver/tracker/login?next='
        expected_url += self.url
        self.assertEqual(response.url, expected_url)

    def test_get_authentified(self):
        """Get page then update resource while user is authentified."""
        credentials = {'username': 'username',
                       'password': 'password'}
        self.client.login(**credentials)
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
        self.assertEqual(self.u.expenditure_set.count(), 1)
        e = self.u.expenditure_set.all()[0]
        self.assertEqual(e.amount, 100)
        self.assertEqual(e.description, 'expenditure description')
        self.assertEqual(len(e.tag_set.all()), 2)


class PurseCreationTest(TestCase):
    """Test purse creation view."""

    def setUp(self):
        self.url = reverse('tracker:purse_creation')

    def test_get_non_authentified(self):
        """Get page while no user is authentified."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        url = 'http://testserver/tracker/login?next=/tracker/purses/create/'
        self.assertEqual(response.url, url)

    def test_get_authentified(self):
        """Get page for authentified user."""
        credentials = {'username': 'username',
                       'password': 'password'}
        create_user(**credentials)
        self.client.login(**credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_first_purse(self):
        """Get page then post to create a first purse."""
        credentials = {'username': 'username',
                       'password': 'password'}
        u = create_user(**credentials)
        self.client.login(**credentials)
        response = self.client.get(self.url)
        token = response.cookies['csrftoken'].value
        data = {'name': 'Tes',
                'description': 'The purse description',
                'csrftoken': token}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        url = 'http://testserver/tracker/expenditures/'
        self.assertEqual(response.url, url)
        self.assertEqual(u.purse_set.count(), 1)

    def test_post(self):
        """Get page then post."""
        credentials = {'username': 'username',
                       'password': 'password'}
        u = create_user(**credentials)
        create_purse(u)
        self.client.login(**credentials)
        response = self.client.get(self.url)
        token = response.cookies['csrftoken'].value
        data = {'name': 'Second purse',
                'description': 'The purse description',
                'csrftoken': token}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        url = 'http://testserver/tracker/purses/'
        self.assertEqual(response.url, url)
        u = User.objects.get(username='username')
        self.assertEqual(u.purse_set.count(), 2)
        self.assertEqual(u.default_purse.name, 'Second purse')


class PurseUpdateTest(TestCase):
    """Test purse update view."""

    def setUp(self):
        self.credentials = {'username': 'username',
                            'password': 'password'}
        u = create_user(**self.credentials)
        create_purse(u)
        self.url = reverse('tracker:purse_update', kwargs={'pk': u.pk})

    def test_get_non_authentified(self):
        """Get page while no user is authentified."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        url = 'http://testserver/tracker/logout/'
        self.assertEqual(response.url, url)

    def test_get_authentified(self):
        """Get page for authentified user."""
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_authentified_not_in_purse(self):
        """Get page for authentified user not in purse."""
        credentials = {'username': 'other',
                       'password': 'password'}
        create_user(**credentials)
        self.client.login(**credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        url = 'http://testserver/tracker/logout/'
        self.assertEqual(response.url, url)

    def test_post(self):
        """Post a new purse name."""
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        token = response.cookies['csrftoken'].value
        data = {'name': 'New purse name',
                'csrftoken': token}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        url = 'http://testserver/tracker/purses/'
        self.assertEqual(response.url, url)
        u = User.objects.get(username='username')
        self.assertTrue(u.purse_set.values_list('name', flat=True),
                        ['New purse name'])


class ExpenditureFilteredListTest(TestCase):
    """Test expenditure filtered list."""

    def setUp(self):
        self.credentials = {'username': 'username',
                            'password': 'password'}
        create_user(**self.credentials)
        self.url = reverse('tracker:expenditure-search')

    def test_get_non_authentified(self):
        """Get page while no user is authentified."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        url = 'http://testserver/tracker/login'
        url += '?next=/tracker/expenditures/search/'
        self.assertEqual(response.url, url)

    def test_get_authentified_without_purse(self):
        """Get page while user is authentified but has no purse."""
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        expected_url = 'http://testserver/tracker/purses/create/'
        self.assertRedirects(response, expected_url)

    def test_get_authentified_without_default_purse(self):
        """Get page while user is authentified but has no default purse."""
        self.client.login(**self.credentials)
        u = User.objects.get(username='username')
        create_purse(u)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(u.default_purse, p)
        # TODO Check messages

    def test_get(self):
        """Get page for authentified user with purse."""
        self.client.login(**self.credentials)
        u = User.objects.get(username='username')
        p = create_purse(u)
        desc = 'Uniquedesc'
        # REMARK First letter must be in uppercase
        create_expenditure(**{'amount': 100,
                              'date': '2014-12-2',
                              'description': desc,
                              'author': u,
                              'purse': p})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, desc)

    def test_get_single_keyword(self):
        """Get page for a single filter keyword."""
        self.client.login(**self.credentials)
        u = User.objects.get(username='username')
        p = create_purse(u)
        create_expenditure(**{'amount': 100,
                              'date': '2014-12-2',
                              'description': 'firstdesc uniqueterm',
                              'author': u,
                              'purse': p})
        create_expenditure(**{'amount': 100,
                              'date': '2014-12-2',
                              'description': 'otherdesc',
                              'author': u,
                              'purse': p})
        response = self.client.get(self.url + '?filter=firstdesc')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'uniqueterm')
        self.assertNotContains(response, 'otherterm')

    def test_get_num_keyword(self):
        """Get page for a single filter keyword convertible to float."""
        self.client.login(**self.credentials)
        u = User.objects.get(username='username')
        p = create_purse(u)
        create_expenditure(**{'amount': 120.45,
                              'date': '2014-12-2',
                              'description': 'firstdesc uniqueterm',
                              'author': u,
                              'purse': p})
        create_expenditure(**{'amount': 100,
                              'date': '2014-12-2',
                              'description': 'otherdesc',
                              'author': u,
                              'purse': p})
        create_expenditure(**{'amount': 120.45,
                              'date': '2014-11-7',
                              'description': 'lastdesc',
                              'author': u,
                              'purse': p})
        response = self.client.get(self.url + '?filter=120.45')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'uniqueterm')
        self.assertNotContains(response, 'otherdesc')
        self.assertContains(response, 'Lastdesc')
        # REMARK Note that descriptions are capitalized

    def test_get_multiple_keywords(self):
        """Get page for multiple filter keywords."""
        self.client.login(**self.credentials)
        u = User.objects.get(username='username')
        p = create_purse(u)
        create_expenditure(**{'amount': 120.45,
                              'date': '2014-12-2',
                              'description': 'firstdesc uniqueterm',
                              'author': u,
                              'purse': p})
        create_expenditure(**{'amount': 100,
                              'date': '2014-12-2',
                              'description': 'otherdesc',
                              'author': u,
                              'purse': p})
        create_expenditure(**{'amount': 120.45,
                              'date': '2014-12-7',
                              'description': 'lastdesc',
                              'author': u,
                              'purse': p})
        response = self.client.get(self.url + '?filter=120.45+unique')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'uniqueterm')
        self.assertNotContains(response, 'otherterm')
        self.assertNotContains(response, 'lastdesc')


class PurseDeletionTest(TestCase):
    """Test purse deletion view."""

    def setUp(self):
        self.credentials = {'username': 'username',
                            'password': 'password'}
        u = create_user(**self.credentials)
        p = create_purse(u)
        self.url = reverse('tracker:purse_delete',
                           kwargs={'pk': p.pk})

    def test_get_non_authentified(self):
        """Get page while no user is authentified."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        url = 'http://testserver/tracker/login?next=/tracker/purses/delete/1/'
        self.assertEqual(response.url, url)

    def test_get_authentified(self):
        """Get page for authentified user."""
        self.client.login(**self.credentials)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Purse.objects.count(), 0)
