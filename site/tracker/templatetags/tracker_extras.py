"""A module for extra template tags.
"""

from datetime import datetime
from django import template

register = template.Library()

@register.assignment_tag(name='is_current_month')
def check_date_month(date):
    """True iff the given `date` belongs to current month.
    """
    try:
        return datetime.today().month == date.month
    except AttributeError:
        return False
