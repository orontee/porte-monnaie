from django.conf.urls import (patterns, include, url)
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm

urlpatterns = patterns('',
                       url(r'^tracker/', include('tracker.urls', namespace='tracker', app_name='tracker')),
                       url(r'^$', RedirectView.as_view(url=reverse_lazy('tracker:home'))))

urlpatterns += patterns('',
                        url(r'^login/$', 'django.contrib.auth.views.login', 
                            {'template_name': 'accounts/login.html', 
                             'authentication_form': AuthenticationForm },
                            name='login'))
