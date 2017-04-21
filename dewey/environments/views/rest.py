import csv
from hashlib import md5
import requests
import time

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.conf import settings
from rest_framework import renderers, metadata, parsers, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes

from dewey.core.utils import dotutils
from dewey.environments import OperatingSystem
from dewey.environments.models import Cluster, Environment, Host, Role, SafeAccessControl, Secret
from dewey.networks.models import Network
from dewey.environments.serializers import ClusterSerializer, \
    SaltHostSerializer, SaltHostSecretsSerializer


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
    my_env_role_acls = []
    secrets_dict = {}
    role = get_object_or_404(Role, name=role)
    environment = get_object_or_404(Environment, name=environment)
    all_env_acls = SafeAccessControl.objects.filter(safe__vault__all_environments=True)
    all_env_all_host_acls = all_env_acls.filter(all_hosts=True)
    all_env_role_acls = all_env_acls.filter(
        content_type=ContentType.objects.get_for_model(Role)
    ).filter(
        object_id=role.id
    )
    for safe_acl in role.safe_acls.all():
        if safe_acl.safe.environment == environment:
            my_env_role_acls.append(safe_acl)
    all_host_acls = SafeAccessControl.objects.filter(all_hosts=True)
    my_env_all_host_acls = all_host_acls.filter(safe__vault__environment=environment)
    for acls in [all_env_all_host_acls, all_env_role_acls, my_env_all_host_acls, my_env_role_acls]:
        for acl in acls:
            safes.append(acl.safe)
    for safe in safes:
        for secret in safe.secret_set.all():
            secrets_dict[secret.name] = secret.export_format
    return Response(dotutils.expand_flattened_dict(secrets_dict))


def export_secrets(request):
    now = int(time.time())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="secrets_{}.csv"'.format(now)
    writer = csv.writer(response)
    writer.writerow(['name', 'safe', 'secret'])
    for secret in Secret.objects.all():
        writer.writerow([secret.name, secret.safe.id, secret.export_format])
    return response


def nagios_hosts(request):
    hosts = []
    for host in Host.objects.all():
        if host.monitored:
            hosts.append(host)
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
    roles = [role for role in Role.objects.all() if role.monitored_hosts]
    hosts_by_os = {}
    for os in OperatingSystem:
        hosts = Host.objects.filter(operating_system=os)
        hosts_by_os[os.name] = [host for host in hosts if host.monitored]
    context = {'roles': roles, 'hosts': hosts_by_os}
    return render(request, 'hosts/nagios_hostgroups.txt', context, content_type='text/plain')


def nagios_hosts_md5(request):
    path = reverse('nagios_hosts')
    hosts_url = '{}://{}{}'.format(settings.SITE_PROTOCOL, settings.SITE_DOMAIN, path)
    if settings.FRONTEND == 'runserver':
        return HttpResponse('this view is unsupported with the development server, {}'.format(hosts_url))
    else:
        request = requests.get(hosts_url, verify='/etc/ssl/certs/plos-ca.pem')
        request.raise_for_status()
        checksum = md5(request.content).hexdigest()
        return HttpResponse(checksum, content_type='text/plain')


def nagios_hostgroups_md5(request):
    path = reverse('nagios_hostgroups')
    hostgroups_url = '{}://{}{}'.format(settings.SITE_PROTOCOL, settings.SITE_DOMAIN, path)
    if settings.FRONTEND == 'runserver':
        return HttpResponse('this view is unsupported with the development server, {}'.format(hostgroups_url))
    else:
        request = requests.get(hostgroups_url, verify='/etc/ssl/certs/plos-ca.pem')
        request.raise_for_status()
        checksum = md5(request.content).hexdigest()
        return HttpResponse(checksum, content_type='text/plain')
