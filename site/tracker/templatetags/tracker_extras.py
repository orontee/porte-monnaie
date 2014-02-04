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
    """Build the pagination anchors list.
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
        if is_paginated is False:
            return ''
        anchor = u"""<a href="{url}">{number}</a>"""
        def build_element(i, cls=None):
            lnk = add_page_query(url, i, paginator) if isinstance(i, int) else url
            if cls is not None:
                elt = u"""<li class=""" + cls + '>' + anchor + '</li>'
            else:
                elt = u"""<li>""" + anchor + '</li>'
            return elt.format(url=lnk, number=i)

        elements = ['<ul class="pagination">']
        delta = 2
        hidden = min(page.number - delta - 1, delta) + 1
        for i in range(1, hidden):
            elements.append(build_element(i))
        if page.number - delta - 1 > delta:
            elements.append(build_element('...', 'disabled'))
        visible = max(page.number - delta, 1)
        for i in range(visible, page.number):
            elements.append(build_element(i))
        elements.append(build_element(page.number, 'active'))
        hidden = min(page.number + delta + 1, paginator.num_pages + 1)
        for i in range(page.number + 1, hidden):
            elements.append(build_element(i))
        if page.number + delta < paginator.num_pages - delta:
            elements.append(build_element('...', 'disabled'))
        visible = max(hidden, paginator.num_pages - delta + 1)
        for i in range(visible, paginator.num_pages + 1):
            elements.append(build_element(i))
        elements.append('</ul>')
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
