from rest_framework import serializers

from .models import Network, AddressAssignment


class NetworkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Network
        fields = ('slug', 'description', 'interface_id', 'cidr', 'mask_bits', 'netmask', 'reverse_zone')


class AddressAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressAssignment
        fields = ('host', 'address', 'network', 'canonical')