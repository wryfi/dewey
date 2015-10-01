from rest_framework import serializers

from .models import HostRole


class HostRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostRole
        fields = ('id', 'name','description')