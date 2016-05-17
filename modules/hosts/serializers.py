from rest_framework_json_api import serializers
from rest_framework.relations import Hyperlink

from dewey.serializers import HyperlinkedGenericRelatedField
from .models import Cluster, Host, HostRole
from hardware.models import Server


class HostDetailSerializer(serializers.ModelSerializer):
    parent = serializers.HyperlinkedRelatedField(view_name='host-detail', read_only=True)
    virtual_machines = serializers.HyperlinkedRelatedField(read_only=True, many=True, view_name='host-detail')
    roles = serializers.ResourceRelatedField(
        many=True,
        queryset=Host.objects,
        related_link_view_name='host-roles-nested-list',
        related_link_url_kwarg='host_pk',
        self_link_view_name='host-relationships'
    )

    class Meta:
        model = Host
        fields = ('hostname', 'shortname', 'domain', 'kind', 'operating_system', 'roles',
                  'parent', 'virtual_machines', 'environment', 'ip_addresses')

    def create(self, validated_data):
        return Host(**validated_data)

    def update(self, instance, validated_data):
        return instance


class HostRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostRole
        fields = ('id', 'name', 'description')


class ClusterSerializer(serializers.ModelSerializer):
    kind = serializers.SerializerMethodField()

    class Meta:
        model = Cluster
        fields = ('id', 'name', 'description', 'kind', 'members')

    def get_kind(self, obj):
        return obj.get_kind_display()
