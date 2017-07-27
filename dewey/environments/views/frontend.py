import json

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST

from ..models import Environment, Grain, Host, Role, Safe, SafeAccessControl, Secret, Vault
from ..forms import GrainCreateForm, SecretAddForm, HostSafeAccessForm, RoleSafeAccessForm, SafeUpdateForm, \
    SecretUpdateForm, SafeCreateForm
from dewey.core.utils.decorators import HostAccessRequired, SafeAccessRequired


def hosts_list(request, *args, **kwargs):
    context = {
        'environments': Environment.objects.order_by('name'),
        'roles': Role.objects.order_by('name'),
        'hosts': Host.objects.order_by('hostname'),
        'hosts_count': Host.objects.count()
    }
    if 'environment' in request.GET.keys():
        environment = request.GET.get('environment')
        if environment != 'all':
            context['hosts'] = context['hosts'].filter(environment__name=environment)
    if 'roles' in request.GET.keys():
        if request.GET.get('roles') != 'any':
            roles = request.GET.get('roles').split(':')
            role_list = []
            for role in roles:
                try:
                    role_list.append(Role.objects.get(name=role))
                except Role.DoesNotExist:
                    pass
            context['hosts'] = context['hosts'].filter(roles__in=role_list).distinct()
    return render(request, 'environments/hosts.html', context)


def host_detail(request, *args, **kwargs):
    host = get_object_or_404(Host, hostname=kwargs.get('hostname'))
    grain_form = GrainCreateForm(request.POST or None, initial={'host': host.id})
    grain_form.helper.form_action = reverse('host_grain_create', kwargs={'hostname': host.hostname})
    context = {'host': host, 'grain_form': grain_form}
    return render(request, 'environments/host_detail.html', context)


@require_POST
@HostAccessRequired('hostname')
def host_grain_create(request, *args, **kwargs):
    host = get_object_or_404(Host, hostname=kwargs.get('hostname'))
    form = GrainCreateForm(request.POST, initial={'host': host.id})
    if form.is_valid():
        grain = form.save()
        messages.add_message(request, messages.SUCCESS, 'added grain {} to {}'.format(grain.name, grain.host.shortname))
    else:
        messages.add_message(request, messages.ERROR, json.dumps(form.errors))
    return redirect('host_detail', hostname=host.hostname)


@require_POST
@HostAccessRequired('hostname')
def host_grain_delete(request, *args, **kwargs):
    host = get_object_or_404(Host, hostname=kwargs.get('hostname'))
    grain = get_object_or_404(Grain, host=host, name=request.POST.get('name'))
    grain.delete()
    messages.add_message(request, messages.SUCCESS, 'deleted grain {}'.format(request.POST.get('name')))
    return redirect('host_detail', hostname=host.hostname)


def secrets_list(request, *args, **kwargs):
    context = {
        'secrets': Secret.objects.order_by('name'),
        'secrets_count': Secret.objects.count(),
        'safes_count': Safe.objects.count(),
    }
    return render(request, 'environments/secrets.html', context)


def secret_detail(request, *args, **kwargs):
    safe = get_object_or_404(Safe, name=kwargs['safe'])
    secret = get_object_or_404(Secret, name=kwargs['name'], safe=safe)
    update_form = SecretUpdateForm(request.POST or None, instance=secret)
    update_form.helper.form_action = reverse('secret_update', kwargs={'safe': safe.name, 'name': secret.name})
    delete_form = SecretUpdateForm(request.POST or None, instance=secret)
    delete_form.helper.form_action = reverse('secret_delete', kwargs={'safe': safe.name, 'name': secret.name})
    context = {
        'secrets_count': Secret.objects.count(),
        'safes_count': Safe.objects.count(),
        'secret_form': update_form,
        'delete_form': delete_form,
        'secret': secret,
    }
    return render(request, 'environments/secret_detail.html', context)


@require_POST
@SafeAccessRequired('safe')
def secret_update(request, *args, **kwargs):
    safe = get_object_or_404(Safe, name=kwargs['safe'])
    secret = get_object_or_404(Secret, name=kwargs['name'], safe=safe)
    form = SecretUpdateForm(request.POST or None, instance=secret)
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, 'updated secret {}'.format(secret.name))
    else:
        messages.add_message(request, messages.ERROR, json.dumps(form.errors))
    return redirect(reverse('safe_detail', kwargs={'name': safe.name}))


@require_POST
@SafeAccessRequired('safe')
def secret_delete(request, *args, **kwargs):
    safe = get_object_or_404(Safe, name=kwargs.get('safe'))
    secret = get_object_or_404(Secret, name=kwargs.get('name'), safe=safe)
    form = SecretUpdateForm(request.POST or None, instance=secret)
    if form.is_valid():
        secret.delete()
        messages.add_message(request, messages.SUCCESS, 'deleted secret {}'.format(secret.name))
        return redirect(reverse('secrets'))
    else:
        messages.add_message(request, messages.ERROR, json.dumps(form.errors))
    return redirect(reverse('secret_detail', kwargs={'name': secret.name, 'safe': safe.name}))


@require_POST
@SafeAccessRequired('safe')
def secret_create(request, *args, **kwargs):
    form = SecretAddForm(request.POST or None)
    if form.is_valid():
        secret = form.save(commit=False)
        secret.safe = get_object_or_404(Safe, name=kwargs.get('safe'))
        secret.save()
        messages.add_message(request, messages.SUCCESS,
                             'saved secret {} to {}'.format(form.cleaned_data['name'], secret.safe.name))
        if form.cleaned_data.get('redirect'):
            return redirect(form.cleaned_data['redirect'])
        return redirect(reverse('secret_detail', kwargs={'safe': secret.safe.name, 'name': secret.name}))
    else:
        messages.add_message(request, messages.ERROR, json.dumps(form.errors))
    return redirect(reverse('secrets'))


def safes_list(request, *args, **kwargs):
    safe_create_form = SafeCreateForm(request.POST or None)
    context = {
        'safes': Safe.objects.order_by('name'),
        'safes_count': Safe.objects.count(),
        'secrets_count': Secret.objects.count(),
        'safe_create_form': safe_create_form
    }
    if request.method == 'POST':
        if safe_create_form.is_valid():
            safe = safe_create_form.save(commit=False)
            vault = get_object_or_404(Vault, id=safe_create_form.cleaned_data['vault'])
            safe.vault = vault
            safe.save()
            messages.add_message(request, messages.SUCCESS, 'added safe {}'.format(safe.name))
            return redirect(reverse('safe_detail', kwargs={'name': safe.name}))
    return render(request, 'environments/safes.html', context)


def safe_detail(request, *args, **kwargs):
    safe = get_object_or_404(Safe, name=kwargs['name'])
    context = {
        'secrets_count': Secret.objects.count(),
        'safes_count': Safe.objects.count(),
        'safe': safe,
        'safe_update_form': SafeUpdateForm(request.POST or None, instance=safe),
        'safe_create_form': SafeCreateForm(),
        'host_access_form': HostSafeAccessForm(initial={'safe': safe.id}),
        'role_access_form': RoleSafeAccessForm(initial={'safe': safe.id}),
        'secret_form': SecretAddForm(
            initial={'safe': safe.id, 'redirect': reverse('safe_detail', kwargs={'name': safe.name})}
        ),
    }
    context['secret_form'].helper.form_action = reverse('secret_create', kwargs={'safe': safe.name})
    context['host_access_form'].helper.form_action = reverse('safe_access_create_host', kwargs={'name': safe.name})
    context['role_access_form'].helper.form_action = reverse('safe_access_create_role', kwargs={'name': safe.name})
    if request.method == 'POST':
        if context['safe_update_form'].is_valid():
            context['safe_update_form'].save()
            messages.add_message(request, messages.SUCCESS, 'updated safe {}'.format(safe.name))
            return redirect(reverse('safe_detail', kwargs={'name': safe.name}))
    return render(request, 'environments/safe_detail.html', context)


@require_POST
@SafeAccessRequired('name')
def safe_delete(request, *args, **kwargs):
    safe = get_object_or_404(Safe, name=kwargs.get('name'))
    count = safe.secret_set.count()
    safe.delete()
    messages.add_message(request, messages.SUCCESS, 'deleted safe {} and {} secrets'.format(safe.name, count))
    return redirect(reverse('safe_list'))


@require_POST
@SafeAccessRequired('name')
def safe_access_delete_host(request, *args, **kwargs):
    # I'm abusing HostSafeAccessForm for form validation;
    form = HostSafeAccessForm(request.POST)
    if form.is_valid():
        host = get_object_or_404(Host, id=form.cleaned_data.get('host'))
        safe = get_object_or_404(Safe, id=form.cleaned_data.get('safe'))
        access_list = SafeAccessControl.objects\
            .filter(safe=safe)\
            .filter(object_id=host.id)\
            .filter(content_type=ContentType.objects.get_for_model(Host))
        for access_control in access_list:
            access_control.delete()
        messages.add_message(request, messages.SUCCESS, 'removed control(s) from {}'.format(safe.name))
        return redirect(reverse('safe_detail', kwargs={'name': safe.name}))
    else:
        safe = get_object_or_404(Safe, name=kwargs['name'])
        messages.add_message(request, messages.ERROR, json.dumps(form.errors))
        return redirect(reverse('safe_detail', kwargs={'name': safe.name}))


@require_POST
@SafeAccessRequired('name')
def safe_access_delete_role(request, *args, **kwargs):
    # I'm abusing RoleSafeAccessForm for form validation;
    form = RoleSafeAccessForm(request.POST)
    if form.is_valid():
        role = get_object_or_404(Role, id=form.cleaned_data.get('role'))
        safe = get_object_or_404(Safe, id=form.cleaned_data.get('safe'))
        access_list = SafeAccessControl.objects\
            .filter(safe=safe)\
            .filter(object_id=role.id)\
            .filter(content_type=ContentType.objects.get_for_model(Role))
        for access_control in access_list:
            access_control.delete()
        messages.add_message(request, messages.SUCCESS, 'removed control(s) from {}'.format(safe.name))
        return redirect(reverse('safe_detail', kwargs={'name': safe.name}))
    else:
        messages.add_message(request, messages.ERROR, json.dumps(form.errors))
        safe = get_object_or_404(Safe, name=kwargs['name'])
        return redirect(reverse('safe_detail', kwargs={'name': safe.name}))


@require_POST
@SafeAccessRequired('name')
def safe_access_create_host(request, *args, **kwargs):
    form = HostSafeAccessForm(request.POST)
    if form.is_valid():
        host = get_object_or_404(Host, id=form.cleaned_data.get('host'))
        safe = get_object_or_404(Safe, id=form.cleaned_data.get('safe'))
        control, created = SafeAccessControl.objects.get_or_create(
            safe=safe, object_id=host.id, content_type=ContentType.objects.get_for_model(Host)
        )
        if created:
            message, level = 'added access control', messages.SUCCESS
        else:
            message, level = 'access control already exists', messages.WARNING
    else:
        message, level = json.dumps(form.errors), messages.ERROR
        safe = get_object_or_404(Safe, name=kwargs.get('name'))
    messages.add_message(request, level, message)
    return redirect(reverse('safe_detail', kwargs={'name': safe.name}))


@require_POST
@SafeAccessRequired('name')
def safe_access_create_role(request, *args, **kwargs):
    form = RoleSafeAccessForm(request.POST)
    if form.is_valid():
        role = get_object_or_404(Role, id=form.cleaned_data.get('role'))
        safe = get_object_or_404(Safe, id=form.cleaned_data.get('safe'))
        control, created = SafeAccessControl.objects.get_or_create(
            safe=safe, object_id=role.id, content_type=ContentType.objects.get_for_model(Role)
        )
        if created:
            message, level = 'added access control', messages.SUCCESS
        else:
            message, level = 'access control already exists', messages.WARNING
    else:
        message, level = json.dumps(form.errors), messages.ERROR
        safe = get_object_or_404(Safe, name=kwargs.get('name'))
    messages.add_message(request, level, message)
    return redirect(reverse('safe_detail', kwargs={'name': safe.name}))

