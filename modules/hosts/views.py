from hashlib import md5
import requests

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.conf import settings
from rest_framework import viewsets
from rest_framework_json_api.views import RelationshipView

from .models import Cluster, Host, HostRole, Network
from .serializers import ClusterSerializer, HostRoleSerializer, HostDetailSerializer


class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostDetailSerializer


class HostRelationshipView(RelationshipView):
    queryset = Host.objects


class HostRoleViewSet(viewsets.ModelViewSet):
    queryset = HostRole.objects.all()
    serializer_class = HostRoleSerializer

    def get_queryset(self):
        queryset = self.queryset
        if 'host_pk' in self.kwargs:
            host_pk = self.kwargs['host_pk']
            queryset = queryset.filter(host__pk=host_pk)
        return queryset


class HostParentViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostDetailSerializer

    def get_queryset(self):
        queryset = self.queryset
        if 'host_pk' in self.kwargs:
            host_pk = self.kwargs['host_pk']
            host = Host.objects.get(id=host_pk)
            parent = host.parent_type.model_class().objects.get(id=host.parent_id)
            queryset = queryset.filter(id=parent.id)
        return queryset


class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


def nagios_hosts(request):
    hosts = Host.objects.all()
    routers = []
    for slug in settings.NAGIOS_NETWORKS:
        try:
            network = Network.objects.get(slug=slug)
            routers.append({'ip': network.gateway, 'name': network.gateway.replace('.', '-')})
        except Network.DoesNotExist:
            pass
    return render(request, 'hosts/nagios_hosts.txt', {'hosts': hosts, 'routers': routers},
                  content_type='text/plain')


def nagios_hostgroups(request):
    roles = HostRole.objects.all()
    return render(request, 'hosts/nagios_hostgroups.txt', {'roles': roles}, content_type='text/plain')


def nagios_hosts_md5(request):
    path = reverse('nagios_hosts')
    hosts_url = '{}://{}{}'.format(settings.SITE_PROTOCOL, settings.SITE_DOMAIN, path)
    if settings.FRONTEND == 'runserver':
        return HttpResponse('this view is unsupported with the development server, {}'.format(hosts_url))
    else:
        request = requests.get(hosts_url)
        request.raise_for_status()
        checksum = md5(request.content).hexdigest()
        return HttpResponse(checksum, content_type='text/plain')


def nagios_hostgroups_md5(request):
    path = reverse('nagios_hostgroups')
    hostgroups_url = '{}://{}{}'.format(settings.SITE_PROTOCOL, settings.SITE_DOMAIN, path)
    if settings.FRONTEND == 'runserver':
        return HttpResponse('this view is unsupported with the development server, {}'.format(hostgroups_url))
    else:
        request = requests.get(hostgroups_url)
        request.raise_for_status()
        checksum = md5(request.content).hexdigest()
        return HttpResponse(checksum, content_type='text/plain')

