from hashlib import md5
import requests
from django.contrib.contenttypes.models import ContentType

from django.http import HttpResponse
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.conf import settings
from rest_framework import renderers, metadata, pagination, parsers, views, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework_json_api.views import RelationshipView

from .models import AddressAssignment, Cluster, Host, HostRole, Network
from .serializers import AddressAssignmentSerializer, ClusterSerializer, HostRoleSerializer, HostDetailSerializer,\
    NetworkSerializer, SaltHostSerializer


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
    # TODO add support for additional parent types: Server, Cluster, PDU, NetworkDevice, etc.
    serializer_classes = {
        Host: HostDetailSerializer,
        Cluster: ClusterSerializer
    }

    def get_queryset(self):
        host_pk = self.kwargs.get('host_pk', None)
        if host_pk:
            host = Host.objects.get(id=host_pk)
            parent_type = host.parent_type.model_class()
            self.serializer_class = self.serializer_classes.get(parent_type)
            queryset = parent_type.objects.filter(id=host.parent_id)
            return queryset


class HostVirtualMachineViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostDetailSerializer

    def get_queryset(self):
        host_pk = self.kwargs.get('host_pk', None)
        host_type = ContentType.objects.get(model='host')
        if host_pk:
            queryset = Host.objects.filter(parent_id=host_pk).filter(parent_type=host_type).exclude(id=host_pk)
            return queryset


class HostAddressAssignmentViewSet(viewsets.ModelViewSet):
    queryset = AddressAssignment.objects.all()
    serializer_class = AddressAssignmentSerializer

    def get_queryset(self):
        host_pk = self.kwargs.get('host_pk', None)
        if host_pk:
            queryset = AddressAssignment.objects.filter(host_id=host_pk)
            return queryset


class StandardApiMixin(object):
    renderer_classes = [
        renderers.JSONRenderer,
        renderers.BrowsableAPIRenderer
    ]
    parser_classes = [
        parsers.JSONParser,
        parsers.FormParser,
        parsers.MultiPartParser
    ]
    metadata_class = metadata.SimpleMetadata
    pagination_class = None


class SaltHostViewSet(StandardApiMixin, viewsets.ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = SaltHostSerializer
    lookup_field = 'hostname'
    lookup_value_regex = '[\w\.-]+\.\w+'


# TODO rewrite as a class-based view and add to api router
@api_view(http_method_names=['GET'])
@renderer_classes([renderers.JSONRenderer, renderers.BrowsableAPIRenderer])
def salt_discovery_view(request, environment=None):
    discovery = {}
    if environment:
        for role in HostRole.objects.all():
            discovery[role.name] = []
            for host in role.hosts:
                if host.environment == environment:
                    discovery[role.name].append(host.hostname)
    return Response(discovery)


class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class NetworkViewSet(viewsets.ModelViewSet):
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer


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

