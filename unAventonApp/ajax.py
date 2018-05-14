""" Call ajax in this module """
from .models import Usuario, Viaje, Tarjeta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.core import serializers
import json


def neededParams(method_list, *args):
    for value in args:
        if value not in method_list:
            return False
    return True


@login_required
def viajes_activos(request):
    """ retorna todos los viajes activos
    para el usuario logueado """
    data = {}
    try:
        usuario = Usuario.objects.get(user=request.user)
        data['viajes'] = [viaje.asJson() for viaje in usuario.viajesCreadosActivos()]
    except Usuario.DoesNotExist:
        data.setdefault('error', []).append('No exisite un Usuario para el user {0}'.format(request.user))
    return JsonResponse(data)


@login_required
def lista_de_espera_de_copilotos_para_un_viaje(request):
    """ retorna todos los copilotos que estan en la lista de espera
    para un viaje del usuario logueado """
    data = {}
    try:
        viaje_id = request.GET.get('viajeId', None)
        if not viaje_id:
            raise KeyError("viajeId")
        usuario = Usuario.objects.get(user=request.user)
        viaje = Viaje.objects.get(auto__usuario=usuario, id=viaje_id)
        data['lista'] = [obj.asJson() for obj in viaje.copilotos_en_lista_de_espera()]
    except KeyError as e:
        data.setdefault('error', []).append('Falta parametro para el request: {0} '.format(e))
    except Usuario.DoesNotExist:
        data.setdefault('error', []).append('No exisite un Usuario para el user {0}'.format(request.user))
    except Viaje.DoesNotExist:
        data.setdefault('error', []).append('No exisite el viaje {0} para el usuario = {1} '.format(viaje_id, usuario))
    return JsonResponse(data)


@login_required
def lista_de_calificaciones_pendientes_a_copilotos(request):
    data = {}
    try:
        usuario = Usuario.objects.get(user=request.user)
        data['lista'] = [obj.asJson() for obj in usuario.calificacionesPendientesParaCopilotos()]
    except Usuario.DoesNotExist:
        data.setdefault('error', []).append('No exisite un perfil para el user {0}'.format(request.user))
    return JsonResponse(data)


@login_required
def lista_de_calificaciones_pendientes_a_pilotos(request):
    data = {}
    try:
        usuario = Usuario.objects.get(user=request.user)
        data['lista'] = [obj.asJson() for obj in usuario.calificacionesPendientesParaPiloto()]
    except Usuario.DoesNotExist:
        data.setdefault('error', []).append('No exisite un perfil para el user {0}'.format(request.user))
    except TypeError:
        pass
    return JsonResponse(data)

@login_required
def datos_relacionados_al_usuario(request):
    """ Arma un diccionario con los datos del usuario
    y datos utiles de los viajes.
    Todos estos datos son usados para construir la pagina
    con los datos del usuario y tablas.
    """
    data = {}
    try:
        usuario = Usuario.objects.get(user=request.user)
        data['usuario'] = usuario.asJson()
        data['calificacion_como_piloto'] = usuario.calificacionComoPiloto()
        data['calificacion_como_copiloto'] = usuario.calificacionComoCopiloto()
        viajes_creados_activos = usuario.viajesCreadosActivos()
        data['viajes_activos'] = [obj.asJson() for obj in viajes_creados_activos] if viajes_creados_activos else None
        tarjetas_de_creditos = usuario.tarjetas_de_credito()
        data['tarjetas_de_credito'] = [obj.asJson() for obj in tarjetas_de_creditos] if tarjetas_de_creditos else None
        data['viajes_en_espera_de_confirmacion'] = len(usuario.viajesEnEsperaComoCopiloto())
    except Usuario.DoesNotExist:
        data.setdefault('error', []).append('No exisite un perfil para el user {0}'.format(request.user))
    return JsonResponse(data)

@login_required
def crear_viaje_ajax(request):
    metodo = 'GET'
    request_data = getattr(request, metodo)
    fecha = request_data['fecha']
    duracion = request_data['duracion']
    origen = request_data['origen']
    destino = request_data['destino']
    auto_id = request_data['auto']
    cuenta_bancaria_id = request_data['cuenta_bancaria']

    return JsonResponse({})
