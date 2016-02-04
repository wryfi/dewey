from django.conf.urls import patterns, url

urlpatterns  = patterns('hosts.views',
    url(r'^nagios/hosts/$', 'nagios_hosts', name='nagios_hosts'),
    url(r'nagios/hosts/md5/', 'nagios_hosts_md5', name='nagios_hosts_md5'),
    url(r'^nagios/hostgroups/$', 'nagios_hostgroups', name='nagios_hostgroups'),
    url(r'^nagios/hostgroups/md5/$', 'nagios_hostgroups_md5', name='nagios_hostgroups_md5'),
)