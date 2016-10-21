import csv
import socket
import time

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets

from .models import Network
from .serializers import NetworkSerializer


class NetworkViewSet(viewsets.ModelViewSet):
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer


def available_addresses(request):
    context = {'networks': {}}
    networks_requested = request.GET.get('networks', 'all')
    if networks_requested == 'all':
        networks = Network.objects.all()
    else:
        netsplit = networks_requested.split(',')
        networks = [get_object_or_404(Network, slug=network) for network in netsplit]
    for network in networks:
        context['networks'][network.slug] = network.unused_addresses
    return render(request, 'networks/unused_addrs.html', context)


def assignments_csv(request, slug):
    network = get_object_or_404(Network, slug=slug)
    now = int(time.time())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="address_assignments_{}_{}.csv"'.format(network.slug, now)
    writer = csv.writer(response)
    writer.writerow(['host', 'address'])
    for assignment in sorted(network.address_assignments.all(), key=lambda item: socket.inet_aton(item.address)):
        writer.writerow([assignment.host.hostname, assignment.address])
    return response
