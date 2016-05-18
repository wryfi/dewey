"""dewey URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

from rest_framework_nested import routers

from hardware import views as hardware_views
from hosts import views as hosts_views
from hosts import urls as hosts_urls


router = routers.DefaultRouter()
router.register(r'hosts', hosts_views.HostViewSet)
router.register(r'host-roles', hosts_views.HostRoleViewSet)
router.register(r'clusters', hosts_views.ClusterViewSet)
router.register(r'servers', hardware_views.ServerViewSet)

hosts_router = routers.NestedSimpleRouter(router, r'hosts', lookup='host')
hosts_router.register(r'roles', hosts_views.HostRoleViewSet, base_name='host-roles-nested')

parent_router = routers.NestedSimpleRouter(router, r'hosts', lookup='host')
parent_router.register(r'parent', hosts_views.HostParentViewSet, base_name='host-parent')

virtual_machines_router = routers.NestedSimpleRouter(router, r'hosts', lookup='host')
virtual_machines_router.register(r'virtual_machines', hosts_views.HostVirtualMachineViewSet, base_name='host-virtual-machines')

address_assignments_router = routers.NestedSimpleRouter(router, r'hosts', lookup='host')
address_assignments_router.register(r'address_assignments', hosts_views.HostAddressAssignmentViewSet, base_name='host-address-assignments')

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api/', include(hosts_router.urls)),
    url(r'^api/', include(parent_router.urls)),
    url(r'^api/', include(virtual_machines_router.urls)),
    url(r'^api/', include(address_assignments_router.urls)),
    url(r'^api/hosts/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)/$', hosts_views.HostRelationshipView.as_view(), name='host-relationships'),
    url(r'^api/salt/hosts/$', hosts_views.SaltHostViewSet.as_view({'get': 'list'})),
    url(r'^api/salt/discovery/(?P<environment>\w+)/$', hosts_views.salt_discovery_view, name='salt-discovery'),
    #url(r'^api/', hosts_views.HostRelationshipView.as_view()),
    url(r'^hosts/', include(hosts_urls)),
    #url(r'^api/hosts/', include(hosts_rest_urls))
]
