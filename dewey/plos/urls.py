from django.conf.urls import url

from dewey.plos import views


urlpatterns = [
    url(r'directory/users', views.manage_users, name='users')
]