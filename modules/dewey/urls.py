from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.conf import settings

from rest_framework_nested import routers

from .forms import CrispyAuthenticationForm
from hardware import views as hardware_views
from environments import urls as enviro_urls
from environments.views import rest as enviro_views
from environments.views import frontend as enviro_frontend
from networks import views as networks_views

router = routers.DefaultRouter()
# for hostname lookups in URLs to work reliably, we abandon format suffixes
#router.include_format_suffixes = False
#router.register(r'clusters', enviro_views.ClusterViewSet)
#router.register(r'host-roles', enviro_views.HostRoleViewSet)
router.register(r'hosts', enviro_views.HostViewSet)
#router.register(r'network-devices', hardware_views.NetworkDeviceViewSet)
#router.register(r'networks', networks_views.NetworkViewSet)
#router.register(r'pdus', hardware_views.PowerDistributionUnitViewSet)
router.register(r'salt/hosts', enviro_views.SaltHostViewSet, base_name='salt-hosts')
#router.register(r'servers', hardware_views.ServerViewSet)
#router.register(r'pdus', hardware_views.PowerDistributionUnitViewSet)
#router.register(r'network-devices', hardware_views.NetworkDeviceViewSet)

hosts_router = routers.NestedSimpleRouter(router, r'hosts', lookup='host')
hosts_router.register(r'roles', enviro_views.HostRoleViewSet, base_name='host-roles-nested')
hosts_router.register(r'parent', enviro_views.HostParentViewSet, base_name='host-parent')
hosts_router.register(r'virtual_machines', enviro_views.HostVirtualMachineViewSet, base_name='host-virtual-machines')
hosts_router.register(r'address_assignments', enviro_views.HostAddressAssignmentViewSet, base_name='host-address-assignments')

salthosts_router = routers.NestedSimpleRouter(router, 'salt/hosts', lookup='host')
salthosts_router.register(r'secrets', enviro_views.SaltHostSecretsViewSet, base_name='host-secrets')

urlpatterns = [
    url(r'^$', enviro_frontend.hosts_list, name='index'),
    url(r'^accounts/login/$', auth_views.login, {
            'template_name': 'dewey/login.html',
            'authentication_form': CrispyAuthenticationForm
        }, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, {'template_name': 'dewey/logout.html'}, name='logout'),
    url(r'^accounts/password/reset/request/$', RedirectView.as_view(url=settings.PASSWORD_RESET_URL, permanent=False), name='password_reset'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api/', include(hosts_router.urls)),
    url(r'^api/', include(salthosts_router.urls)),
    url(r'^api/hosts/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)/$', enviro_views.HostRelationshipView.as_view(), name='host-relationships'),
    url(r'^api/salt/discovery/(?P<environment>\w+)/$', enviro_views.salt_discovery_view, name='salt-discovery'),
    url(r'^api/salt/secrets/(?P<environment>[\w]+)/(?P<role>[\w.-]+)/$', enviro_views.role_secrets, name='role-secrets'),
    url(r'^hosts/', include(enviro_urls)),
    url(r'^environments/', include(enviro_urls)),
    url(r'^export/secrets', enviro_views.export_secrets, name='export-secrets'),
]
