"""A module for table template tags.

"""

from django import template

register = template.Library()


@register.inclusion_tag('tracker/table_header.html',
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
