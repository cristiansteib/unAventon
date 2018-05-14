from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth import logout as __logout, login as __login, authenticate
from django.contrib.auth.models import User
from .models import Usuario, Viaje, Tarjeta
from .modules.Git import Git
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

def baseContext():
    return {
        'footer': {}
    }


def index(request):
    context = baseContext()
    return render(request, 'unAventonApp/index.html', context)


def login(request):
    context = baseContext()
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            ## se autentico bien
            __login(request, user)

            return HttpResponseRedirect(request.GET.get('next','/'))
        else:
            ## algun dato esta mal
            context['error'] = {'message':'E-mail inexistente, o contraseña invalida'}

    return render(request, 'unAventonApp/login.html', context)


def signIn(request):
    return render(request, 'unAventonApp/signIn.html')


def signInRegister(request):
    if request.method == 'POST':
        try:
            r = request.POST
            user = User.objects.create_user(r['email'], r['email'], r['password'])
            Usuario.objects.create(user=user, nombre=r['firstName'], apellido=r['lastName'], dni=r['dni'], fechaDeNacimiento=r['birthDay'])
            return render(request, 'unAventonApp/signin_success.html')
        except IntegrityError:
            context = {'error':'Ese usuario ya esta registrado'}
            return render(request,'unAventonApp/signIn.html', context)

    return HttpResponseRedirect('signin')


def logout(request):
    __logout(request)
    return HttpResponseRedirect('/')

@login_required
def viajes_inscriptos(request):
    return render(request, 'unAventonApp/viajes_inscriptos.html')

@login_required
def buscar_viajes(request):
    return render(request, 'unAventonApp/buscar_viajes.html')


@login_required
def mis_viajes(request):
    return render(request, 'unAventonApp/mis_viajes.html')

@login_required
def mi_perfil(request):
    return render(request, 'unAventonApp/configuracion_de_la_cuenta.html')

@login_required
def crear_viaje(request):
    context = {}
    usuario = Usuario.objects.get(user=request.user)
    context['autos'] = [auto.asJson() for auto in usuario.autos()]
    context['cuentas_bancarias'] = [cuenta.asJson() for cuenta in usuario.cuentas_bancarias()]

    return render(request, 'unAventonApp/crear_viaje.html', context)
