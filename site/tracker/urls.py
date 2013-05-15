"""Module defining the url patterns.

All the url names defined here are accessible from the tracker
namespace.
"""

from django.conf.urls import (patterns, url)
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from tracker.views import (ExpenditureAdd, ExpenditureList)

urlpatterns = patterns('tracker.views',
                       url(r'^$', RedirectView.as_view(
                           url=reverse_lazy('tracker:list')),
                           name='home'))

urlpatterns += patterns('tracker.views',
                       url(r'^add_expenditure/$',
                           ExpenditureAdd.as_view(),
                           name='add'),
                       url(r'^expenditures/$',
                           ExpenditureList.as_view(),
                           name='list'))

urlpatterns += patterns('',
                        url(r'^login/$', 'django.contrib.auth.views.login', 
                            {'template_name': 'accounts/login.html', 
                             'authentication_form': AuthenticationForm },
                            name='login'),
                        url(r'^logout/$', 'django.contrib.auth.views.logout',
                            {'template_name': 'accounts/logged_out.html'},
                            name='logout'))
