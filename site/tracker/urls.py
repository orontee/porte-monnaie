"""Module defining the url patterns.

All the url names defined here are accessible from the tracker
namespace.
"""

from datetime import datetime
from django.conf.urls import (patterns, url)
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.forms import (AuthenticationForm,
                                       PasswordChangeForm)
from tracker.views import (ExpenditureAdd,
                           ExpenditureMonthList)

urlpatterns = patterns('tracker.views',
                       url(r'^$', RedirectView.as_view(
                           url=reverse_lazy('tracker:list')),
                           name='home'))

urlpatterns += patterns('tracker.views',
                        url(r'^add_expenditure/$',
                            ExpenditureAdd.as_view(),
                            name='add'),
                        url(r'^expenditures/$',
                            ExpenditureMonthList.as_view(
                                **dict(zip(['month', 'year'],
                                           '{0:%m},{0:%Y}'.format(
                                               datetime.today()).split(',')))),
                            name='list'),
                        url(r'^expenditures/archive/$',
                            ExpenditureMonthList.as_view(),
                            name='archive'))

urlpatterns += patterns('',
                        url(r'^login/$', 'django.contrib.auth.views.login',
                            {'template_name': 'accounts/login.html',
                             'authentication_form': AuthenticationForm},
                            name='login'),
                        url(r'^logout/$', 'django.contrib.auth.views.logout',
                            {'template_name': 'accounts/logged_out.html'},
                            name='logout'),
                        url(r'^password_change/$',
                            'django.contrib.auth.views.password_change',
                            {'template_name': 'accounts/password_change_form.html',
                             'password_change_form': PasswordChangeForm,
                             'post_change_redirect': '/tracker/password_change_done'},
                            name='password_change'),
                        url(r'^password_change_done/$',
                            'django.contrib.auth.views.password_change_done',
                            {'template_name': 'accounts/password_change_done.html'}))
