"""
Module defining the url patterns.

All the url names defined here are accessible from the tracker
namespace.
"""

from django.conf.urls import (patterns, url)
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy
from tracker.views import (ExpenditureAdd, ExpenditureList)

urlpatterns = patterns('tracker.views',
                       url(r'^$', RedirectView.as_view(url=reverse_lazy('tracker:add')), name='home'))

urlpatterns += patterns('tracker.views',
                       url(r'^add_expenditure/$',
                           ExpenditureAdd.as_view(),
                           name='add'),
                       url(r'^expenditures/$',
                           ExpenditureList.as_view()))
