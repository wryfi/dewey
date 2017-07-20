from django.conf.urls import url

from dewey.plos import views


urlpatterns = [
    url(r'directory/users', views.manage_users, name='users'),
    url(r'directory/user/(?P<username>\w+)/$', views.manage_user, name='user'),
]