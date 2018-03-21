from django.urls import path

from . import views
name = 'unAventonApp'
urlpatterns = [
    path('',views.index,name='index'),
]