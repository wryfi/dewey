from django.conf.urls import url

from rest_framework_nested import routers

from dewey.salt import api, views
from dewey.environments.views import rest as enviro_views


router = routers.SimpleRouter()
router.register(r'salt/changes', api.ChangeViewSet, base_name='salt-changes')
router.register(r'salt/highstates', api.HighstateViewSet, base_name='salt-highstates')
# TODO: remove deprecated 'salt/hosts' api endpoint
# the 'salt/hosts' url is officially deprecated and will be removed in a future release
router.register(r'salt/hosts', enviro_views.SaltHostViewSet, base_name='salt-hosts')

events_router = routers.NestedSimpleRouter(router, 'salt/highstates', lookup='highstate')
events_router.register(r'changes', api.StateChangeViewSet, base_name='highstate-changes')
events_router.register(r'errors', api.StateErrorViewSet, base_name='highststate-errors')

# TODO: remove deprecated 'salt/hosts' api endpoint
# see deprecation note above (these lines will be removed in a future release)
hosts_router = routers.NestedSimpleRouter(router, 'salt/hosts', lookup='host')
hosts_router.register(r'secrets', enviro_views.SaltHostSecretsViewSet, base_name='host-secrets')

urlpatterns = [
    url(r'^$', views.highstates_list, name='highstates_index'),
    url(r'^highstate/(?P<jid>\d+)/$', views.highstate_detail, name='highstate_detail'),
    url(r'^highstates/$', views.highstates_list, name='highstates_list'),
    url(r'^highstates/changes/$', views.statechanges_list, name='statechanges_list'),
    url(r'^change/(?P<id>\d+)/$', views.change_detail, name='change_detail'),
    url(r'^highstates/errors/$', views.stateerrors_list, name='stateerrors_list'),
]