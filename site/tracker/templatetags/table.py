"""A module for table template tags.
"""

from django import template
from tracker.templatetags.tracker_extras import do_pagination

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
def do_footer(context, field_names):
    """Include a template for a table footer build from the given fields.
    """
    pagination = do_pagination(context)
    page_choices = context.get('page_choices', [15, 25, 50])
    # TODO Add a choice for all pages
    # TODO No default here, better raise an exception
    try:
        paginator = context['paginator']
    except KeyError:
        paginator = None
    per_page = paginator.per_page if paginator else None
    return {'column_count': len(field_names),
            'pagination': pagination,
            'per_page': per_page,
            'page_choices': page_choices,
            'params': context.get('params', None)}


# @register.simple_tag(name='value')
# def do_getattr(obj, name):
#     """Return the attribute of obj named name, or None if obj has no such
#     attribute.
#     """
#     return getattr(obj, name, None)
