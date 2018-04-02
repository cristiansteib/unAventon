from django.urls import path
from .views import index, login, signIn, logout, signInRegister

name = 'unAventonApp'
urlpatterns = [
    path('', index, name='index'),
    path('login', login, name='login'),
    path('signin', signIn, name='signin'),
    path('signinReg', signInRegister, name='signin_register'),
    path('logout',logout, name='logout')

]
