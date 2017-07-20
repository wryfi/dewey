from crispy_forms.layout import Layout, Field, Div, Submit
from django import forms

from dewey.core.forms import CrispyMixin
from dewey.core.exceptions import InvalidKeyError
from dewey.core.utils import validators

from plop.directory.users import get_user, list_used_uids


class DirectoryUserModifyForm(CrispyMixin):
    username = forms.CharField(disabled=True)
    uid = forms.IntegerField()
    ssh_key = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(DirectoryUserModifyForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('username'),
            Field('uid'),
            Field('ssh_key'),
            Div(
                Submit('submit', 'update', css_class='btn btn-sm btn-default'),
                css_class='col-md-9 offset-3'
            )
        )

    class Meta:
        fields = ('username', 'uid', 'ssh_key')

    def clean_ssh_key(self):
        cleaned = super(DirectoryUserModifyForm, self).clean()
        key_comment = cleaned['username']
        key_split = cleaned['ssh_key'].split()
        if len(key_split) < 2:
            raise forms.ValidationError('keys must have at least type and value')
        key_type = key_split[0]
        key_value = key_split[1]
        try:
            is_valid = validators.validate_openssh_key(key_type, key_value)
        except InvalidKeyError as exception:
            raise forms.ValidationError(exception.message)
        if is_valid:
            return '{} {} {}'.format(key_type, key_value, key_comment)

    def clean_uid(self):
        cleaned = super(DirectoryUserModifyForm, self).clean()
        uid = cleaned['uid']
        directory_user = get_user(cleaned['username'])
        if not directory_user:
            raise forms.ValidationError('could not find directory account for {}'.format(cleaned['username']))
        if uid == int(directory_user['uidNumber']):
            return uid
        taken = list_used_uids()
        if cleaned['uid'] in taken:
            raise forms.ValidationError('uid {} is already in use'.format(cleaned['uid']))
        return uid
