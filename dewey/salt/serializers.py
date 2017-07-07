from rest_framework import serializers

from .models import Change, Highstate, StateChange, StateError
from dewey.environments.models import Host


class HighstateSerializer(serializers.ModelSerializer):
    host = serializers.SlugRelatedField(slug_field='hostname', queryset=Host.objects.all())

    class Meta:
        model = Highstate
        fields = ('id', 'host', 'timestamp', 'return_code', 'jid')


class StateErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateError
        fields = ('id', 'highstate', 'state_id', 'name', 'comment')


class StateChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateChange
        fields = ('id', 'highstate', 'state_id', 'name', 'comment', 'change_set')


class ChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Change
        fields = ('id', 'state_change', 'change_type', 'content')
