from django.views.generic.list import ListView
from django.utils import timezone

from dewey.views import SortMixin, FilterMixin
from environments.models import Environment, Host, Role

import logging

logger = logging.getLogger('.'.join(['dewey', __name__]))


class HostListView(SortMixin, ListView):
    model = Host
    default_sort_params = ('hostname', 'asc')

    def get_template_names(self):
        return [self.kwargs['template']]

    def sort_queryset(self, queryset, order_by, order):
        if not order_by or order_by == 'hostname':
            queryset = queryset.order_by('hostname')
        if order == 'desc':
            queryset = queryset.reverse()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(HostListView, self).get_context_data(*args, **kwargs)
        context.update({'environments': Environment.objects.order_by('name')})
        context.update({'host_count': Host.objects.all().count()})
        context.update({'roles': Role.objects.order_by('name')})
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = super(HostListView, self).get_queryset(*args, **kwargs)
        if 'environment' in self.request.GET.keys():
            environment = self.request.GET.get('environment')
            if environment != 'all':
                queryset = queryset.filter(environment__name=environment)
        if 'roles' in self.request.GET.keys():
            if self.request.GET.get('roles') != 'any':
                roles = self.request.GET.get('roles').split(':')
                role_list = []
                for role in roles:
                    try:
                        role_list.append(Role.objects.get(name=role))
                    except Role.DoesNotExist:
                        pass
                queryset = queryset.filter(roles__in=role_list).distinct()
        return queryset

