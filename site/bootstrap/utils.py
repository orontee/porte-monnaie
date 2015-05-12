"""Module gathering utilities."""


def update_widgets(form):
    """Make sure that the form widgets have the bootstrap classes."""
    for f in form.fields.values():
        w = f.widget
        classes = w.attrs.get('class', '').split()
        candidates = ['form-control', 'form-control-static']
        if all([cls not in candidates for cls in classes]):
            value = 'form-control' + ' '.join(classes)
            w.attrs.update({'class': value})
