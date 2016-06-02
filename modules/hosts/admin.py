from django.contrib import admin
from django.apps import apps
from django import forms

from .models import AddressAssignment


class CustomAddrAssignmentForm(forms.ModelForm):
    def clean(self):
        address = self.cleaned_data['address']
        canonical = self.cleaned_data['canonical']
        host = self.cleaned_data['host']
        network = self.cleaned_data['network']
        if canonical:
            for assignment in AddressAssignment.objects.filter(host=host):
                if assignment.canonical:
                    raise forms.ValidationError(
                        '{} is already canonical for {}'.format(assignment.address, host.hostname)
                    )
        if address not in network.range:
            raise forms.ValidationError('{} is not in the selected network'.format(address))
        if not AddressAssignment.objects.filter(network=network).filter(host=host).filter(address=address).exists():
            if network.address_allocated(address):
                raise forms.ValidationError('{} has already been allocated'.format(address))
        return self.cleaned_data


class AddrAssignmentAdmin(admin.ModelAdmin):
    form = CustomAddrAssignmentForm


admin.site.register(AddressAssignment, AddrAssignmentAdmin)

for model in apps.get_app_config('hosts').get_models():
    if model != AddressAssignment:
        admin.site.register(model)
