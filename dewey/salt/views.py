from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404

from dewey.environments.models import Host
from dewey.salt.models import Highstate, StateChange, Change, StateError
from dewey.core.utils.pagination import get_paginator


def highstate_detail(request, id):
    highstate = get_object_or_404(Highstate, id=id)
    context = {'highstate': highstate}
    return render(request, 'salt/highstate_detail.html', context=context)


def highstates_list(request):
    context = {'hosts': Host.objects.order_by('hostname')}
    highstates = Highstate.objects.order_by('-timestamp')
    if 'host' in request.GET.keys():
        hostname = request.GET.get('host')
        if hostname != 'all':
            highstates = highstates.filter(host__hostname=hostname)
    context['highstates'] = get_paginator(highstates, request.GET.get('page'))
    return render(request, 'salt/highstates_list.html', context=context)


def statechanges_list(request):
    context = {'hosts': Host.objects.order_by('hostname')}
    statechanges = StateChange.objects.order_by('-highstate__timestamp')
    if 'host' in request.GET.keys():
        hostname = request.GET.get('host')
        if hostname != 'all':
            statechanges = statechanges.filter(highstate__host__hostname=hostname)
    context['statechanges'] = get_paginator(statechanges, request.GET.get('page'))
    return render(request, 'salt/statechanges_list.html', context=context)


def change_detail(request, id):
    context = {'change': get_object_or_404(Change, id=id)}
    return render(request, 'salt/change_detail.html', context=context)


def stateerrors_list(request):
    context = {'hosts': Host.objects.order_by('hostname')}
    stateerrors = StateError.objects.order_by('-highstate__timestamp')
    if 'host' in request.GET.keys():
        hostname = request.GET.get('host')
        if hostname != 'all':
            stateerrors = stateerrors.filter(highstate__host=hostname)
    context['stateerrors'] = get_paginator(stateerrors, request.GET.get('page'))
    print(context)
    return render(request, 'salt/stateerrors_list.html', context=context)

