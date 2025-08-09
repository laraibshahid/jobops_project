from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered

app_config = apps.get_app_config('users')

for model in app_config.get_models():
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
