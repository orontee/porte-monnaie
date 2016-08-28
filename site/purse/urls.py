from django.conf.urls import (include, url)
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    url(r'^tracker/', include('tracker.urls',
                              namespace='tracker',
                              app_name='tracker')),
    url(r'^$', RedirectView.as_view(
        permanent=True,
        url=reverse_lazy('tracker:home'))),
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(
        packages=['tracker']),
        name='javascript-catalog')]

# if settings.DEBUG:
#     if settings.DEBUG_TOOLBAR:
#         import debug_toolbar
#         urlpatterns += [url(
#             r'^__debug__/', include(debug_toolbar.urls))]
