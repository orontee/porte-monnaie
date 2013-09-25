"""A module for extra template tags.
"""

import datetime
from django import template
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

register = template.Library()


@register.assignment_tag(name='is_current_month')
def check_date_month(date):
    """`True` if and only if the `date` belongs to current month.
    """
    try:
        return datetime.date.today().month == date.month
    except AttributeError:
        return False


@register.assignment_tag(name='is_current_year')
def check_date_year(date):
    """`True` if and only if `date` belongs to current year.
    """
    try:
        return datetime.date.today().year == date.year
    except AttributeError:
        return False


@register.simple_tag(name='previous_month_url', takes_context=True)
def do_previous_month_url(context):
    """Return the archive url for the previous month.
    """
    return do_archive_url(context['previous_month'])


@register.simple_tag(name='next_month_url', takes_context=True)
def do_next_month_url(context):
    """Return the archive url for the next month.
    """
    return do_archive_url(context['next_month'])


@register.simple_tag(name='current_month_url')
def do_current_month_url():
    """Return the archive url for the current month.
    """
    return do_archive_url(datetime.date.today())


@register.simple_tag(name='month_url')
def do_month_url(month):
    """Return the archive url for the given month.
    """
    return do_archive_url(datetime.date(datetime.date.today().year,
                                        month, 1))


@register.simple_tag(name='current_year_url')
def do_current_year_url():
    """Return the summary url for the current year.
    """
    return do_summary_url(datetime.date.today())


def do_archive_url(date):
    """Return the archive url for the given date.
    """
    kwargs = {'month': '{0:%m}'.format(date),
              'year': '{0:%Y}'.format(date)}
    return reverse('tracker:archive', kwargs=kwargs)


def do_summary_url(date):
    """Return the summary url for the given date.
    """
    kwargs = {'year': '{0:%Y}'.format(date)}
    return reverse('tracker:summary', kwargs=kwargs)


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
        raise ImproperlyConfigured("The pagination tag must be used with "
                                   "the QueryPaginationMixin mixin")
    else:
        this_page = '<span class=\'current-page\'>{0}</span>'
        if is_paginated is False:
            return this_page.format(1)
        delta = 2
        elements = []
        template = u"""<a href='{url}' class='page-number' title='{msg}'>{number}</a>"""
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
