""" Call ajax in this module """
from .models import Usuario, Viaje, Tarjeta, CuentaBancaria, Auto
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.core import serializers
import json
from django.utils import timezone
import datetime
from django.db import IntegrityError


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
        cuentas_bancarias = usuario.get_cuentas_bancarias()
        data['get_cuentas_bancarias'] = [obj.asJson() for obj in cuentas_bancarias] if cuentas_bancarias else None
        autos = usuario.get_autos()
        data['get_vehiculos'] = [obj.asJson() for obj in autos] if autos else None

    except Usuario.DoesNotExist:
        data.setdefault('error', []).append('No exisite un perfil para el user {0}'.format(request.user))
    return JsonResponse(data)


#----------   Alta   --------------

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

@login_required
def crear_auto(request):
    response = {}
    r = request.POST
    try:
        Auto.objects.get(
            dominio=r['dominio'].upper().replace(' ','')
        )
        response['error'] = True
        response['msg'] = 'Ese auto ya esta en uso'
        return JsonResponse(response)

    except Auto.DoesNotExist:
        auto = Auto.objects.create(
            usuario=request.user.usuario,
            marca=r['marca'],
            modelo=r['modelo'],
            capacidad=r['capacidad'],
            dominio=r['dominio'].upper().replace(' ','')
        )
        response['data'] = auto.asJson()
        response['error'] = False
        response['msg'] = 'auto agregado'
        return JsonResponse(response)


@login_required
def crear_cuenta_bancaria(request):
    response = {}
    r = request.POST

    try:
        CuentaBancaria.objects.get(
            cbu=r['cbu'],
        )
        response['error'] = True
        response['msg'] = 'Esa cuenta ya esta en uso'
        return JsonResponse(response)
    except CuentaBancaria.DoesNotExist:
        cuenta = CuentaBancaria.objects.create(
            usuario=request.user.usuario,
            cbu=r['cbu'],
            entidad=r['entity']
        )
        response['error'] = False
        response['msg'] = 'Creado ok'
        response['data'] = cuenta.asJson()
        return JsonResponse(response)


@login_required
def crear_tarjeta(request):
    response = {}
    r = request.POST
    try:
        tarjeta = Tarjeta.objects.get(
            numero=r['cardNumber'],
            ccv=r['ccv'],
            fechaDeVencimiento=r['fechaVto'],
            fechaDeCreacion=r['fechaCreacion'],
        )
        tarjeta.usuario.add(request.user.usuario)
        print(tarjeta.usuario.all())
        response['error'] = False
        response['msg'] = 'usuario agregado a esa tarjeta'
        return JsonResponse(response)

    except Tarjeta.DoesNotExist:
        try:
            Tarjeta.objects.get( numero=r['cardNumber'])
            response['error'] = True
            response['msg'] = 'Esa tarjeta ya se encuentra en uso, revise los datos'
            return JsonResponse(response)

        except Tarjeta.DoesNotExist:
            tarjeta = Tarjeta.objects.create(
                numero=r['cardNumber'],
                ccv=r['ccv'],
                fechaDeVencimiento=r['fechaVto'],
                fechaDeCreacion=r['fechaCreacion'],
            )
            tarjeta.usuario.add(request.user.usuario)
            response['data'] = tarjeta.asJson()
            response['error'] = False
            response['msg'] = 'tarjeta creada'
            print(tarjeta.usuario.all())
            return JsonResponse(response)



#---------   Modificacion   ----------


@login_required
def actualizar_tarjeta(request):

    response = {}
    try:
        r = request.POST
        tarjeta = Tarjeta.objects.get(pk=r['id_tarjeta'])
        try:
            tarjeta.numero = r['cardNumber']
            tarjeta.ccv = r['ccv']
            tarjeta.fechaDeCreacion = r['fechaCreacion']
            tarjeta.fechaDeVencimiento = r['fechaVto']
            tarjeta.save()
            response['data'] = tarjeta.asJson()
            response['error'] = False
            return JsonResponse(response)
        except IntegrityError:
            response['msg'] = 'Tarjeta en uso por otro usuario'
            response['error'] = True
            return JsonResponse(response)

    except Tarjeta.DoesNotExist:
        response['error'] = True
        response['msg'] = 'no existe esa tarjeta!!!'
        return JsonResponse(response)


@login_required
def actualizar_datos_perfil(request):
    response = {}
    try:
        r = request.POST
        usuario = Usuario.objects.get(user=request.user)
        usuario.nombre = r['firstName']
        usuario.apellido = r['lastName']
        usuario.dni = r['dni']
        usuario.fechaDeNacimiento = r['birthDay']
        usuario.save()
        response['data'] = usuario.asJson()
        response['error'] = False
        return JsonResponse(response)
    except:
        response['error'] = True
        response['msg'] = 'no se pudo actualizar el perfil'
        return JsonResponse(response)


@login_required
def actualizar_cuenta_bancaria(request):
    response = {}
    r = request.POST
    try:
        cuenta = CuentaBancaria.objects.get(pk=r['id_cuenta'])

        try:
            cbu = CuentaBancaria.objects.get(cbu=r['cbu'])
            response['error'] = True
            response['msg'] = 'Cuenta bancaria en uso'
            return JsonResponse(response)
        except CuentaBancaria.DoesNotExist:
            cuenta.cbu = r['cbu']
            cuenta.entidad = r['entity']
            cuenta.save()
            response['error'] = False
            response['msg'] = 'Cuenta bancaria actualizada'
            response['data'] = cuenta.asJson()
            return JsonResponse(response)

    except CuentaBancaria.DoesNotExist:
        response['error'] = True
        response['msg'] = 'No existe esa cuenta bancaria'
        return JsonResponse(response)



#----------   Baja   ------------


@login_required
def borrar_auto(request):
    response = {}
    try:
        r = request.POST
        auto = Auto.objects.get(pk=r['id'])
        res = auto.delete()
        print(res)
        response['data'] = res
        response['error'] = False
        return JsonResponse(response)
    except:
        response['error'] = True
        response['msg'] = 'no se pudo borrar'
        return JsonResponse(response)


@login_required
def borrar_tarjeta(request):
    response = {}
    r = request.POST
    try:
        tarjeta = Tarjeta.objects.get(pk=r['id_tarjeta'])
        tarjeta.delete()
        response['error'] = False
        response['msg'] = 'tarjeta borrada'
        return JsonResponse(response)
    except CuentaBancaria.DoesNotExist:
        response['error'] = True
        response['msg'] = 'No existe esa tarjeta'
        return JsonResponse(response)


@login_required
def borrar_cuenta_bancaria(request):
    response = {}
    r = request.POST
    try:
        cuenta = CuentaBancaria.objects.get(pk=r['id_cuenta'])
        cuenta.delete()
        response['error'] = False
        response['msg'] = 'cuenta borrada'
        return  JsonResponse(response)
    except CuentaBancaria.DoesNotExist:
        response['error'] = True
        response['msg'] = 'No existe esa cuenta'
        return JsonResponse(response)
