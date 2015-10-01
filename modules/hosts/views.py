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