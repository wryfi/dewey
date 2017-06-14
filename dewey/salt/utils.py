from django.shortcuts import get_object_or_404

from dewey.environments.models import Host
from dewey.salt.models import Highstate, StateChange, StateError


def get_highstates(hostname, order_by='-timestamp'):
    host = get_object_or_404(Host, hostname=hostname)
    return Highstate.objects.filter(host=host).order_by(order_by)


def get_latest_highstate(hostname):
    try:
        return get_highstates(hostname, '-timestamp')[0]
    except IndexError:
        return


def get_state_changes(hostname, order_by='-highstate__timestamp'):
    host = get_object_or_404(Host, hostname=hostname)
    return StateChange.objects.filter(highstate__host=host).order_by(order_by)


def get_latest_state_change(hostname):
    try:
        return get_state_changes(hostname, '-highstate__timestamp')[0]
    except IndexError:
        return


def get_state_errors(hostname, order_by='-highstate__timestamp'):
    host = get_object_or_404(Host, hostname=hostname)
    return StateError.objects.filter(highstate__host=host).order_by(order_by)


def get_latest_state_error(hostname):
    try:
        return get_state_errors(hostname, '-highstate__timestamp')[0]
    except IndexError:
        return
