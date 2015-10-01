from rest_framework import serializers

from hosts.serializers import HostListSerializer
from .models import Server


class ServerListSerializer(serializers.HyperlinkedModelSerializer):
    hosts = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='host-detail')

    class Meta:
        model = Server
        fields = ('id', 'asset_tag', 'manufacturer', 'model', 'serial', 'hosts')


class ServerDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Server
        fields = ('id', 'asset_tag', 'manufacturer', 'model', 'serial', 'hosts', 'rack_units')