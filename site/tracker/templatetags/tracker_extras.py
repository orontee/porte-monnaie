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


@register.simple_tag(name='previous_month_url', takes_context=True)
def do_previous_month_url(context):
    """Return the archive url for the previous month.
    """
    return do_archive_url(context['previous_month'], 1,
                          context.get('paginator', None))


@register.simple_tag(name='current_month_url', takes_context=True)
def do_current_month_url(context):
    """Return the archive url for the current month.
    """
    return do_archive_url(datetime.today(), 1,
                          context.get('paginator', None))


@register.simple_tag(name='next_month_url', takes_context=True)
def do_next_month_url(context):
    """Return the archive url for the next month.
    """
    return do_archive_url(context['next_month'], 1,
                          context.get('paginator', None))


def do_archive_url(date, page=1, paginator=None):
    """Return the archive url for the given date.
    """
    url = reverse('tracker:archive')
    template = '{0}?month={1}&year={2}&page={3}'
    paginate_by = None
    if paginator is not None:
        paginate_by = paginator.per_page
        template += '&paginate_by={4}'
    return template.format(url,
                           '{0:%m}'.format(date),
                           '{0:%Y}'.format(date),
                           page, paginate_by)


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
        this_page = '<span class=\'current-page\'>{0}</span>'
        if is_paginated is False:
            return this_page.format(1)
        delta = 2
        elements = []
        template = u"""<a href='{url}' class='page-number' title='{msg}'>{number}</a>"""
        msg = _('Jump to page {0}')

        def add_element(i):
            elements.append(template.format(url=do_archive_url(date, i, paginator),
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
        elements.append(this_page.format(page.number))
        hidden = min(page.number + delta + 1, paginator.num_pages + 1)
        for i in range(page.number + 1, hidden):
            add_element(i)
        if page.number + delta < paginator.num_pages - delta:
            elements.append('...')
        visible = max(hidden, paginator.num_pages - delta + 1)
        for i in range(visible, paginator.num_pages + 1):
            add_element(i)
        return ' '.join(elements)
