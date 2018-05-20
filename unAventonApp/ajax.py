""" Call ajax in this module """
from .models import Usuario, Viaje, Tarjeta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.core import serializers
import json
from django.utils import timezone
import datetime


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
        data['viajes'] = [viaje.asJson() for viaje in usuario.get_viajes_creados_activos()]
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
        data['lista'] = [obj.asJson() for obj in viaje.get_copilotos_en_lista_de_espera()]
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
        data['lista'] = [obj.asJson() for obj in usuario.get_calificaciones_pendientes_para_copilotos()]
    except Usuario.DoesNotExist:
        data.setdefault('error', []).append('No exisite un perfil para el user {0}'.format(request.user))
    return JsonResponse(data)


@login_required
def lista_de_calificaciones_pendientes_a_pilotos(request):
    data = {}
    try:
        usuario = Usuario.objects.get(user=request.user)
        data['lista'] = [obj.asJson() for obj in usuario.get_calificaciones_pendientes_para_piloto()]
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
        data['calificacion_como_piloto'] = usuario.get_calificacion_como_piloto()
        data['calificacion_como_copiloto'] = usuario.get_calificacion_como_copiloto()
        viajes_creados_activos = usuario.get_viajes_creados_activos()
        data['viajes_activos'] = [obj.asJson() for obj in viajes_creados_activos] if viajes_creados_activos else None
        tarjetas_de_creditos = usuario.get_tarjetas_de_credito()
        data['get_tarjetas_de_credito'] = [obj.asJson() for obj in
                                           tarjetas_de_creditos] if tarjetas_de_creditos else None
        data['viajes_en_espera_de_confirmacion'] = len(usuario.get_viajes_en_espera_como_copiloto())
    except Usuario.DoesNotExist:
        data.setdefault('error', []).append('No exisite un perfil para el user {0}'.format(request.user))
    return JsonResponse(data)


@login_required
def crear_viaje_ajax(request):
    try:
        metodo = 'POST'
        request_data = getattr(request, metodo)
        fecha_hora = timezone.datetime.fromtimestamp(int(request_data['fecha_hora_unix'])) + timezone.timedelta(
            hours=21)
        datos_viaje = {
            'comentario': request_data['comentario'],
            'fecha_hora_salida': fecha_hora,
            'duracion': request_data['duracion'],
            'origen': request_data['origen'],
            'gasto_total': request_data['costo'],
            'destino': request_data['destino'],
            'auto_id': request_data['auto_id'],
            'cuenta_bancaria_id': request_data['cuenta_bancaria'],
            'se_repite': (
            request_data['repeticion'], -1 if request_data['repeticion'] == 'diario' else fecha_hora.weekday())
        }

        mensaje_json = request.user.usuario.set_nuevo_viaje(datos_viaje)
        print(mensaje_json)
    except ValueError:
        mensaje_json = {
            'creado': False,
            'error': [{200: 'El a&ntilde;o esta fuera del rango'}]
        }
    return JsonResponse(mensaje_json)
