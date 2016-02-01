from django.conf.urls import patterns, url

urlpatterns  = patterns('hosts.views',
    url(r'^nagios/hosts/$', 'nagios_hosts', name='nagios_hosts'),
    url(r'^nagios/hostgroups/$', 'nagios_hostgroups', name='nagios_hostgroups'),
)