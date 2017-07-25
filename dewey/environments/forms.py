import re

from django import forms
from django.shortcuts import get_object_or_404

from crispy_forms.layout import Field, Layout, Submit, Div

from .models import Host, Grain, Role, SafeAccessControl, Safe, Secret, Vault
from dewey.core.forms import CrispyMixin


class HostSafeAccessForm(CrispyMixin, forms.Form):
    safe = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(HostSafeAccessForm, self).__init__(*args, **kwargs)
        self.fields['host'] = forms.ChoiceField(choices=Host.objects.order_by('hostname').values_list('id', 'hostname'))
        self.helper.layout = Layout(
            Field('safe'),
            Field('host'),
            Div(
                Submit('submit', 'add host', css_class='btn btn-sm btn-default'),
                css_class='col-md-9 offset-md-3'
            ),
        )

    class Meta:
        model = SafeAccessControl
        fields = ('safe', 'acl_object')


class RoleSafeAccessForm(CrispyMixin, forms.Form):
    safe = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(RoleSafeAccessForm, self).__init__(*args, **kwargs)
        self.fields['role'] = forms.ChoiceField(choices=Role.objects.order_by('name').values_list('id', 'name'))
        self.helper.layout = Layout(
            Field('role'),
            Field('safe'),
            Div(
                Submit('submit', 'add role', css_class='btn btn-sm btn-default'),
                css_class='col-md-9 offset-md-3'
            )
        )

    class Meta:
        model = SafeAccessControl
        fields = ('safe', 'acl_object')


class SecretMixin(forms.Form):
    name = forms.CharField()
    secret = forms.CharField(widget=forms.Textarea)


class SecretUpdateForm(CrispyMixin, SecretMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SecretUpdateForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('name'),
            Field('secret'),
            Div(
                Submit('submit', 'save', css_class='btn btn-sm btn-primary'),
                css_class='col-md-9 offset-md-3'
            )
        )

    class Meta:
        model = Secret
        fields = ('name', 'secret')


class SecretCreateMixin(SecretMixin, CrispyMixin):
    redirect = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super(SecretCreateMixin, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('name'),
            Field('safe'),
            Field('secret'),
            Field('redirect'),
            Div(
                Submit('submit', 'save', css_class='btn btn-sm btn-default'),
                css_class='col-md-9 offset-md-3'
            )
        )

    def clean(self):
        cleaned = super(SecretCreateMixin, self).clean()
        safe = get_object_or_404(Safe, id=self.data.get('safe'))
        if Secret.objects.filter(name=cleaned['name'], safe=safe):
            raise forms.ValidationError('secret with that name already exists in {}'.format(safe.name))
        if not re.match(r'^[\w.-]+$', cleaned['name']):
            raise forms.ValidationError('secret names can only contain letters, numbers, hyphens, and periods')
        return cleaned

    class Meta:
        model = Secret
        fields = ('name', 'secret')


class SecretAddForm(SecretCreateMixin, forms.ModelForm):
    safe = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Secret
        fields = ('name', 'secret')


class SafeUpdateForm(CrispyMixin, forms.ModelForm):
    name = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(SafeUpdateForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('name'),
            Div(
                Submit('submit', 'save', css_class='btn btn-sm btn-primary'),
                css_class='col-md-9 offset-md-3'
            )
        )

    class Meta:
        model = Safe
        fields = ('name',)


class SafeCreateForm(CrispyMixin, forms.ModelForm):
    name = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(SafeCreateForm, self).__init__(*args, **kwargs)
        self.fields['vault'] = forms.ChoiceField(choices=Vault.objects.order_by('name').values_list('id', 'name'))
        self.helper.form_action = 'safe_list'
        self.helper.layout = Layout(
            Field('name'),
            Field('vault'),
            Div(
                Submit('submit', 'save', css_class='btn btn-sm btn-primary'),
                css_class='col-md-9 offset-md-3'
            )
        )

    class Meta:
        model = Safe
        fields = ('name',)


class GrainCreateForm(CrispyMixin, forms.ModelForm):
    host = forms.CharField(widget=forms.HiddenInput)
    name = forms.CharField()
    value = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(GrainCreateForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('name'),
            Field('value'),
            Div(
                Submit('submit', 'save', css_class='btn btn-sm btn-primary'),
                css_class='col-md-9 offset-md-3'
            )
        )

    class Meta:
        model = Grain
        fields = ['host', 'name', 'value']

    def clean_host(self):
        host_id = self.cleaned_data['host']
        return Host.objects.get(id=host_id)
