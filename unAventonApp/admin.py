from django.apps import apps
from django.contrib import admin

#agrega dinamicamente todos los modelos de la app

app_models = apps.get_app_config('unAventonApp').get_models()
for model in app_models:
    admin.site.register(model)
