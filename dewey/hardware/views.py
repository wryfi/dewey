from rest_framework import viewsets
from rest_framework.response import Response

from .models import NetworkDevice, PowerDistributionUnit, Server
from .serializers import NetworkDeviceDetailSerializer, NetworkDeviceListSerializer,\
    PowerDistributionUnitDetailSerializer, PowerDistributionUnitListSerializer,\
    ServerDetailSerializer, ServerListSerializer


class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = Server.objects.all()
        context = {'request': request}
        serializer = ServerListSerializer(queryset, many=True, context=context)
        return Response(serializer.data)


class NetworkDeviceViewSet(viewsets.ModelViewSet):
    queryset = NetworkDevice.objects.all()
    serializer_class = NetworkDeviceDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = NetworkDevice.objects.all()
        context = {'request': request}
        serializer = NetworkDeviceListSerializer(queryset, many=True, context=context)
        return Response(serializer.data)


class PowerDistributionUnitViewSet(viewsets.ModelViewSet):
    queryset = PowerDistributionUnit.objects.all()
    serializer_class = PowerDistributionUnitDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = PowerDistributionUnit.objects.all()
        context = {'request': request}
        serializer = PowerDistributionUnitListSerializer(queryset, many=True, context=context)
        return Response(serializer.data)
