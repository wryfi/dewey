from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r'^', views.HostViewSet)

urlpatterns = [
    #url(r'^hosts/$', views.HostList.as_view(), name='host-list'),
    #url(r'^hosts/(?P<hostname>[\w.-]+)/$', views.HostDetail.as_view(), name='host-detail'),
    #url(r'^', include(router.urls)),
    #url(r'^roles/$', views.HostRoleList.as_view(), name='hostrole-list'),
    #url(r'^roles/(?P<pk>\d+)/$', views.HostRoleDetail.as_view(), name='hostrole-detail')
]

#urlpatterns = format_suffix_patterns(urlpatterns)