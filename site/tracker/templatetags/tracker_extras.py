"""A module for extra template tags.
"""

import datetime
from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

register = template.Library()


@register.assignment_tag(name='is_current_month')
def check_date_month(date):
    """``True`` if and only if the ``date`` belongs to current month.
    """
    try:
        return datetime.date.today().month == date.month
    except AttributeError:
        return False


@register.assignment_tag(name='is_current_year')
def check_date_year(date):
    """``True`` if and only if ``date`` belongs to current year.
    """
    try:
        return datetime.date.today().year == date.year
    except AttributeError:
        return False


@register.assignment_tag(name='current_date')
def do_current_date():
    """Return the current date.
    """
    return datetime.date.today()


def add_page_query(url, page=1, paginator=None):
    """Add page query to the given url.
    """
    template = '{0}?page={1}'
    paginate_by = None
    if paginator is not None:
        paginate_by = paginator.per_page
        template += '&paginate_by={2}'
    return template.format(url, page, paginate_by)


@register.simple_tag(name='pagination',
                     takes_context=True)
def do_pagination(context):
    """Build the pagination anchors.
    """
    try:
        is_paginated = context['is_paginated']
        paginator = context['paginator']
        page = context['page_obj']
        url = context['path_info']
    except KeyError:
        raise ImproperlyConfigured('The pagination tag must be used with '
                                   'the QueryPaginationMixin mixin')
    else:
        this_page = '<span class=\'current-page\'>{0}</span>'
        if is_paginated is False:
            return this_page.format(1)
        delta = 2
        elements = []
        template = u"""<a href='{url}' class='page-number'"""
        template += u"""title='{msg}'>{number}</a>"""
        msg = _('Jump to page {0}')

        def add_element(i):
            elements.append(template.format(url=add_page_query(url, i,
                                                               paginator),
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


@register.simple_tag(takes_context=True)
def email_admin(context):
    """Insert an anchor to mail to the first site admin.
    """
    try:
        name, email = settings.ADMINS[0]
    except KeyError:
        raise ImproperlyConfigured('The email_admin tag expects a non-empty '
                                   'ADMINS setting')
    return '<a href="mailto:{0}">{1}</a>'.format(email, name)
