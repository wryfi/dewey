import re

from django.shortcuts import render
from plop.directory import users, groups


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

