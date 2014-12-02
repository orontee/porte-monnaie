"""Module defining generic view mixins."""

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils import formats
from django.utils.timezone import now
from django.utils.translation import ungettext
from django.utils.translation import ugettext_lazy as _


class WithCurrentDateMixin(object):
    """Extends a view context with the current datetime."""
    def get_context_data(self, **kwargs):
        context = super(WithCurrentDateMixin, self).get_context_data(**kwargs)
        context['now'] = now()
        return context


class FieldNamesMixin(object):
    """Mixin that handles tables field names.

    The view context is extended with a key called ``field_names``.
    Its value is read from an attribute with the same name.

    """
    def get_context_data(self, **kwargs):
        """Extends the context with the ``field_names`` key."""
        context = super(FieldNamesMixin, self).get_context_data(**kwargs)
        try:
            context['field_names'] = self.field_names
        except AttributeError:
            raise ImproperlyConfigured('FieldNamesMixin requires '
                                       'the field_names attribute')
        return context


class QueryPaginationMixin(object):
    """Mixin that reads the pagination configuration.

    The configuration is read from the query parameters.

    """
    paginate_by = 15

    def get_paginate_by(self, queryset):
        """Returns the number of items to paginate by.

        It may return ``None`` for no pagination. Query parameters are
        search first, then the attribute ``paginate_by``.

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
        """Extends the context data with info on the request path."""
        context = super(QueryPaginationMixin, self).get_context_data(**kwargs)
        context.update({'path_info': self.request.path_info})
        return context


class QueryFilterMixin(object):
    """Mixin that read the filter configuration from the query parameters.

    The expected query parameter is named ``filter`` and its value is
    splitted to get the filter keywords.

    It supports filtering on one field whose name is read from the
    ``filter_attr`` attribute. The lookup type used to filter is
    ``contains`` or ``icontains`` depending on the
    ``filter_ignore_case`` attribute.

    When the attribute ``filter_num_attr`` is set, filtering also
    applies to the specified field but only for keywords convertible
    to float.

    All filters are combined using logical AND operations.
    """
    filter_ignore_case = True
    filter_attr = 'description'
    filter_num_attr = 'amount'
    filter_description = _('Apply filter')

    def has_filter(self):
        """Checks whether the query parameter named filter is non empty."""
        return ((len(self.request.GET['filter']) != 0)
                if 'filter' in self.request.GET
                else False)

    def get_filter_keywords(self):
        """Returns the filter operands found in the query parameters."""
        kws = (self.request.GET['filter'].split(' ')
               if self.has_filter() else list())
        return kws

    def get_context_data(self, **kwargs):
        """Extends the context data with the current filter."""
        context = super(QueryFilterMixin, self).get_context_data(**kwargs)
        context.update({'filter_description': self.filter_description})
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
        """Filter the default query set."""
        qs = super(QueryFilterMixin, self).get_queryset()
        kw = '{0}__{1}'.format(self.filter_attr,
                               'icontains' if self.filter_ignore_case
                               else 'contains')
        if self.filter_num_attr is not None:
            okw = '{0}__{1}'.format(self.filter_num_attr, 'exact')

        for f in self.get_filter_keywords():
            dct, n = {}, None
            if self.filter_num_attr is not None:
                try:
                    n = float(formats.sanitize_separators(f))
                    dct[okw] = n
                except ValueError:
                    pass
            if n is None:
                dct[kw] = f
            qs = qs.filter(**dct)
        return qs


class ObjectOwnerMixin(object):
    """Check that the authenticated user is the owner of an object.

    This mixin must be used with ``SingleObjectMixin`` or
    ``SingleObjectTemplateResponseMixin``.

    """
    owner_field = None

    def is_owner(self, user, obj):
        """Checks that ``user`` is the owner of ``obj``.

        The check compares the attributes named ``owner_field`` of
        ``obj`` and ``user``.

        """
        if self.owner_field is None:
            raise ImproperlyConfigured('ObjectOwnerMixin requires '
                                       'the owner_field')
        return getattr(obj, self.owner_field, None) == user

    def dispatch(self, *args, **kwargs):
        """Raise a 404 exception in case the ``is_owner`` check fails."""
        user = self.request.user
        obj = self.get_object()
        if not self.is_owner(user, obj):
            raise Http404()
        return super(ObjectOwnerMixin, self).dispatch(*args, **kwargs)


class EditableObjectMixin(object):
    """Check that an object is editable.

    To be used with ``SingleObjectMixin`` or
    ``SingleObjectTemplateResponseMixin``.

    """
    def dispatch(self, *args, **kwargs):
        """Raise a 404 exception in case the object is not editable."""
        obj = self.get_object()
        try:
            if not obj.is_editable():
                raise Http404()
        except AttributeError:
            raise ImproperlyConfigured('EditableObjectMixin requires '
                                       'the is_editable attribute')
        return super(EditableObjectMixin, self).dispatch(*args, **kwargs)
