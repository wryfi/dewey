import re

from django.apps import apps
from django.contrib import admin
from django import forms

from .models import Environment, Host


class CustomHostForm(forms.ModelForm):
    def clean(self):
        environment = self.cleaned_data['environment']
        regex = re.compile(environment.hostname_regex)
        if not re.match(regex, self.cleaned_data['hostname']):
            raise forms.ValidationError('that is not a valid hostname for this environment')
        return self.cleaned_data


class HostAdmin(admin.ModelAdmin):
    form = CustomHostForm


admin.site.register(Host, HostAdmin)

for model in apps.get_app_config('environments').get_models():
    if model != Host:
        admin.site.register(model)
