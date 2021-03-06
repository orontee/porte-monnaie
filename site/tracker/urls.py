"""Module defining the url patterns.

All the url names defined here are accessible from the tracker
namespace.

"""

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.views import (login, logout,
                                       password_change,
                                       password_reset,
                                       password_reset_done,
                                       password_reset_complete)
from django.core.urlresolvers import reverse_lazy
from django.utils.timezone import now
from django.views.defaults import (server_error,
                                   page_not_found,
                                   permission_denied)
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
                           PasswordResetForm)
from users.views.base import (PasswordResetConfirm,
                              UserActivation,
                              UserCreation,
                              UserDeletion)


urlpatterns = [
    url(regex=r'^$',
        view=HomeView.as_view(),
        name='home')]

urlpatterns += [
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
        name='list')]

urlpatterns += [
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
        name='purse_delete')]

urlpatterns += [
    url(regex=r'^tags/$',
        view=TagView.as_view(),
        name='tags')]

urlpatterns += [
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
        name='user_activation')]

urlpatterns += [
    url(r'^login/$', login,
        {'authentication_form': AuthenticationForm},
        name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^password_change/$', password_change,
        {'password_change_form': PasswordChangeForm,
         'post_change_redirect':
         reverse_lazy('tracker:home'),
         'extra_context': {'now': now()}},
        name='password_change')]

urlpatterns += [
    url(r'^password_reset/$', password_reset,
        {'post_reset_redirect':
         reverse_lazy('tracker:password_reset_done'),
         'password_reset_form': PasswordResetForm},
        name='password_reset'),
    url(r'^password_reset_done/$', password_reset_done,
        name='password_reset_done'),
    url(r'^password_reset_confirm/(?P<uidb64>\w+)/(?P<token>[\w-]+)/$',
        view=PasswordResetConfirm.as_view(
            success_url=reverse_lazy(
                'tracker:password_reset_complete')),
        name='password_reset_confirm'),
    url(r'^password_reset_complete/$', password_reset_complete,
        name='password_reset_complete')]

if settings.DEBUG:
    urlpatterns += [
        url(r'^500/$', server_error),
        url(r'^404/$', page_not_found),
        url(r'^403/$', permission_denied)
    ]
