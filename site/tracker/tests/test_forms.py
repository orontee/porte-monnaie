"""Tests for forms of tracker application."""

from django.test import TestCase
from django.utils.timezone import now
from tracker.forms import (ExpenditureForm, MultipleExpenditureForm)
from tracker.models import Expenditure


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
        """Test that a form with invalid computed dates is not valid."""
        data = {'amount': 10,
                'date': '2014-05-31',
                'description': 'Test',
                'occurrences': '2'}
        form = MultipleExpenditureForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('occurrences' in form.errors)

    def test_valid(self):
        """Test a form with valid data."""
        data = {'amount': 10,
                'date': '2014-05-01',
                'description': 'Test',
                'occurrences': '6'}
        form = MultipleExpenditureForm(data)
        self.assertTrue(form.is_valid())
        self.assertEquals(len(form.other_dates), 5)
