from rest_framework_json_api import serializers
from rest_framework import serializers as vanilla_serial
from rest_framework.relations import Hyperlink

from .models import AddressAssignment, Cluster, Host, HostRole, Network
from hardware.models import Server


class HostDetailSerializer(serializers.ModelSerializer):
    parent = serializers.ResourceRelatedField(
        queryset=Host.objects,
        related_link_view_name='host-parent-list',
        related_link_url_kwarg='host_pk',
        self_link_view_name='host-relationships'
    )
    roles = serializers.ResourceRelatedField(
        many=True,
        queryset=Host.objects,
        related_link_view_name='host-roles-nested-list',
        related_link_url_kwarg='host_pk',
        self_link_view_name='host-relationships'
    )
    virtual_machines = serializers.ResourceRelatedField(
        many=True,
        queryset=Host.objects,
        related_link_view_name='host-virtual-machines-list',
        related_link_url_kwarg='host_pk',
        self_link_view_name='host-relationships'
    )
    address_assignments = serializers.ResourceRelatedField(
        many=True,
        queryset=Host.objects,
        related_link_view_name='host-address-assignments-list',
        related_link_url_kwarg='host_pk',
        self_link_view_name='host-relationships'
    )

    class Meta:
        model = Host
        fields = ('hostname', 'shortname', 'domain', 'kind', 'operating_system', 'roles',
                  'parent', 'virtual_machines', 'environment', 'address_assignments')
        read_only_fields = ('shortname', 'domain', 'roles', 'parent', 'virtual_machines'
                            'environment', 'address_assignments')


class HostRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = HostRole
        fields = ('id', 'name', 'description')


class SaltHostSerializer(vanilla_serial.ModelSerializer):
    roles = vanilla_serial.SerializerMethodField()

    class Meta:
        model = Host
        fields = ('id', 'hostname', 'ip_addresses', 'environment', 'roles')

    def get_roles(self, obj):
         return [role.name for role in obj.roles.all()]


class ClusterSerializer(serializers.ModelSerializer):
    kind = serializers.SerializerMethodField()

    class Meta:
        model = Cluster
        fields = ('id', 'name', 'description', 'kind', 'members')

    def get_kind(self, obj):
        return obj.get_kind_display()


class NetworkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Network
        fields = ('slug', 'description', 'interface_id', 'cidr', 'mask_bits', 'netmask', 'reverse_zone')


class AddressAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressAssignment
        fields = ('host', 'address', 'network', 'canonical')
