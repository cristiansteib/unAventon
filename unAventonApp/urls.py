from django.urls import path
from .views import index, login, signIn

name = 'unAventonApp'
urlpatterns = [
    path('', index, name='index'),
    path('login', login, name='login'),
    path('signin', signIn, name='signin'),
]
