"""A module for table template tags.
"""

from django import template
from tracker.templatetags.tracker_extras import do_pagination
from django.core.exceptions import ImproperlyConfigured

register = template.Library()


@register.inclusion_tag('tracker/header.html',
                        name='table_header',
                        takes_context=True)
def do_header(context, field_names):
    """Include a template for a table header build from the given fields.

    The columns order is the same as the one in field_names.
    """
    datas = []
    model = context['object_list'].model
    fields = dict([(f.name, f) for f in model._meta.fields])
    for name in field_names:
        field = None
        try:
            field = fields[name]
        except KeyError:
            try:
                field = getattr(model, name).field
            except AttributeError:
                pass
        if field:
            datas.append({'name': field.name,
                          'verbose_name': field.verbose_name})
    return {'header_datas': datas}


@register.inclusion_tag('tracker/footer.html',
                        name='table_footer',
                        takes_context=True)
def do_footer(context, field_names=None):
    """Include a template for a table footer.
    """
    if not field_names:
        try:
            field_names = context['field_names']
        except KeyError:
            raise ImproperlyConfigured("Context or tag must set field names")
    dct = {'column_count': len(field_names),
           'params': context.get('params', None)}
    paginator = context.get('paginator', None)
    if not paginator:
        raise ImproperlyConfigured("Expecting a paginator in context")
    dct.update({'pagination': do_pagination(context),
                'per_page': paginator.per_page,
                'page_choices': context.get(
                    'page_choices', [15, 25, 50])})
    return dct
