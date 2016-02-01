from django.shortcuts import render
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
    return render(request, 'hosts/nagios_hosts.txt', {'hosts': hosts})


def nagios_hostgroups(request):
    roles = HostRole.objects.all()
    return render(request, 'hosts/nagios_hostgroups.txt', {'roles': roles})
