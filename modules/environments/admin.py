import re

from django.apps import apps
from django.contrib import admin
from django import forms

from .models import Host


class CustomHostForm(forms.ModelForm):
    def clean_hostname(self):
        if not re.match(r'(.*\.)+.*', self.cleaned_data['hostname']):
            raise forms.ValidationError('please enter a FULLY QUALIFIED name')
        return self.cleaned_data['hostname']


class HostAdmin(admin.ModelAdmin):
    form = CustomHostForm


admin.site.register(Host, HostAdmin)

for model in apps.get_app_config('environments').get_models():
    if model != Host:
        admin.site.register(model)
