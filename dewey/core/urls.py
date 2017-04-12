from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.conf import settings

from rest_framework_nested import routers

from .forms import CrispyAuthenticationForm
from dewey.hardware import views as hardware_views
from dewey.environments import urls as enviro_urls
from dewey.environments.views import rest as enviro_views
from dewey.environments.views import frontend as enviro_frontend
from dewey.networks import urls as networks_urls

router = routers.DefaultRouter()
router.trailing_slash = r'/?'

router.register(r'salt/hosts', enviro_views.SaltHostViewSet, base_name='salt-hosts')

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
    url(r'^api/', include(salthosts_router.urls)),
    url(r'^api/salt/discovery/(?P<environment>\w+)/$', enviro_views.salt_discovery_view, name='salt-discovery'),
    url(r'^api/salt/secrets/(?P<environment>[\w]+)/(?P<role>[\w.-]+)/$', enviro_views.role_secrets, name='role-secrets'),
    url(r'^hosts/', include(enviro_urls)),
    url(r'^environments/', include(enviro_urls)),
    url(r'^export/secrets', enviro_views.export_secrets, name='export-secrets'),
    url(r'^networks/', include(networks_urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

