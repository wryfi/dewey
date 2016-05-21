from django.conf.urls import include, url
from django.contrib import admin

from rest_framework_nested import routers

from hardware import views as hardware_views
from hosts import views as hosts_views
from hosts import urls as hosts_urls


router = routers.DefaultRouter()
# for hostname lookups in URLs to work reliably, we abandon format suffixes
router.include_format_suffixes = False
router.register(r'clusters', hosts_views.ClusterViewSet)
router.register(r'host-roles', hosts_views.HostRoleViewSet)
router.register(r'hosts', hosts_views.HostViewSet)
router.register(r'network-devices', hardware_views.NetworkDeviceViewSet)
router.register(r'networks', hosts_views.NetworkViewSet)
router.register(r'pdus', hardware_views.PowerDistributionUnitViewSet)
router.register(r'salt/hosts', hosts_views.SaltHostViewSet, base_name='salt-hosts')
router.register(r'servers', hardware_views.ServerViewSet)

hosts_router = routers.NestedSimpleRouter(router, r'hosts', lookup='host')
hosts_router.register(r'roles', hosts_views.HostRoleViewSet, base_name='host-roles-nested')
hosts_router.register(r'parent', hosts_views.HostParentViewSet, base_name='host-parent')
hosts_router.register(r'virtual_machines', hosts_views.HostVirtualMachineViewSet, base_name='host-virtual-machines')
hosts_router.register(r'address_assignments', hosts_views.HostAddressAssignmentViewSet, base_name='host-address-assignments')

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api/', include(hosts_router.urls)),
    url(r'^api/hosts/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)/$', hosts_views.HostRelationshipView.as_view(), name='host-relationships'),
    url(r'^api/salt/discovery/(?P<environment>\w+)/$', hosts_views.salt_discovery_view, name='salt-discovery'),
    url(r'^hosts/', include(hosts_urls)),
]
