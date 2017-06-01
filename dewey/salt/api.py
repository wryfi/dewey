from rest_framework import viewsets

from .models import Change, Highstate, StateChange, StateError
from .serializers import ChangeSerializer, HighstateSerializer, StateChangeSerializer, StateErrorSerializer


class HighstateViewSet(viewsets.ModelViewSet):
    serializer_class = HighstateSerializer
    queryset = Highstate.objects.all()


class StateChangeViewSet(viewsets.ModelViewSet):
    serializer_class = StateChangeSerializer
    queryset = StateChange.objects.all()


class StateErrorViewSet(viewsets.ModelViewSet):
    serializer_class= StateErrorSerializer
    queryset = StateError.objects.all()


class ChangeViewSet(viewsets.ModelViewSet):
    serializer_class = ChangeSerializer
    queryset = Change.objects.all()
