from django.conf.urls import patterns, url

from hosts import views

urlpatterns  = [
    url(r'^nagios/hosts/$', views.nagios_hosts, name='nagios_hosts'),
    url(r'nagios/hosts/md5/', views.nagios_hosts_md5, name='nagios_hosts_md5'),
    url(r'^nagios/hostgroups/$', views.nagios_hostgroups, name='nagios_hostgroups'),
    url(r'^nagios/hostgroups/md5/$', views.nagios_hostgroups_md5, name='nagios_hostgroups_md5'),
]