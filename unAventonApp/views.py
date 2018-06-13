from django.shortcuts import render, HttpResponseRedirect,Http404,redirect
from django.contrib.auth import logout as __logout, login as __login, authenticate
from django.contrib.auth.models import User
from .models import Usuario, ViajeCopiloto, Viaje
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
    context = {
        'viajes' :  ViajeCopiloto.objects.filter(usuario=request.user.usuario)
    }
    print(context)
    return render(request, 'unAventonApp/viajes_inscriptos.html', context)

@login_required
def buscar_viajes(request):
    return render(request, 'unAventonApp/buscar_viajes.html')


@login_required
def mis_viajes(request):
    context = {
        'viajes': {
            'semanales': [],
            'diarios': [],
            'unicos': []
        }
    }
    context['viajes']['semanales'] = request.user.usuario.get_viajes_semanales_activos()
    context['viajes']['diarios'] = request.user.usuario.get_viajes_diarios_activos()
    context['viajes']['unicos'] = request.user.usuario.get_viajes_unicos_activos()
    usuario = request.user.usuario
    context['get_autos'] = [auto.asJson() for auto in usuario.get_autos()]
    context['get_cuentas_bancarias'] = [cuenta.asJson() for cuenta in usuario.get_cuentas_bancarias()]

    return render(request, 'unAventonApp/mis_viajes.html', context)

@login_required
def mis_viajes_finalizados(request):
    #TODO
    context = {
        'viajes': Viaje.objects.filter(activo=True)
    }
    return render(request, 'unAventonApp/mis_viajes_finalizados.html',context )


@login_required
def mi_perfil(request):
    return render(request, 'unAventonApp/configuracion_de_la_cuenta.html')


@login_required
def detalle_de_publicacion_del_viaje(request, id):
    if request.method == 'POST':
        pass

    return render(request, 'unAventonApp/detalle_de_publicacion_viaje.html')

@login_required
def crear_viaje(request):
    context = {}
    usuario = Usuario.objects.get(user=request.user)
    context['get_autos'] = [auto.asJson() for auto in usuario.get_autos()]
    context['get_cuentas_bancarias'] = [cuenta.asJson() for cuenta in usuario.get_cuentas_bancarias()]
    return render(request, 'unAventonApp/crear_viaje.html', context)


@login_required
def upload_foto(request):
    if request.method == 'POST':
        usuario = request.user.usuario
        file = request.FILES['files']
        if str(file).lower().endswith(('.jpg', '.png', '.jpeg', '.gif',)) == True:
            usuario.foto_de_perfil.delete()
            usuario.foto_de_perfil = file
            usuario.save()
        return redirect('miPerfil')
    else:
        raise Http404