from django.conf import settings
from django.conf.urls import (patterns, include, url)
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns('',
                       url(r'^tracker/', include('tracker.urls',
                                                 namespace='tracker',
                                                 app_name='tracker')),
                       url(r'^$', RedirectView.as_view(
                           url=reverse_lazy('tracker:home'))))

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('', url(
        r'^__debug__/', include(debug_toolbar.urls)),)
