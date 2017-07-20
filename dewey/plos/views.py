import re

from django.http import Http404
from django.shortcuts import render
from plop.directory import users, groups

from dewey.plos.forms import DirectoryUserModifyForm


def manage_users(request):
    core_groups = []
    extra_groups = []
    unix_groups = groups.list_unix_groups()
    for group in unix_groups:
        group_users = [users.get_user(distinguished_name=DN) for DN in group['member']]
        if re.match('^.*-core-.*', group['cn'][0]):
            core_groups.append({'name': group['sAMAccountName'][0], 'users': group_users})
        elif re.match(r'^.*-extra-.*', group['cn'][0]):
            extra_groups.append({'name': group['sAMAccountName'][0], 'users': group_users})
    return render(request, 'plos/manage_users.html', {'core_groups': core_groups, 'extra_groups': extra_groups})


def manage_user(request, username):
    user = users.get_user(username)
    if not user:
        raise Http404
    if request.method == 'GET':
        initial = {'username': username}
        try:
            initial['uid'] = user['uidNumber'][0]
        except (KeyError, IndexError):
            pass
        try:
            initial['ssh_key'] = user['altSecurityIdentities'][0]
        except (KeyError, IndexError):
            pass
        form = DirectoryUserModifyForm(initial=initial)
        return render(request, 'plos/manage_user.html', {'form': form, 'user': user})
    if request.method == 'POST':
        form = DirectoryUserModifyForm(request.POST)
        if form.is_valid():
            key_type, key_value, key_comment = form.cleaned_data['ssh_key'].split()
            users.set_ssh_key(username, key_type, key_value, key_comment)
            users.set_uid(username, form.cleaned_data['uid'])