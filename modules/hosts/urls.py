from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
    url(r'^roles/$', views.HostRoleList.as_view()),
    url(r'^roles/(?P<pk>\d+)/$', views.HostRoleDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)