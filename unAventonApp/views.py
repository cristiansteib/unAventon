from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth import logout as __logout, login as __login, authenticate
from django.contrib.auth.models import User
from .modules.Git import Git
from django.conf import settings

def index(request):
    context = {
        'footer' : {
            'branch' : Git(settings.BASE_DIR).getActuallBranch()
        }
    }
    return render(request, 'unAventonApp/index.html', context)


def login(request):
    context = {}
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            ## se autentico bien
            __login(request, user)
            return HttpResponseRedirect('/')
        else:
            ## algun dato esta mal
            context['error'] = True

    return render(request, 'unAventonApp/login.html', context)


def signIn(request):
    return render(request, 'unAventonApp/signIn.html')


def signInRegister(request):
    if request.method == 'POST':
        r = request.POST
        user = User.objects.create_user(r['email'],r['email'],r['password'])
        #todo   email email????'''
        #todo verificar si ya existe el correo

        user.save()
        return render(request, 'unAventonApp/signin_success.html')
    return HttpResponseRedirect('signin')

def logout(request):
    __logout(request)
    return HttpResponseRedirect('/')
