import json

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

from ..models import Environment, Grain, Host, Role, Safe, SafeAccessControl, Secret, Vault
from ..forms import GrainCreateForm, SecretAddForm, SecretCreateForm, HostSafeAccessForm, RoleSafeAccessForm, SafeUpdateForm, \
    SecretUpdateForm, SafeCreateForm
from dewey.utils.decorators import HostAccessRequired, SafeAccessRequired


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


@HostAccessRequired('hostname')
def host_grain_create(request, *args, **kwargs):
    host = get_object_or_404(Host, hostname=kwargs.get('hostname'))
    if request.method == 'POST':
        form = GrainCreateForm(request.POST, initial={'host': host.id})
        if form.is_valid():
            grain = form.save()
            messages.add_message(request, messages.SUCCESS, 'added grain {} to {}'.format(grain.name, grain.host.shortname))
        else:
            messages.add_message(request, messages.ERROR, json.dumps(form.errors))
    return redirect('host_detail', hostname=host.hostname)


@HostAccessRequired('hostname')
def host_grain_delete(request, *args, **kwargs):
    host = get_object_or_404(Host, hostname=kwargs.get('hostname'))
    if request.method == 'POST':
        grain = get_object_or_404(Grain, host=host, name=request.POST.get('name'))
        grain.delete()
        messages.add_message(request, messages.SUCCESS, 'deleted grain {}'.format(request.POST.get('name')))
        return redirect('host_detail', hostname=host.hostname)
    else:
        return HttpResponseNotAllowed(['POST'])


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
    create_form = SecretCreateForm()
    context = {
        'secrets_count': Secret.objects.count(),
        'safes_count': Safe.objects.count(),
        'secret_form': update_form,
        'delete_form': delete_form,
        'secret': secret,
        'secret_create_form': create_form
    }
    return render(request, 'environments/secret_detail.html', context)


@SafeAccessRequired('safe')
def secret_update(request, *args, **kwargs):
    safe = get_object_or_404(Safe, name=kwargs['safe'])
    secret = get_object_or_404(Secret, name=kwargs['name'], safe=safe)
    form = SecretUpdateForm(request.POST or None, instance=secret)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'updated secret {}'.format(secret.name))
        else:
            messages.add_message(request, messages.ERROR, json.dumps(form.errors))
    return redirect(reverse('secret_detail', kwargs={'name': secret.name, 'safe': safe.name}))


@SafeAccessRequired('safe')
def secret_delete(request, *args, **kwargs):
    safe = get_object_or_404(Safe, name=kwargs.get('safe'))
    secret = get_object_or_404(Secret, name=kwargs.get('name'), safe=safe)
    form = SecretUpdateForm(request.POST or None, instance=secret)
    if request.method == 'POST':
        if form.is_valid():
            secret.delete()
            messages.add_message(request, messages.SUCCESS, 'deleted secret {}'.format(secret.name))
            return redirect(reverse('secrets'))
        else:
            messages.add_message(request, messages.ERROR, json.dumps(form.errors))
    return redirect(reverse('secret_detail', kwargs={'name': secret.name, 'safe': safe.name}))


@SafeAccessRequired('safe')
def secret_create(request, *args, **kwargs):
    if request.method == 'POST':
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


# TODO: refactor some forms to call REST API via javascript
def safe_detail(request, *args, **kwargs):
    safe = get_object_or_404(Safe, name=kwargs['name'])
    update_form = SafeUpdateForm(request.POST or None, instance=safe)
    create_form = SafeCreateForm()
    secret_form =  SecretAddForm(
            initial={'safe': safe.id, 'redirect': reverse('safe_detail', kwargs={'name': safe.name})}
    )
    secret_form.helper.form_action = reverse('secret_create', kwargs={'safe': safe.name})
    context = {
        'secrets_count': Secret.objects.count(),
        'safes_count': Safe.objects.count(),
        'safe': safe,
        'safe_update_form': update_form,
        'safe_create_form': create_form,
        'host_access_form': HostSafeAccessForm(initial={'safe': safe.id}, user=request.user),
        'role_access_form': RoleSafeAccessForm(initial={'safe': safe.id}),
        'secret_form': secret_form,
    }
    if request.method == 'POST':
        if request.POST.get('verb') == 'update':
            if update_form.is_valid():
                update_form.save()
                messages.add_message(request, messages.SUCCESS, 'updated safe {}'.format(safe.name))
                return redirect(reverse('safe_detail', kwargs={'name': safe.name}))
        elif request.POST.get('verb') == 'delete':
            count = safe.secret_set.count()
            safe.delete()
            messages.add_message(request, messages.SUCCESS,
                                 'deleted safe {} and {} secrets'.format(safe.name, count))
            return redirect(reverse('safe_list'))
    return render(request, 'environments/safe_detail.html', context)


# TODO: this view doesn't use the forms api like everything else;
# it returns an ugly 403 instead of a pretty validation error when access is denied
# this should really be a javascript call to an API endpoint
def delete_safe_access(request, *args, **kwargs):
    if request.method == 'POST':
        safe = get_object_or_404(Safe, id=request.POST.get('safe'))
        groups = [group.name for group in request.user.groups.all()]
        if safe.environment_name not in groups and safe.environment_name != 'all':
            if not request.user.is_superuser:
                raise PermissionDenied
        if request.POST.get('role'):
            role = get_object_or_404(Role, name=request.POST.get('role'))
            access_list = SafeAccessControl.objects.filter(safe=safe).filter(object_id=role.id).filter(
                content_type=ContentType.objects.get_for_model(Role))
        elif request.POST.get('host'):
            host = get_object_or_404(Host, hostname=request.POST.get('host'))
            access_list = SafeAccessControl.objects.filter(safe=safe).filter(object_id=host.id).filter(
                content_type=ContentType.objects.get_for_model(Host))
        redirect_url = request.POST.get('redirect', reverse('secrets'))
        for control in access_list:
            control.delete()
        messages.add_message(request, messages.SUCCESS, 'removed control(s) from {}'.format(safe.name))
        return redirect(redirect_url)


# TODO: this view doesn't use the forms api like everything else;
# it returns an ugly 403 instead of a pretty validation error when access is denied
# this should really be a javascript call to an API endpoint
def create_safe_access(request, *args, **kwargs):
    if request.method == 'POST':
        safe = get_object_or_404(Safe, id=request.POST.get('safe'))
        groups = [group.name for group in request.user.groups.all()]
        if safe.environment_name not in groups and safe.environment_name != 'all':
            if not request.user.is_superuser:
                raise PermissionDenied
        redirect_url = request.POST.get('redirect', reverse('safe_detail', kwargs={'name': safe.name}))
        if request.POST.get('role'):
            contenttype = ContentType.objects.get_for_model(Role)
            acl_object = get_object_or_404(Role, id=request.POST.get('role'))
        elif request.POST.get('host'):
            contenttype = ContentType.objects.get_for_model(Host)
            acl_object = get_object_or_404(Host, id=request.POST.get('host'))
        try:
            control, created = SafeAccessControl.objects.get_or_create(
                safe=safe, content_type=contenttype, object_id=acl_object.id
            )
            if created:
                message, level = 'added access control', messages.SUCCESS
            else:
                message, level = 'access control already exists', messages.WARNING
            messages.add_message(request, level, message)
        except NameError:
            messages.add_message(request, messages.ERROR, 'host or role was not provided')
        return redirect(redirect_url)

