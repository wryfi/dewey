from django.conf.urls import url

from dewey.environments.views import rest as rest_views
from dewey.environments.views import frontend as frontend_views

urlpatterns  = [
    url(r'^nagios/hosts/$', rest_views.nagios_hosts, name='nagios_hosts'),
    url(r'^nagios/hosts/md5/', rest_views.nagios_hosts_md5, name='nagios_hosts_md5'),
    url(r'^nagios/hostgroups/$', rest_views.nagios_hostgroups, name='nagios_hostgroups'),
    url(r'^nagios/hostgroups/md5/$', rest_views.nagios_hostgroups_md5, name='nagios_hostgroups_md5'),
    url(r'^hosts/$', frontend_views.hosts_list, {'template': 'environments/hosts.html'}, name='hosts'),
    url(r'^hosts/(?P<hostname>.*)/grains/create/$', frontend_views.host_grain_create, name='host_grain_create'),
    url(r'^hosts/(?P<hostname>.*)/grains/delete/$', frontend_views.host_grain_delete, name='host_grain_delete'),
    url(r'^hosts/(?P<hostname>.*)/$', frontend_views.host_detail, name='host_detail'),
    url(r'^safes/$', frontend_views.safes_list, name='safe_list'),
    url(r'^safes/(?P<name>[\w.-]+)/$', frontend_views.safe_detail, name='safe_detail'),
    url(r'^safes/(?P<name>[\w.-]+)/delete/$', frontend_views.safe_delete, name='safe_delete'),
    url(r'^safes/(?P<name>[\w.-]+)/access/create/host$', frontend_views.safe_access_create_host, name='safe_access_create_host'),
    url(r'^safes/(?P<name>[\w.-]+)/access/create/role$', frontend_views.safe_access_create_role, name='safe_access_create_role'),
    url(r'^safes/(?P<name>[\w.-]+)/access/delete/host/$', frontend_views.safe_access_delete_host, name='safe_access_delete_host'),
    url(r'^safes/(?P<name>[\w.-]+)/access/delete/role/$', frontend_views.safe_access_delete_role, name='safe_access_delete_role'),
    url(r'^secrets/$', frontend_views.secrets_list, name='secrets'),
    url(r'^secrets/(?P<safe>[\w.-]+)/create/$', frontend_views.secret_create, name='secret_create'),
    url(r'^secrets/(?P<safe>[\w.-]+)/(?P<name>[\w.-]+)/$', frontend_views.secret_detail, name='secret_detail'),
    url(r'^secrets/(?P<safe>[\w.-]+)/(?P<name>[\w.-]+)/delete/$', frontend_views.secret_delete, name='secret_delete'),
    url(r'^secrets/(?P<safe>[\w.-]+)/(?P<name>[\w.-]+)/update/$', frontend_views.secret_update, name='secret_update'),
]