from django import forms
from django.contrib.auth.forms import AuthenticationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, HTML, Layout, Submit


class CrispyMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CrispyMixin, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.html5_required = True
        self.helper.error_text_inline = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'


class AuthCrispyMixin(CrispyMixin):
    def __init__(self, *args, **kwargs):
        super(AuthCrispyMixin, self).__init__(*args, **kwargs)
        self.helper.field_class = 'col-xs-12 col-sm-8 col-sm-offset-2'


class CrispyAuthenticationForm(AuthCrispyMixin, AuthenticationForm):
    '''
    AuthenticationForm with crispy helper for bootstrap
    '''

    def __init__(self, *args, **kwargs):
        super(CrispyAuthenticationForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('username', placeholder='username'),
            Field('password', placeholder='password'),
            Div(
                Div(
                    Submit('submit', 'Sign In', css_class='btn-default'),
                    css_class='col-xs-2 col-sm-offset-2'
                ),
                css_class='row'
            )
        )
        self.helper.form_show_labels = False
