"""Module defining generic view mixins.
"""

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils.translation import ungettext
from django.utils.translation import ugettext_lazy as _


class FieldNamesMixin(object):
    """Extends a view context with the ``field_names`` attribute.
    """
    def get_context_data(self, **kwargs):
        context = super(FieldNamesMixin, self).get_context_data(**kwargs)
        try:
            context['field_names'] = self.field_names
        except AttributeError:
            raise ImproperlyConfigured("field_names attribute "
                                       "required by FieldNamesMixin")
        return context


class QueryPaginationMixin(object):
    """Mixin that read the pagination configuration from the query
    parameters.
    """
    paginate_by = 15

    def get_paginate_by(self, queryset):
        """Returns the number of items to paginate by, or ``None`` for no
        pagination.

        Query parameters are search first.
        """
        if 'paginate_by' in self.request.GET:
            try:
                paginate_by = int(self.request.GET['paginate_by'])
            except ValueError:
                paginate_by = self.paginate_by
                # REMARK No pagination is not supported
        else:
            paginate_by = self.paginate_by
        return paginate_by

    def get_context_data(self, **kwargs):
        """Extends the context data with info on the request path.
        """
        context = super(QueryPaginationMixin, self).get_context_data(**kwargs)
        context.update({'path_info': self.request.path_info})
        return context


class QueryFilterMixin(object):
    """Mixin that read the filter configuration from the query parameters.
    """
    filter_ignore_case = True
    filter_attr = "description"

    def has_filter(self):
        """Check whether the query paramater named filter is non empty.
        """
        return ((len(self.request.GET['filter']) != 0)
                if 'filter' in self.request.GET
                else False)

    def get_filter_keywords(self):
        """Return the filter operands found in the query parameters.
        """
        return (self.request.GET['filter'].split(' ')
                if self.has_filter()
                else list())

    def get_context_data(self, **kwargs):
        """Extend the context data with the current filter.
        """
        context = super(QueryFilterMixin, self).get_context_data(**kwargs)
        context.update({'filter_description': _('Apply filter')})
        if self.has_filter():
            kws = self.get_filter_keywords()
            context.update({'filter': ' '.join(kws)})
            last = kws[-1:][0]
            others = ', '.join(kws[:-1])
            text = ungettext('keyword %(last)s',
                             'keywords %(others)s and %(last)s',
                             len(kws)) % {'last': last,
                                          'others': others}
            context.update({'filter_keywords': text})
        return context

    def get_queryset(self):
        """Return a new queryset containing objects that match the filter
        keywords.
        """
        qs = super(QueryFilterMixin, self).get_queryset()
        kw = '{0}__{1}'.format(self.filter_attr,
                               'icontains' if self.filter_ignore_case
                               else 'contains')
        for f in self.get_filter_keywords():
            qs = qs.filter(**{kw: f})
        return qs


class ObjectOwnerMixin(object):
    """Check that the logged in account is the owner of ``object``.

    To be used with ``SingleObjectMixin`` or
    ``SingleObjectTemplateResponseMixin``.
    """
    owner_field = "author"

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        obj = self.get_object()
        if not getattr(obj, self.owner_field, None) == user:
            raise Http404()
        return super(ObjectOwnerMixin, self).dispatch(*args, **kwargs)


class EditableObjectMixin(object):
    """Check that ``object`` is editable.

    To be used with ``SingleObjectMixin`` or
    ``SingleObjectTemplateResponseMixin``.
    """
    def dispatch(self, *args, **kwargs):
        obj = self.get_object()
        try:
            if not obj.is_editable():
                raise Http404()
        except AttributeError:
            raise ImproperlyConfigured("is_editable attribute required "
                                       "by EditableObjectMixin")
        return super(EditableObjectMixin, self).dispatch(*args, **kwargs)
