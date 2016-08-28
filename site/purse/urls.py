from django.conf import settings
from django.conf.urls import (include, url)
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy
from django.views.i18n import javascript_catalog

js_info_dict = {
    'packages': ('tracker',),
}

urlpatterns = [
    url(r'^tracker/', include('tracker.urls',
                              namespace='tracker',
                              app_name='tracker')),
    url(r'^$', RedirectView.as_view(
        permanent=True,
        url=reverse_lazy('tracker:home'))),
    url(r'^jsi18n/$', javascript_catalog,
        js_info_dict)]

# if settings.DEBUG:
#     if settings.DEBUG_TOOLBAR:
#         import debug_toolbar
#         urlpatterns += [url(
#             r'^__debug__/', include(debug_toolbar.urls))]
