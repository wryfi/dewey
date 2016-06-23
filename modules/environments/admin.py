from django.apps import apps
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.contrib.contenttypes.admin import GenericTabularInline


for model in apps.get_app_config('environments').get_models():
    admin.site.register(model)
