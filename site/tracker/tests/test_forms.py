"""Tests for forms of tracker application."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import now
from tracker.forms import (ExpenditureForm,
                           MultipleExpenditureForm,
                           PurseShareForm)
from tracker.models import Purse


class ExpenditureFormTest(TestCase):
    """Test form to input an expenditure."""

    def test_amount_equal_zero(self):
        """Check that a form with an amount equal to zero is not valid."""
        data = {'amount': 0,
                'date': now(),
                'description': 'Test',
                'occurrences': '1'}
        form = ExpenditureForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('amount' in form.errors)

    def test_empty_description(self):
        """Check that a form with an description made of whitespace characters
        is not valid.

        """
        data = {'amount': 330,
                'date': now(),
                'description': '  \t',
                'occurrences': '1'}
        form = ExpenditureForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('description' in form.errors)

    def test_valid(self):
        """Test a form with valid data."""
        data = {'amount': 10,
                'date': '2014-05-01',
                'description': 'Test'}
        form = ExpenditureForm(data)
        self.assertTrue(form.is_valid())


class MultipleExpenditureFormTest(TestCase):
    """Test form to input multiple expenditures."""

    def test_missing_occurrence(self):
        """Check that a form without occurrence is not valid."""
        data = {'amount': 10,
                'date': now(),
                'description': 'Test'}
        form = MultipleExpenditureForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('occurrences' in form.errors)

    def test_unexpected_occurrence(self):
        """Check that a form with wrong occurrence is not valid."""
        data = {'amount': 10,
                'date': now(),
                'description': 'Test',
                'occurrences': '7'}
        form = MultipleExpenditureForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('occurrences' in form.errors)

    def test_invalid_date(self):
        """Test that a form with invalid date is not valid."""
        data = {'amount': 10,
                'date': '2015-02-29',
                'description': 'Test',
                'occurrences': '1'}
        form = MultipleExpenditureForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('date' in form.errors)

    def test_valid(self):
        """Test a form with valid data."""
        data = {'amount': 10,
                'date': '2014-05-01',
                'description': 'Test',
                'occurrences': '6'}
        form = MultipleExpenditureForm(data)
        self.assertTrue(form.is_valid())
        self.assertEquals(len(form.other_dates), 5)

    def test_occurences(self):
        """Check that a form with occurence build the expected dates."""
        data = {'amount': 20,
                'date': '2014-07-31',
                'description': 'Test',
                'occurrences': '12'}
        form = MultipleExpenditureForm(data)
        self.assertTrue(form.is_valid())
        date_strings = ['2014-08-31', '2014-09-30', '2014-10-31',
                        '2014-11-30', '2014-12-31', '2015-01-31',
                        '2015-02-28', '2015-03-31', '2015-04-30',
                        '2015-05-31', '2015-06-30']
        self.assertEquals([d.isoformat() for d in form.other_dates],
                          date_strings)


class PurseShareFormTest(TestCase):
    """Test purse sharing form."""
    def setUp(self):
        self.p = Purse.objects.create(name='test')

    def test_nonexistent_user(self):
        """Test that a form with a nonexistent user name is not valid."""
        data = {'user': 'nobody'}
        form = PurseShareForm(data=data, instance=self.p)
        self.assertFalse(form.is_valid())
        self.assertTrue('user' in form.errors)

    def test_user_owning_purse(self):
        """Test that a form with user owning the purse is not valid."""
        User = get_user_model()
        credentials = {'username': 'username',
                       'password': 'password'}
        u = User.objects.create_user(**credentials)
        self.p.users.add(u)
        data = {'user': u.username,
                'name': self.p.name}
        form = PurseShareForm(data, instance=self.p)
        self.assertFalse(form.is_valid())
        self.assertTrue('user' in form.errors)

    def test_valid(self):
        """Test a valid form."""
        User = get_user_model()
        credentials = {'username': 'username',
                       'password': 'password'}
        u = User.objects.create_user(**credentials)
        data = {'user': u.username,
                'name': self.p.name}
        form = PurseShareForm(data, instance=self.p)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data['user'] == u)
