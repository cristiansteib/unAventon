from django.shortcuts import render, HttpResponseRedirect, Http404, redirect
from django.contrib.auth import logout as __logout, login as __login, authenticate
from django.contrib.auth.models import User
from .models import Usuario, ViajeCopiloto, Viaje, ConversacionPublica
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone
import datetime
from . import mailer

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

            return HttpResponseRedirect(request.GET.get('next', '/'))
        else:
            ## algun dato esta mal
            context['error'] = {'message': 'E-mail inexistente, o contraseña invalida'}

    return render(request, 'unAventonApp/login.html', context)


def signIn(request):
    return render(request, 'unAventonApp/signIn.html')


def signInRegister(request):
    if request.method == 'POST':
        try:
            r = request.POST
            user = User.objects.create_user(r['email'], r['email'], r['password'])
            usuario = Usuario.objects.create(user=user, nombre=r['firstName'], apellido=r['lastName'], dni=r['dni'],
                                   fechaDeNacimiento=r['birthDay'])
            mailer.send_email(user.email,
                              subject='Bienvenido {0} {1} =) '.format(usuario.nombre, usuario.apellido),
                              message='Muchas gracias por ser parte de nuestra comunidad.\n En unAventon te ayudaremos'
                                      ' a encontrar viajes seguros y confiables en cuestion de segundos')

            return render(request, 'unAventonApp/signin_success.html')
        except IntegrityError:
            context = {'error': 'Ese usuario ya esta registrado'}
            return render(request, 'unAventonApp/signIn.html', context)

    return HttpResponseRedirect('signin')


def viaje(request, id, timestamp):
    # renderiza la vista para ver los datos del viaje
    context = {}
    viaje = Viaje.objects.get(pk=id)
    fecha = timezone.datetime.fromtimestamp(int(timestamp))
    context['viaje'] = viaje.datos_del_viaje_en_fecha(fecha)
    try:
        vc = ViajeCopiloto.objects.get(usuario=request.user.usuario, viaje=viaje, fecha_del_viaje=fecha)
        context['copiloto_confirmado'] = vc.estaConfirmado
    except:
        context['copiloto_confirmado'] = -1 #todavia no mando solicitud

    context['timestamp'] = timestamp
    context['conversacion_publica'] = viaje.get_conversacion_publica()
    context['es_piloto'] = viaje.auto.usuario.pk == request.user.usuario.pk

    return render(request, 'unAventonApp/ver_datos_del_viaje.html', context)


def context_calificaciones_del_usuario(usuario):
    context = {}
    context['usuario'] = usuario
    context['calificaciones_como_piloto'] = usuario.get_calificacion_como_piloto()
    context['calificaciones_como_copiloto'] = usuario.get_calificacion_como_copiloto()
    return context


def ver_calificaciones(request):
    usuario = request.user.usuario
    context = context_calificaciones_del_usuario(usuario)
    return render(request, 'unAventonApp/detalle_de_calificacion.html', context)


def ver_calificaciones_de_usuario(request, id):
    usuario = Usuario.objects.get(pk=id)
    context = context_calificaciones_del_usuario(usuario)
    return render(request, 'unAventonApp/detalle_de_calificacion.html', context)


@login_required
def agregar_pregunta_conversacion_publica(request):
    id_viaje = request.POST['id_viaje']
    timestamp = request.POST['fecha_hora_unix']
    ConversacionPublica.objects.create(
        viaje=Viaje.objects.get(pk=id_viaje),
        usuario=request.user.usuario,
        pregunta=request.POST['pregunta'],
        fechaHoraPregunta=datetime.datetime.now()
    )
    return redirect('viaje', id=id_viaje, timestamp=timestamp)


def logout(request):
    __logout(request)
    print('logout')
    return redirect('index')


@login_required
def viajes_inscriptos(request):
    context = {
        'viajes': ViajeCopiloto.objects.filter(usuario=request.user.usuario)
    }
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
    # TODO: agregar solo los viajes finalizados. @seba
    # el tema es asi, como tenemos un solo registro para los viajes que se repiten
    # entonce tenemos que generar por cada copilotoViaje que este en estado "finalizado",
    # la data del viaje, lo que recauda la app, lo que se retorna al usuario y mas datos
    # que son calculados en realidad segun la repeticio y para X fecha,
    # quiza se puede hacer un metodo sobre el Viaje, que reciba como param una fecha y
    # retorne la data generada para esa fecha.
    # o directamente aca, total en otro lado no se va a usar.
    # ViajeCopiloto tiene el metodo get_estado(). se deberian agrupar por fechas y generar la data
    # sese ya se muchos comentarios redundantes ajaj :D

    context = {
        'viajes': []
    }

    # busca los viajes finalizados con copilotos confirmados
    viajes_copilotos = list(ViajeCopiloto.objects.filter(
        fecha_del_viaje__lte=timezone.now(),
        estaConfirmado=True
    ))

    # aplico un DISTINCT caserito porque no functiona con sqlite
    x = set()
    for vc in viajes_copilotos:
        v = (vc.fecha_del_viaje, vc.viaje.pk)
        if v in x:
            viajes_copilotos.remove(vc)
        else:
            x.add(v)

    print(viajes_copilotos)
    # agrega los datos de cada viaje encontrado
    for viaje_copiloto in viajes_copilotos:
        viaje = viaje_copiloto.viaje
        context['viajes'].append(viaje.datos_del_viaje_en_fecha(viaje_copiloto.fecha_del_viaje))

    return render(request, 'unAventonApp/mis_viajes_finalizados.html', context)


@login_required
def mi_perfil(request):
    return render(request, 'unAventonApp/configuracion_de_la_cuenta.html')


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
            if not str(usuario.foto_de_perfil.name).count('default-user.png'):
                usuario.foto_de_perfil.delete()
            usuario.foto_de_perfil = file
            usuario.save()
        return redirect('miPerfil')
    else:
        raise Http404
