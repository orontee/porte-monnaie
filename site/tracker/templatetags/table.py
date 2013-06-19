"""A module for table template tags.
"""

from django import template

register = template.Library()


@register.inclusion_tag('tracker/header.html',
                        name='table_header',
                        takes_context=True)
def do_header(context, field_names):
    """Include a template for a table header build from the given fields.

    The columns order is the same as the one in field_names.
    """
    datas = []
    fields = context['object_list'].model._meta.fields
    for field in fields:
        if field.name in field_names:
            datas.append({'name': field.name,
                          'verbose_name': field.verbose_name,
                          'help_text': field.help_text})
    datas.sort(key=lambda f: field_names.index(f['name']))
    return {'header_datas': datas}


@register.inclusion_tag('tracker/footer.html',
                        name='table_footer',
                        takes_context=True)
def do_footer(context, field_names):
    """Include a template for a table footer build from the given fields.
    """
    return context.update({'column_count': len(field_names)})
    
@register.simple_tag(name='value')
def do_getattr(obj, name):
    """Return the attribute of obj named name, or None if obj has no such
    attribute.
    """
    return getattr(obj, name, None)
