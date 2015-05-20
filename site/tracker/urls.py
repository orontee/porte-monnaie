"""Module defining the url patterns.

All the url names defined here are accessible from the tracker
namespace.

"""

from django.conf import settings
from django.conf.urls import (patterns, url)
from django.core.urlresolvers import reverse_lazy
from django.utils.timezone import now
from django.views.generic import TemplateView
from tracker.views import (ExpenditureAdd,
                           ExpenditureDelete,
                           ExpenditureUpdate,
                           ExpenditureFilteredList,
                           ExpenditureMonthList,
                           ExpenditureYearSummary,
                           ExpenditureHome,
                           HomeView,
                           PurseCreation,
                           PurseList,
                           PurseUpdate,
                           PurseShare,
                           PurseDelete,
                           TagView,
                           UserChange,
                           UserDefaultPurse)
from tracker.forms import (AuthenticationForm,
                           PasswordChangeForm,
                           PasswordResetForm,
                           SetPasswordForm)
from users.views.base import (UserActivation,
                              UserCreation,
                              UserDeletion)


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
                        url(regex=r'^expenditures/search/$',
                            view=ExpenditureFilteredList.as_view(),
                            name='expenditure-search'),
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
                        url(regex='^purses/share/(?P<pk>\d+)/$',
                            view=PurseShare.as_view(),
                            name='purse_share'),
                        url(regex='^purses/$',
                            view=PurseList.as_view(),
                            name='purse_list'),
                        url(regex=r'^purses/delete/(?P<pk>\d+)/$',
                            view=PurseDelete.as_view(),
                            name='purse_delete'))

urlpatterns += patterns('',
                        url(regex=r'^tags/$',
                            view=TagView.as_view(),
                            name='tags'))

urlpatterns += patterns('',
                        url(regex=r'^user_change/$',
                            view=UserChange.as_view(),
                            name='user_change'),
                        url(regex=r'^user_default_purse/(?P<pk>\d+)/$',
                            view=UserDefaultPurse.as_view(),
                            name='user_default_purse'),
                        url(regex=r'^user_creation/$',
                            view=UserCreation.as_view(
                                success_url=reverse_lazy(
                                    'tracker:user_creation_done')),
                            name='user_creation'),
                        url(regex=r'^user_deletion/$',
                            view=UserDeletion.as_view(
                                success_url=reverse_lazy(
                                    'tracker:home')),
                            name='user_deletion'),
                        url(regex=r'^user_creation_done',
                            view=TemplateView.as_view(
                                template_name='users/user_creation_done.html'),
                            name='user_creation_done'),
                        url(regex=r'^user_activation/(?P<key>\w+)/$',
                            view=UserActivation.as_view(),
                            name='user_activation'))

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
                             reverse_lazy('tracker:home'),
                             'extra_context': {'now': now()}},
                            name='password_change'))

urlpatterns += patterns('',
                        url(r'^password_reset/$',
                            'django.contrib.auth.views.password_reset',
                            {'post_reset_redirect':
                             reverse_lazy('tracker:password_reset_done'),
                             'password_reset_form': PasswordResetForm},
                            name='password_reset'),
                        url(r'^password_reset_done/$',
                            'django.contrib.auth.views.password_reset_done',
                            name='password_reset_done'),
                        url(r'^password_reset_confirm/(?P<uidb64>\w+)/(?P<token>[\w-]+)/$',
                            'django.contrib.auth.views.password_reset_confirm',
                            {'post_reset_redirect':
                             reverse_lazy('tracker:password_reset_complete'),
                             'set_password_form': SetPasswordForm},
                            name='password_reset_confirm'),
                        url(r'^password_reset_complete/$',
                            'django.contrib.auth.views.password_reset_complete',
                            name='password_reset_complete'))

if settings.DEBUG:
    urlpatterns += patterns('',
                            (r'^500/$', 'django.views.defaults.server_error'),
                            (r'^404/$', 'django.views.defaults.page_not_found'),
                            (r'^403/$', 'django.views.defaults.permission_denied'))
