"""Module defining the url patterns.

All the url names defined here are accessible from the tracker
namespace.
"""

from django.conf.urls import (patterns, url)
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.forms import (AuthenticationForm,
                                       PasswordChangeForm)
from django.views.generic import TemplateView
from tracker.views import (ExpenditureAdd,
                           ExpenditureDelete,
                           ExpenditureUpdate,
                           ExpenditureMonthList,
                           ExpenditureYearSummary,
                           ExpenditureHome,
                           HomeView,
                           PurseCreation, PurseUpdate, PurseList,
                           UserChange)
from users.views.base import (UserCreation, UserActivation)

urlpatterns = patterns('',
                       url(regex=r'^$',
                           view=HomeView.as_view(),
                           name='home'))

urlpatterns += patterns('',
                        url(regex=r'^expenditures/add/$',
                            view=ExpenditureAdd.as_view(),
                            name='add'),
                        url(regex=r'^expenditures/update/(?P<pk>\d+)/$',
                            view=ExpenditureUpdate.as_view(),
                            name='update'),
                        url(regex=r'^expenditures/delete/(?P<pk>\d+)/$',
                            view=ExpenditureDelete.as_view(),
                            name='delete'),
                        url(regex=r'^expenditures/(?P<year>\d+)/(?P<month>\d+)/$',
                            view=ExpenditureMonthList.as_view(),
                            name='archive'),
                        url(regex=r'^expenditures/summary/(?P<year>\d+)/$',
                            view=ExpenditureYearSummary.as_view(),
                            name='summary'),
                        url(regex=r'^expenditures/$',
                            view=ExpenditureHome.as_view(),
                            name='list'))

urlpatterns += patterns('',
                        url(regex=r'^purses/create/$',
                            view=PurseCreation.as_view(),
                            name='purse_creation'),
                        url(regex=r'^purses/update/(?P<pk>\d+)/$',
                            view=PurseUpdate.as_view(),
                            name='purse_update'),
                        url(regex='^purses/$',
                            view=PurseList.as_view(),
                            name='purse_list'))

urlpatterns += patterns('',
                        url(regex=r'^user_change/$',
                            view=UserChange.as_view(
                                success_url=reverse_lazy('tracker:home')),
                            name='user_change'),
                        url(regex=r'^user_creation/$',
                            view=UserCreation.as_view(
                                success_url=reverse_lazy(
                                    'tracker:user_creation_done')),
                            name='user_creation'))

urlpatterns += patterns('',
                        url(r'^login/$', 'django.contrib.auth.views.login',
                            {'template_name': 'users/login.html',
                             'authentication_form': AuthenticationForm},
                            name='login'),
                        url(r'^logout/$', 'django.contrib.auth.views.logout',
                            {'template_name': 'users/logged_out.html'},
                            name='logout'),
                        url(r'^password_change/$',
                            'django.contrib.auth.views.password_change',
                            {'template_name':
                             'users/password_change_form.html',
                             'password_change_form': PasswordChangeForm,
                             'post_change_redirect':
                             reverse_lazy('tracker:home')},
                            name='password_change'),
                        url(regex=r'^user_creation_done',
                            view=TemplateView.as_view(
                                template_name='users/user_creation_done.html'),
                            name='user_creation_done'),
                        url(regex=r'^user_activation/(?P<key>\w+)/$',
                            view=UserActivation.as_view(),
                            name='user_activation'))
