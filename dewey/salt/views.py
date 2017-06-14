from django.shortcuts import render, get_object_or_404

from dewey.salt.models import Highstate, StateChange, Change, StateError


def highstate_detail(request, jid):
    highstate = get_object_or_404(Highstate, jid=jid)
    context = {'highstate': highstate}
    return render(request, 'salt/highstate_detail.html', context=context)


def highstates_list(request):
    context = {'highstates': Highstate.objects.order_by('-timestamp')}
    return render(request, 'salt/highstates_list.html', context=context)


def statechanges_list(request):
    context = {'statechanges': StateChange.objects.order_by('-highstate__timestamp')}
    return render(request, 'salt/statechanges_list.html', context=context)


def statechange_detail(request, id):
    context = {'statechange': get_object_or_404(StateChange, id=id)}
    return render(request, 'salt/statechange_detail.html', context=context)


def change_detail(request, id):
    context = {'change': get_object_or_404(Change, id=id)}
    return render(request, 'salt/change_detail.html', context=context)


def stateerrors_list(request):
    context = {'stateerrors': StateError.objects.order_by('-highstate__timestamp')}
    return render(request, 'salt/stateerrors_list.html', context=context)


def stateerror_detail(request, id):
    context = {'stateerror': get_object_or_404(StateError, id=id)}
    return render(request, 'salt/stateerror_detail.html', context=context)
