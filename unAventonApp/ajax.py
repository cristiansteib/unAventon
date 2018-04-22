""" Call ajax in this module """
from .models import Usuario, Viaje
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
    usuario = Usuario.objects.get(user=request.user)
    data['viajes'] = [viaje.asJson() for viaje in usuario.viajesCreadosActivos()]
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
        data['lista'] = [obj.asJson() for obj in viaje.copilotosEnListaDeEspera()]
    except KeyError as e:
        data.setdefault('error', []).append('Falta parametro para el request: {0} '.format(e))
    except Usuario.DoesNotExist:
        data.setdefault('error', []).append('No exisite un perfil para el user {0}'.format(request.user))
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
def datos_del_usuario(request):
    """ Arma un diccionario con los datos del usuario
    que luego pueden ser usados para armar el perfil
    """
    data = {}
    try:
        usuario = Usuario.objects.get(user=request.user)
        data['usuario'] = usuario.asJson()
        data['calificacion_como_piloto'] = usuario.calificacionComoPiloto()
        data['calificacion_como_copiloto'] = usuario.calificacionComoCopiloto()
        viajes_creados_activos = usuario.viajesCreadosActivos()
        data['viajes_activos'] = [obj.asJson() for obj in viajes_creados_activos] if viajes_creados_activos else None
        data['viajes_en_espera_de_confirmacion'] = len(usuario.viajesEnEsperaComoCopiloto())
    except Usuario.DoesNotExist:
        data.setdefault('error', []).append('No exisite un perfil para el user {0}'.format(request.user))
    return JsonResponse(data)