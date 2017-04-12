from rest_framework import serializers

from dewey.hardware.models import NetworkDevice, PowerDistributionUnit, Server


class ServerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ('id', 'asset_tag', 'manufacturer', 'model', 'serial')


class ServerDetailSerializer(serializers.ModelSerializer):
    hosts = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='host-detail')

    class Meta:
        model = Server
        fields = ('id', 'asset_tag', 'manufacturer', 'model', 'serial', 'hosts', 'rack_units')


class NetworkDeviceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkDevice
        fields = ('id', 'name', 'ports', 'speed', 'interconnect')


class NetworkDeviceDetailSerializer(serializers.ModelSerializer):
    hosts = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='host-detail')

    class Meta:
        model = NetworkDevice
        fields = ('id', 'name', 'ports', 'speed', 'interconnect', 'hosts')


class PowerDistributionUnitListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PowerDistributionUnit
        fields = ('id', 'name', 'ports', 'volts', 'amps')


class PowerDistributionUnitDetailSerializer(serializers.ModelSerializer):
    hosts = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='host-detail')

    class Meta:
        model = PowerDistributionUnit
        fields = ('id', 'name', 'ports', 'volts', 'amps', 'hosts')
