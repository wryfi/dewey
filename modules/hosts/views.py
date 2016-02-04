from hashlib import md5
import requests

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.conf import settings
from rest_framework import generics, viewsets
from rest_framework.response import Response

from .models import Cluster, Host, HostRole
from .serializers import ClusterSerializer, HostRoleSerializer, HostDetailSerializer, HostListSerializer


class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = Host.objects.all()
        context = {'request': request}
        serializer = HostListSerializer(queryset, many=True, context=context)
        return Response(serializer.data)


class HostRoleViewSet(viewsets.ModelViewSet):
    queryset = HostRole.objects.all()
    serializer_class = HostRoleSerializer


class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


def nagios_hosts(request):
    hosts = Host.objects.all()
    return render(request, 'hosts/nagios_hosts.txt', {'hosts': hosts}, content_type='text/plain')


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

