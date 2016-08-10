from django import forms

from crispy_forms.layout import Field, Layout, Submit, Div

from .models import Host, Role, SafeAccessControl, Safe, Secret
from dewey.forms import CrispyMixin


class HostSafeAccessForm(CrispyMixin, forms.Form):
    safe = forms.CharField(widget=forms.HiddenInput)
    host = forms.ChoiceField(choices=Host.objects.order_by('hostname').values_list('id', 'hostname'))

    def __init__(self, *args, **kwargs):
        super(HostSafeAccessForm, self).__init__(*args, **kwargs)
        self.helper.form_action = 'safe_access_create'
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
    role = forms.ChoiceField(choices=Role.objects.order_by('name').values_list('id', 'name'))

    def __init__(self, *args, **kwargs):
        super(RoleSafeAccessForm, self).__init__(*args, **kwargs)
        self.helper.form_action = 'safe_access_create'
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


class SecretMixin(object):
    name = forms.CharField()
    secret = forms.CharField(widget=forms.Textarea)


class UpdateSecretForm(CrispyMixin, SecretMixin, forms.ModelForm):
    verb = forms.CharField(widget=forms.HiddenInput, initial='update')

    def __init__(self, *args, **kwargs):
        super(UpdateSecretForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('name'),
            Field('secret'),
            Field('verb'),
            Div(
                Submit('submit', 'save', css_class='btn btn-sm btn-primary'),
                css_class='col-md-9 offset-md-3'
            )
        )

    class Meta:
        model = Secret
        fields = ('name', 'secret')


class CreateSecretForm(CrispyMixin, SecretMixin, forms.ModelForm):
    safe = forms.ChoiceField(choices=Safe.objects.order_by('name').values_list('id', 'name'))

    def __init__(self, *args, **kwargs):
        super(CreateSecretForm, self).__init__(*args, **kwargs)
        self.helper.form_action = 'secrets'
        self.helper.layout = Layout(
            Field('name'),
            Field('safe'),
            Field('secret'),
            Div(
                Submit('submit', 'save', css_class='btn btn-sm btn-default'),
                css_class='col-md-9 offset-md-3'
            )
        )

    class Meta:
        model = Secret
        fields = ('name', 'secret')
