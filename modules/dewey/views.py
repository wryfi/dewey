from django.core.exceptions import ImproperlyConfigured

import logging

logger = logging.getLogger('.'.join(['dewey', __name__]))


class FilterMixin(object):
    """
    View mixin which provides filtering for ListView.
    Lifted from https://gist.github.com/robgolding/4097500
    """
    filter_url_kwarg = 'filter'
    default_filter_param = None

    def get_default_filter_param(self):
        if self.default_filter_param is None:
            raise ImproperlyConfigured(
                "'FilterMixin' requires the 'default_filter_param' attribute "
                "to be set.")
        return self.default_filter_param

    def filter_queryset(self, qs, filter_param):
        """
        Filter the queryset `qs`, given the selected `filter_param`. Default
        implementation does no filtering at all.
        """
        return qs

    def get_filter_param(self):
        return self.request.GET.get(self.filter_url_kwarg,
                               self.get_default_filter_param())

    def get_queryset(self):
        return self.filter_queryset(
            super(FilterMixin, self).get_queryset(),
            self.get_filter_param())

    def get_context_data(self, *args, **kwargs):
        context = super(FilterMixin, self).get_context_data(*args, **kwargs)
        context.update({
            'filter': self.get_filter_param(),
        })
        return context


class SortMixin(object):
    """
    View mixin which provides sorting for ListView.
    Lifted from https://gist.github.com/robgolding/4097500
    """
    default_sort_params = None

    def sort_queryset(self, qs, order_by, order):
        return qs

    def get_default_sort_params(self):
        if self.default_sort_params is None:
            raise ImproperlyConfigured(
                "'SortMixin' requires the 'default_sort_params' attribute "
                "to be set.")
        return self.default_sort_params

    def get_sort_params(self):
        default_order_by, default_order = self.get_default_sort_params()
        order_by = self.request.GET.get('order_by', default_order_by)
        order = self.request.GET.get('order', default_order)
        return (order_by, order)

    def get_queryset(self):
        return self.sort_queryset(
            super(SortMixin, self).get_queryset(),
            *self.get_sort_params())

    def get_context_data(self, *args, **kwargs):
        context = super(SortMixin, self).get_context_data(*args, **kwargs)
        order_by, order = self.get_sort_params()
        context.update({
            'order_by': order_by,
            'order': order,
        })
        return context
