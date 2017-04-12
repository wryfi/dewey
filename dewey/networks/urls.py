from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'addresses/available/$', views.available_addresses, name='networks_addresses_available'),
    url(r'addresses/assigned/$', views.assignments_csv, name='networks_addresses_assigned_csv'),
]

