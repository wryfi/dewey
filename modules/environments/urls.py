from django.conf.urls import patterns, url

from environments.views import rest as rest_views
from environments.views import frontend as frontend_views

urlpatterns  = [
    url(r'^nagios/hosts/$', rest_views.nagios_hosts, name='nagios_hosts'),
    url(r'^nagios/hosts/md5/', rest_views.nagios_hosts_md5, name='nagios_hosts_md5'),
    url(r'^nagios/hostgroups/$', rest_views.nagios_hostgroups, name='nagios_hostgroups'),
    url(r'^nagios/hostgroups/md5/$', rest_views.nagios_hostgroups_md5, name='nagios_hostgroups_md5'),
    url(r'^hosts/$', frontend_views.hosts_list, {'template': 'environments/hosts.html'}, name='hosts'),
    url(r'^hosts/(?P<hostname>.*)/$', frontend_views.host_detail, name='host_detail'),
    url(r'^safes/$', frontend_views.safes_list, name='safe_list'),
    url(r'^safes/(?P<name>[\w.-]+)/$', frontend_views.safe_detail, name='safe_detail'),
    url(r'^safe-access/delete/$', frontend_views.delete_safe_access, name='safe_access_delete'),
    url(r'^safe-access/create/$', frontend_views.create_safe_access, name='safe_access_create'),
    url(r'^secrets/(?P<safe>[\w.-]+)/(?P<name>[\w.-]+)/$', frontend_views.secret_detail, name='secret_detail'),
    url(r'^secrets/$', frontend_views.secrets_list, name='secrets'),
]