from rest_framework import serializers

from .models import NetworkDevice, PowerDistributionUnit, Server


class ServerListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Server
        fields = ('id', 'asset_tag', 'manufacturer', 'model', 'serial')


class ServerDetailSerializer(serializers.HyperlinkedModelSerializer):
    hosts = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='host-detail')

    class Meta:
        model = Server
        fields = ('id', 'asset_tag', 'manufacturer', 'model', 'serial', 'hosts', 'rack_units')


class NetworkDeviceListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NetworkDevice
        fields = ('id', 'name', 'ports', 'speed', 'interconnect')


class NetworkDeviceDetailSerializer(serializers.HyperlinkedModelSerializer):
    hosts = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='host-detail')

    class Meta:
        model = NetworkDevice
        fields = ('id', 'name', 'ports', 'speed', 'interconnect', 'hosts')


class PowerDistributionUnitListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PowerDistributionUnit
        fields = ('id', 'name', 'ports', 'volts', 'amps')


class PowerDistributionUnitDetailSerializer(serializers.HyperlinkedModelSerializer):
    hosts = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='host-detail')

    class Meta:
        model = PowerDistributionUnit
        fields = ('id', 'name', 'ports', 'volts', 'amps', 'hosts')
