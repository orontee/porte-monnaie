"""A module for extra template tags.
"""

from datetime import datetime
from django import template
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

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
def do_archive_url(date, page=1):
    """Return the archive url for the given date.
    """
    template = '{0}?month={1}&year={2}&page={3}'
    url = reverse('tracker:archive')
    return template.format(url,
                           '{0:%m}'.format(date),
                           '{0:%Y}'.format(date),
                           page)


@register.simple_tag(name='pagination',
                     takes_context=True)
def do_pagination(context):
    """Build the pagination anchors.
    """
    try:
        is_paginated = context['is_paginated']
        paginator = context['paginator']
        page = context['page_obj']
        date = context['month']
    except KeyError:
        return ""
        # TODO Raise a user exception to signify a wrong use of the
        # tag
    else:
        if is_paginated is False:
            return '<span class=\'current-page\'>{0}</span>'.format(1)
        delta = 2
        elements = []
        template = u"""<a href='{url}' class='page-number' title='{msg}'>{number}</a>"""
        msg = _('Jump to page {0}')
        def add_element(i):
            elements.append(template.format(url=do_archive_url(date, i),
                                            msg=msg.format(i),
                                            number=i))
        hidden = min(page.number - delta - 1, delta) + 1
        for i in range(1, hidden):
            add_element(i)
        if page.number - delta - 1 > delta:
            elements.append('...')
        visible = max(page.number - delta, 1)
        for i in range(visible, page.number):
            add_element(i)
        elements.append(
            '<span class=\'current-page\'>{0}</span>'.format(page.number))
        hidden = min(page.number + delta + 1, paginator.num_pages + 1)
        for i in range(page.number + 1, hidden):
            add_element(i)
        if page.number + delta < paginator.num_pages - delta:
            elements.append('...')
        visible = max(hidden, paginator.num_pages - delta + 1)
        for i in range(visible, paginator.num_pages + 1):
            add_element(i)
        return ' '.join(elements)
