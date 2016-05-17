from rest_framework_json_api import serializers

from .models import Server


class ServerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ('id', 'asset_tag', 'manufacturer', 'model', 'serial')


class ServerDetailSerializer(serializers.ModelSerializer):
    hosts = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='host-detail')

    class Meta:
        model = Server
        fields = ('id', 'asset_tag', 'manufacturer', 'model', 'serial', 'hosts', 'rack_units')