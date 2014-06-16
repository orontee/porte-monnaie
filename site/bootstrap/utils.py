def update_widgets(form):
    """Make sure that the form widgets have the bootstrap classes.
    """
    for f in form.fields.values():
        w = f.widget
        w.attrs.update({'class': 'form-control'})
