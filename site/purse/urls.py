from django.conf.urls import (patterns, include, url)
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns('',
                       url(r'^tracker/', include('tracker.urls', 
                                                 namespace='tracker', 
                                                 app_name='tracker')),
                       url(r'^$', RedirectView.as_view(
                           url=reverse_lazy('tracker:home'))))
