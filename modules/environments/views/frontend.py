from django.contrib.contenttypes.models import ContentType
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse

from dewey.views import SortMixin, FilterMixin
from environments.models import Environment, Host, Role, Safe, SafeAccessControl, Secret
from ..forms import CreateSecretForm, HostSafeAccessForm, RoleSafeAccessForm, UpdateSecretForm

import logging

logger = logging.getLogger('.'.join(['dewey', __name__]))


class HostListView(SortMixin, ListView):
    model = Host
    default_sort_params = ('hostname', 'asc')

    def get_template_names(self):
        return [self.kwargs['template']]

    def sort_queryset(self, queryset, order_by, order):
        if not order_by or order_by == 'hostname':
            queryset = queryset.order_by('hostname')
        if order == 'desc':
            queryset = queryset.reverse()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(HostListView, self).get_context_data(*args, **kwargs)
        context.update({'environments': Environment.objects.order_by('name')})
        context.update({'host_count': Host.objects.all().count()})
        context.update({'roles': Role.objects.order_by('name')})
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = super(HostListView, self).get_queryset(*args, **kwargs)
        if 'environment' in self.request.GET.keys():
            environment = self.request.GET.get('environment')
            if environment != 'all':
                queryset = queryset.filter(environment__name=environment)
        if 'roles' in self.request.GET.keys():
            if self.request.GET.get('roles') != 'any':
                roles = self.request.GET.get('roles').split(':')
                role_list = []
                for role in roles:
                    try:
                        role_list.append(Role.objects.get(name=role))
                    except Role.DoesNotExist:
                        pass
                queryset = queryset.filter(roles__in=role_list).distinct()
        return queryset


class HostDetailView(DetailView):
    model = Host
    template_name = 'environments/host_detail.html'

    def get_object(self):
        return get_object_or_404(Host, hostname=self.kwargs['hostname'])


class SecretListView(ListView):
    model = Secret
    template_name = 'environments/secrets.html'

    def get_context_data(self, *args, **kwargs):
        context = super(SecretListView, self).get_context_data(*args, **kwargs)
        context.update({'secrets_count': Secret.objects.count()})
        context.update({'safes_count': Safe.objects.count()})
        context.update({'secret_form': CreateSecretForm})
        return context


class SecretDetailView(DetailView):
    model = Secret
    template_name = 'environments/secret_detail.html'

    def get_object(self, queryset=None):
        safe = get_object_or_404(Safe, name=self.kwargs['safe'])
        return get_object_or_404(Secret, name=self.kwargs['name'], safe=safe)

    def get_context_data(self, *args, **kwargs):
        context = super(SecretDetailView, self).get_context_data(*args, **kwargs)
        form = UpdateSecretForm(initial=self.object.__dict__)
        form.helper.form_action = reverse('secret_detail', kwargs={'name': self.object.name, 'safe': self.object.safe.name})
        context.update({'secret_form': form})
        return context


class SafeDetailView(DetailView):
    model = Safe
    template_name = 'environments/safe_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Safe, name=self.kwargs['name'])

    def get_context_data(self, *args, **kwargs):
        context = super(SafeDetailView, self).get_context_data(*args, **kwargs)
        context.update({'host_access_form': HostSafeAccessForm(initial={'safe': self.object.id})})
        context.update({'role_access_form': RoleSafeAccessForm(initial={'safe': self.object.id})})
        return context


def create_secret(request, *args, **kwargs):
    if request.method == 'POST':
        form = CreateSecretForm(request.POST)
        if form.is_valid():
            secret = form.save(commit=False)
            secret.safe = get_object_or_404(Safe, id=form.cleaned_data['safe'])
            secret.save()
            messages.add_message(request, messages.SUCCESS, 'saved secret {}'.format(form.cleaned_data['name']))
    return redirect(reverse('secrets'))


def update_secret(request, *args, **kwargs):
    if request.method == 'POST':
        form = UpdateSecretForm(request.POST)
        if form.is_valid():
            safe = get_object_or_404(Safe, name=kwargs['safe'])
            secret = get_object_or_404(Secret, name=kwargs['name'], safe=safe)
            secret.name = form.cleaned_data['name']
            secret.secret = form.cleaned_data['secret']
            secret.save()
            messages.add_message(request, messages.SUCCESS, 'updated secret {}'.format(secret.name))
            return redirect(reverse('secret_detail', kwargs={'name': secret.name, 'safe': safe.name}))
    return redirect(reverse('secret_detail', kwargs={'name': kwargs['name'], 'safe': kwargs['safe']}))


def delete_secret(request, *args, **kwargs):
    if request.method == 'POST':
        safe = Safe.objects.get(name=request.POST.get('safe'))
        secret = Secret.objects.get(name=request.POST.get('secret'), safe=safe)
        secret.delete()
        messages.add_message(request, messages.SUCCESS, 'deleted secret {} from {}'.format(secret.name, safe.name))
        return redirect(reverse('secrets'))


def secrets(request, *args, **kwargs):
    if request.method == 'GET':
        return SecretListView.as_view()(request, *args, **kwargs)
    if request.method == 'POST':
        return create_secret(request, *args, **kwargs)


def secret(request, *args, **kwargs):
    if request.method == 'GET':
        return SecretDetailView.as_view()(request, *args, **kwargs)
    if request.method == 'POST':
        if request.POST.get('verb') == 'update':
            return update_secret(request, *args, **kwargs)
        elif request.POST.get('verb') == 'delete':
            return delete_secret(request, *args, **kwargs)


def delete_safe_access(request, *args, **kwargs):
    if request.method == 'POST':
        safe = get_object_or_404(Safe, id=request.POST.get('safe'))
        if request.POST.get('role'):
            role = get_object_or_404(Role, name=request.POST.get('role'))
            access_list = SafeAccessControl.objects.filter(safe=safe).filter(object_id=role.id).filter(content_type=ContentType.objects.get_for_model(Role))
        elif request.POST.get('host'):
            host = get_object_or_404(Host, hostname=request.POST.get('host'))
            access_list = SafeAccessControl.objects.filter(safe=safe).filter(object_id=host.id).filter(content_type=ContentType.objects.get_for_model(Host))
        redirect_url = request.POST.get('redirect', reverse('secrets'))
        for control in access_list:
            control.delete()
        messages.add_message(request, messages.SUCCESS, 'removed control(s) from {}'.format(safe.name))
        return redirect(redirect_url)


def create_safe_access(request, *args, **kwargs):
    if request.method == 'POST':
        safe = get_object_or_404(Safe, id=request.POST.get('safe'))
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