from rest_framework import generics

from .models import HostRole
from .serializers import HostRoleSerializer


class HostRoleList(generics.ListCreateAPIView):
    queryset = HostRole.objects.all()
    serializer_class = HostRoleSerializer


class HostRoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = HostRole.objects.all()
    serializer_class = HostRoleSerializer
