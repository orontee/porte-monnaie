"""Tests for models of tracker application."""

from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.test import TestCase
from django.utils.timezone import now
from tracker.models import (Expenditure, Purse, Tag)

User = get_user_model()


class PurseTest(TestCase):
    """Test purses."""
    def test_usernames(self):
        """Test usernames."""
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
    """Test expenditures."""
    def setUp(self):
        self.u = User.objects.create(username='test',
                                     password='password',
                                     is_active=False)
        self.p = Purse.objects.create(name='test')
        self.p.created -= timedelta(days=5)
        self.p.users.add(self.u)

    def test_is_editable(self):
        """Test expenditure edition."""
        e = Expenditure.objects.create(amount=100,
                                       date=now(),
                                       description='test',
                                       author=self.u,
                                       purse=self.p)
        self.assertTrue(e.is_editable())

        e.created -= timedelta(days=3)
        e.save()
        self.assertFalse(e.is_editable())


class TagManagerTest(TestCase):
    """Test tag manager."""
    def test_get_tag_names(self):
        """Test tag names extraction."""
        desc = "if HUMAN then ?"
        names = Tag.objects.get_tag_names(desc)
        self.assertEquals(names, ['human', 'then'])

    def test_update_from(self):
        """Test tag update."""
        u = User.objects.create(username='test',
                                password='password',
                                is_active=False)
        p = Purse.objects.create(name='test')
        p.users.add(u)
        description = "one two two   three a e i"
        e = Expenditure(amount=100,
                        date=now(),
                        description=description,
                        author=u,
                        purse=p)
        e.save()
        qs = p.tag_set.order_by('id')
        qs = qs.annotate(weight=Count('expenditures'))
        tags = [d for d in qs.values('name', 'weight')]
        expecting = [{'name': u'one', 'weight': 1},
                     {'name': u'two', 'weight': 1},
                     {'name': u'three', 'weight': 1}]
        self.assertEqual(tags, expecting)

        e = Expenditure(amount=100,
                        date=now(),
                        description='two',
                        author=u,
                        purse=p)
        e.save()
        qs = p.tag_set.order_by('id')
        qs = qs.annotate(weight=Count('expenditures'))
        tags = [d for d in qs.values('name', 'weight')]
        expecting = [{'name': u'one', 'weight': 1},
                     {'name': u'two', 'weight': 2},
                     {'name': u'three', 'weight': 1}]
        self.assertEqual(tags, expecting)

        q = Purse.objects.create(name='other')
        q.users.add(u)
        e = Expenditure(amount=100,
                        date=now(),
                        description='four five',
                        author=u,
                        purse=q)
        e.save()
        qs = p.tag_set.order_by('id')
        self.assertEqual(qs.count(), 3)
