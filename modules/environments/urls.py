from django.conf.urls import patterns, url

from environments.views import rest as rest_views
from environments.views import frontend as frontend_views

urlpatterns  = [
    url(r'^nagios/hosts/$', rest_views.nagios_hosts, name='nagios_hosts'),
    url(r'^nagios/hosts/md5/', rest_views.nagios_hosts_md5, name='nagios_hosts_md5'),
    url(r'^nagios/hostgroups/$', rest_views.nagios_hostgroups, name='nagios_hostgroups'),
    url(r'^nagios/hostgroups/md5/$', rest_views.nagios_hostgroups_md5, name='nagios_hostgroups_md5'),
    url(r'^hosts/list/$', frontend_views.HostListView.as_view(), {'template': 'environments/hosts.html'}, name='hosts'),
    url(r'^hosts/detail/(?P<hostname>.*)/$', frontend_views.HostDetailView.as_view(), name='host_detail'),
    url(r'^safes/detail/(?P<name>[\w.-]+)/$', frontend_views.SafeDetailView.as_view(), name='safe_detail'),
    url(r'^safes/access/delete/$', frontend_views.delete_safe_access, name='safe_access_delete'),
    url(r'^safes/access/create/$', frontend_views.create_safe_access, name='safe_access_create'),
    url(r'^secrets/list/$', frontend_views.SecretListView.as_view(), name='secrets'),
]