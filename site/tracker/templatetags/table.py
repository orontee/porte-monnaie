"""A module for table template tags.
"""

from django import template

register = template.Library()

@register.inclusion_tag('tracker/table.html', name='table')
def do_table(object_list, field_names):
    hdatas, rdatas = [], []
    fields = object_list.model._meta.fields
    for field in fields:
        if field.name in field_names:
            hdatas.append({'name': field.name,
                           'verbose_name': field.verbose_name,
                           'help_text': field.help_text})
    hdatas.sort(key=lambda f: field_names.index(f['name']))
    for obj in object_list:
        data = []
        for name in field_names:
            try:            
                dct = {'value': getattr(obj, name),
                       'class': name}
            except AttributeError:
                pass
            else:
                data.append(dct)
        rdatas.append(data)
    return {'header_datas': hdatas,
            'row_datas': rdatas}
    
