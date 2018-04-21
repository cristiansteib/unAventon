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
def mis_viajes_activos(request):
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
    if not neededParams(request.GET, 'viajeId'):
        print('falta parametro viajeId')
        raise Http404
    viaje_id = request.GET['viajeId']
    data = {'error':[]}
    try:
        usuario = Usuario.objects.get(user=request.user)
        viaje = Viaje.objects.get(auto__usuario=usuario, id=viaje_id)
        data['lista'] = [obj.asJson() for obj in viaje.copilotosEnListaDeEspera()]
    except Usuario.DoesNotExist:
        data['error'].append('No exisite un perfil para el user {0}'.format(request.user))
    except Viaje.DoesNotExist:
        data['error'].append('No exisite el viaje {0} para el usuario = {1} '.format(viaje_id, usuario))
    return JsonResponse(data)
