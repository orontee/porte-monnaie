"""Bootstrap forms."""

from django.forms.widgets import HiddenInput
from django.utils.encoding import force_text
from django.utils.html import format_html

from bootstrap.utils import update_widgets


class BootstrapWidgetMixin(object):
    """Mixin to build forms with Bootstrap classes."""

    def __init__(self, *args, **kwargs):
        """Call ``update_widgets``."""
        super(BootstrapWidgetMixin, self).__init__(*args, **kwargs)
        update_widgets(self)


class StaticControl(HiddenInput):
    """To place plain text next to a form label."""

    def render(self, name, value, attrs=None):
        """Use the .form-control-static class on a <p>."""
        legacy = super(StaticControl, self).render(name, value, attrs)
        if value is None:
            value = ''
        final_value = force_text(self._format_value(value))
        static = format_html('<p class="form-control-static">\r\n{0}</p>',
                             final_value)
        return legacy + static
