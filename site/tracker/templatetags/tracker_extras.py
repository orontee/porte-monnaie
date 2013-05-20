"""A module for extra template tags.
"""

from datetime import datetime
from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.assignment_tag(name='is_current_month')
def check_date_month(date):
    """True iff the given `date` belongs to current month.
    """
    try:
        return datetime.today().month == date.month
    except AttributeError:
        return False

@register.simple_tag(name='archive_url')
def do_archive_url(date):
    """Return the archive url for the given date.
    """
    return '{0}?month={1}&year={2}'.format(reverse('tracker:archive'),
                                           '{0:%m}'.format(date),
                                           '{0:%Y}'.format(date))
