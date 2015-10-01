from rest_framework import serializers

from .models import Cluster, Host, HostRole


class HostListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Host
        fields = ('id', 'hostname', 'roles')


class HostDetailSerializer(serializers.HyperlinkedModelSerializer):
    operating_system = serializers.SerializerMethodField()

    class Meta:
        model = Host
        fields = ('hostname', 'shortname', 'domain', 'kind', 'operating_system', 'roles')

    def get_operating_system(self, obj):
        return obj.get_operating_system_display()


class HostRoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HostRole
        fields = ('id', 'name', 'description')


class ClusterSerializer(serializers.HyperlinkedModelSerializer):
    kind = serializers.SerializerMethodField()

    class Meta:
        model = Cluster
        fields = ('id', 'name', 'description', 'kind', 'hosts')

    def get_kind(selfself, obj):
        return obj.get_kind_display()
