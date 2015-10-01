from rest_framework import viewsets
from rest_framework.response import Response

from .models import Server
from .serializers import ServerDetailSerializer, ServerListSerializer


class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = Server.objects.all()
        context = {'request': request}
        serializer = ServerListSerializer(queryset, many=True, context=context)
        return Response(serializer.data)
