"""Bootstrap forms."""


from bootstrap.utils import update_widgets


class BootstrapWidgetMixin(object):
    """Mixin to build forms with Bootstrap classes."""
    def __init__(self, *args, **kwargs):
        """Call ``update_widgets``."""
        super(BootstrapWidgetMixin, self).__init__(*args, **kwargs)
        update_widgets(self)
