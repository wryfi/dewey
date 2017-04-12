import re

from django.apps import apps
from django.contrib import admin
from django import forms

from .models import Host, HostMonitoringException, Role


class CustomHostForm(forms.ModelForm):
    def clean(self):
        environment = self.cleaned_data['environment']
        regex = re.compile(environment.hostname_regex)
        if not re.match(regex, self.cleaned_data['hostname']):
            raise forms.ValidationError('that is not a valid hostname for this environment')
        return self.cleaned_data


class HostAdmin(admin.ModelAdmin):
    form = CustomHostForm
    ordering = ('hostname',)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'roles':
            kwargs['queryset'] = Role.objects.order_by('name')
        return super(HostAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class MonitoringExceptionAdmin(admin.ModelAdmin):
    ordering = ('host__hostname',)


class RoleAdmin(admin.ModelAdmin):
    ordering = ('name',)


admin.site.register(Host, HostAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(HostMonitoringException, MonitoringExceptionAdmin)

for model in apps.get_app_config('environments').get_models():
    if model != Host and model != Role and model != HostMonitoringException:
        admin.site.register(model)
