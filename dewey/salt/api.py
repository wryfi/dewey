from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets

from .models import Change, Highstate, StateChange, StateError
from .serializers import ChangeSerializer, HighstateSerializer, StateChangeSerializer, StateErrorSerializer


class SaltApiPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        salt_group = get_object_or_404(Group, name='salt')
        if request.user.is_authenticated() and request.method in permissions.SAFE_METHODS:
            return True
        return salt_group in request.user.groups.all()


class HighstateViewSet(viewsets.ModelViewSet):
    permission_classes = (SaltApiPermission,)
    serializer_class = HighstateSerializer
    queryset = Highstate.objects.all()


class StateChangeViewSet(viewsets.ModelViewSet):
    permission_classes = (SaltApiPermission,)
    serializer_class = StateChangeSerializer
    queryset = StateChange.objects.all()


class StateErrorViewSet(viewsets.ModelViewSet):
    permission_classes = (SaltApiPermission,)
    serializer_class= StateErrorSerializer
    queryset = StateError.objects.all()


class ChangeViewSet(viewsets.ModelViewSet):
    permission_classes = (SaltApiPermission,)
    serializer_class = ChangeSerializer
    queryset = Change.objects.all()
