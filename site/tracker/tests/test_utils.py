"""Tests for tracker utilities."""

from django.test import TestCase
from django.db import connection
from tracker.models import Purse
from tracker.utils import dictfetchall


class DictFetchAllTest(TestCase):
    """Test function that convert cursors to dicts."""

    def test_dictfetchall(self):
        """Check the result of a conversion."""
        Purse.objects.create(name='test1', description='desc1')
        Purse.objects.create(name='test2', description='desc2')
        Purse.objects.create(name='test3', description='desc3')
        cursor = connection.cursor()
        cursor = cursor.execute('SELECT * FROM tracker_purse ORDER BY created;')
        self.maxDiff = None
        dct = dictfetchall(cursor)
        self.assertEqual(len(dct), 3)
        self.assertEqual(dct[0].keys(),
                         ['description', 'created', 'id', 'name'])
        self.assertEqual(dct[0]['description'], 'desc1')
        self.assertEqual(dct[2]['name'], 'test3')
        
        
    
