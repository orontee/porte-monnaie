"""A module for table template tags.
"""
from django import template

register = template.Library()

def get_css_class(field):
    if field is None:
        return
    name = field.__class__.__name__
    if name in ('TextField', 'CharField',
                'IPAddressField', 'GenericIPAddressField',
                'SlugField'):
        return 'text'
    elif name in ('AutoField', 'BigIntegerField',
                  'IntegerField', 'SmallIntegerField',
                  'PositiveIntegerField', 'PositiveSmallIntegerField'):
        return 'integer'
    elif name in ('DecimalField', 'FloatField'):
        return 'float'
    elif name in ('BooleanField', 'NullBooleanField'):
        return 'bool'
    elif name in ('DateField', 'DateTimeField', 'TimeField'):
        return 'datetime'
    elif name == 'CommaSeparatedIntegerField':
        return 'integers'
    elif name == 'EmailField':
        return 'email'
    elif name == 'URLField':
        return 'url'
    return None
    # TODO Fixme

    # TODO Format values

@register.inclusion_tag('tracker/table_row.html',
                        name='table_row')
def do_table_row(obj, field_names):
    datas = []
    fields = dict([(f.name, f) for f in obj._meta.fields
                   if f.name in field_names])
    for name in field_names:
        try:
            dct = {'value': getattr(obj, name)}
        except AttributeError:
            pass
        else:
            styles = (get_css_class(fields.get(name, None)), name)
            css = ' '.join([c for c in styles if c is not None])
            dct.update({'class': css})                        
            datas.append(dct)
            if "float" in styles:
                dct.update({'floatformat': 2})
            elif "text" in styles:
                dct.update({'capfirst': True})                
    return {'datas': datas}


@register.inclusion_tag('tracker/table_header.html',
                        takes_context=True,
                        name='table_header')
def do_table_header(context, field_names):
    datas = []
    fields = context['object_list'].model._meta.fields
    for field in fields:
        if field.name in field_names:
            datas.append({'name': field.name,
                          'verbose_name': field.verbose_name.capitalize(),
                          'help_text': field.help_text.capitalize()})
    datas.sort(key=lambda f: field_names.index(f['name']))
    
    return {'datas': datas}
    
