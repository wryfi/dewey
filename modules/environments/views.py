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

from dewey.utils import dotutils
from .models import Cluster, Host, Role
from networks.models import AddressAssignment, Network
from .serializers import ClusterSerializer, HostRoleSerializer, HostDetailSerializer,\
    SaltHostSerializer, SaltHostSecretsSerializer
from networks.serializers import AddressAssignmentSerializer
from hardware.models import NetworkDevice, PowerDistributionUnit, Server
from hardware.serializers import NetworkDeviceDetailSerializer, PowerDistributionUnitDetailSerializer, ServerDetailSerializer


class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostDetailSerializer


class HostRelationshipView(RelationshipView):
    queryset = Host.objects


class HostRoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = HostRoleSerializer

    def get_queryset(self):
        queryset = self.queryset
        if 'host_pk' in self.kwargs:
            host_pk = self.kwargs['host_pk']
            queryset = queryset.filter(host__pk=host_pk)
        return queryset


class HostParentViewSet(viewsets.ModelViewSet):
    serializer_classes = {
        Host: HostDetailSerializer,
        Cluster: ClusterSerializer,
        PowerDistributionUnit: PowerDistributionUnitDetailSerializer,
        NetworkDevice: NetworkDeviceDetailSerializer,
        Server: ServerDetailSerializer
    }

    def get_parent_type(self):
        host_pk = self.kwargs.get('host_pk', None)
        if host_pk:
            host = Host.objects.get(id=host_pk)
            return host.parent_type.model_class()

    def get_serializer_class(self):
        if self.kwargs.get('host_pk'):
            return self.serializer_classes.get(self.get_parent_type())

    def get_queryset(self):
        host_pk = self.kwargs.get('host_pk', None)
        if host_pk:
            host = Host.objects.get(id=host_pk)
            parent_type = self.get_parent_type()
            queryset = parent_type.objects.filter(id=host.parent_id)
            return queryset


class HostVirtualMachineViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostDetailSerializer

    def get_queryset(self):
        host_pk = self.kwargs.get('host_pk', None)
        host_type = ContentType.objects.get(app_label='environments', model='host')
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


class SaltHostViewSet(StandardApiMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Host.objects.all()
    serializer_class = SaltHostSerializer
    lookup_field = 'hostname'
    lookup_value_regex = '[\w\.-]+\.\w+'


class SaltHostSecretsViewSet(StandardApiMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = SaltHostSecretsSerializer

    def get_queryset(self):
        host_hostname = self.kwargs.get('host_hostname', None)
        if host_hostname:
            queryset = Host.objects.filter(hostname=host_hostname)
            return queryset


# TODO rewrite as a class-based view and add to api router
@api_view(http_method_names=['GET', 'HEAD'])
@renderer_classes([renderers.JSONRenderer, renderers.BrowsableAPIRenderer])
def salt_discovery_view(request, environment=None):
    discovery = {}
    if environment:
        for role in Role.objects.all():
            discovery[role.name] = []
            for host in role.hosts:
                if host.environment.name == environment:
                    discovery[role.name].append(host.hostname)
    return Response(discovery)


class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


@api_view(http_method_names=['GET', 'HEAD'])
@renderer_classes([renderers.JSONRenderer, renderers.BrowsableAPIRenderer])
def role_secrets(request, environment, role):
    safes = []
    secrets = []
    secrets_dict = {}
    role = Role.objects.get(name=role)
    if environment == 'all':
        env_acls = SafeAccessControl.objects.filter(safe__vault__all_environments=True)
        for acl in env_acls.filter(content_type=ContentType.objects.get_for_model(Role)).filter(object_id=role.id):
            safes.append(acl.safe)
    else:
        for safe_acl in role.safe_acls.all():
            if safe_acl.safe.environment_name == environment:
                safes.append(safe_acl.safe)
    for safe in safes:
        for secret in safe.secret_set.all():
            secrets.append(secret)
    for secret in secrets:
        secrets_dict[secret.name] = secret.export_format
    return Response(dotutils.expand_flattened_dict(secrets_dict))


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
    roles = Role.objects.all()
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
