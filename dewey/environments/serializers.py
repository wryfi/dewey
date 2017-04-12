from rest_framework import serializers as serializers

from .models import Cluster, Host, Role
from dewey.networks.models import AddressAssignment, Network


class SaltHostSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    environment = serializers.SerializerMethodField()

    class Meta:
        # TODO: remove environment and roles fields
        # after salt is transitioned to using grains field
        model = Host
        fields = ('id', 'hostname', 'ip_addresses', 'environment', 'roles', 'grains')

    def get_roles(self, obj):
        return [role.name for role in obj.roles.all()]

    def get_environment(self, obj):
        return obj.environment.name


class SaltHostSecretsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Host
        fields = ('id', 'hostname', 'salt_secrets')


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
