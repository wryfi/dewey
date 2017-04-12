import csv
import socket
import time

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets

from .models import Network
from .serializers import NetworkSerializer


class NetworkViewSet(viewsets.ModelViewSet):
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer


@login_required
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


@login_required
def get_unused_addresses(request):
    context = {'networks': []}
    for network in Network.objects.all():
        context['networks'].append({'slug': network.slug, 'address': network.get_unused_address()})
    return render(request, 'networks/address_finder.html', context)


@login_required
def assignments_csv(request):
    now = int(time.time())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="address_assignments_{}.csv"'.format(now)
    writer = csv.writer(response)
    for network in Network.objects.all():
        for assignment in sorted(network.address_assignments.all(), key=lambda item: socket.inet_aton(item.address)):
            writer.writerow([network.slug, assignment.host.hostname, assignment.address])
    return response

