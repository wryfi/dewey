from rest_framework import fields, serializers
from rest_framework.relations import Hyperlink
from rest_framework.reverse import reverse

from dewey.serializers import HyperlinkedGenericRelatedField
from .models import Cluster, Host, HostRole
from . import OperatingSystem
from hardware.models import Server


class HostListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Host
        fields = ('id', 'hostname', 'environment')


class HyperlinkedParentField(HyperlinkedGenericRelatedField):
    # TODO: implement to_internal_value() method
    def to_representation(self, value):
        request = self.context.get('request', None)
        format = self.context.get('format', None)

        assert request is not None, (
            "`%s` requires the request in the serializer"
            " context. Add `context={'request': request}` when instantiating "
            "the serializer." % self.__class__.__name__
        )

        if isinstance(value, Server):
            self.view_name = 'server-detail'
            self.queryset = Server.objects.all()
            parent_type = 'server'
        elif isinstance(value, Host):
            self.view_name = 'host-detail'
            self.queryset = Host.objects.all()
            parent_type = 'host'
        elif isinstance(value, Cluster):
            self.view_name = 'cluster-detail'
            self.queryset = Cluster.objects.all()
            parent_type = 'cluster'
        else:
            raise RuntimeError('Unexpected parent type')

        if format and self.format and self.format != format:
           format = self.format

        try:
            url = self.get_url(value, self.view_name, request, format)
        except NoReverseMatch:
            msg = (
                'Could not resolve URL for hyperlinked relationship using '
                'view name "%s". You may have failed to include the related '
                'model in your API, or incorrectly configured the '
                '`lookup_field` attribute on this field.'
            )
            if value in ('', None):
                value_string = {'': 'the empty string', None: 'None'}[value]
                msg += (
                    " WARNING: The value of the field on the model instance "
                    "was %s, which may be why it didn't match any "
                    "entries in your URL conf." % value_string
                )
            raise ImproperlyConfigured(msg % self.view_name)

        if url is None:
            return None

        name = self.get_name(value)
        return {'id': value.id, 'kind': parent_type, 'url': Hyperlink(url, name)}


class HostDetailSerializer(serializers.HyperlinkedModelSerializer):
    # TODO: figure out how to make writable!
    parent = HyperlinkedParentField(read_only=True)
    virtual_machines = serializers.HyperlinkedRelatedField(read_only=True, many=True, view_name='host-detail')

    class Meta:
        model = Host
        fields = ('hostname', 'shortname', 'domain', 'kind', 'operating_system', 'roles',
                  'parent', 'virtual_machines', 'environment', 'ip_addresses')


class HostRoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HostRole
        fields = ('id', 'name', 'description')


class ClusterSerializer(serializers.HyperlinkedModelSerializer):
    kind = serializers.SerializerMethodField()

    class Meta:
        model = Cluster
        fields = ('id', 'name', 'description', 'kind', 'members')

    def get_kind(selfself, obj):
        return obj.get_kind_display()
