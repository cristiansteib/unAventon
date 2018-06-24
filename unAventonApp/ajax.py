""" Call ajax in this module """
from .models import Usuario, Viaje, Tarjeta, CuentaBancaria, Auto, ViajeCopiloto, ConversacionPublica
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.core import serializers
import json
from django.utils import timezone
import datetime
from django.db import IntegrityError
from django.contrib.auth import logout
from django.forms.models import model_to_dict
from . import mailer


def neededParams(method_list, *args):
    for value in args:
        if value not in method_list:
            return False
    return True


def get_root_url(request):
    scheme = request.is_secure() and "https" or "http"
    return scheme + '://' + str(request.META['HTTP_HOST'])


def get_url_viaje_copiloto(request, viaje_copiloto):
    return get_root_url(request) + viaje_copiloto.get_absolute_url()


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
    #TODO: chequear si la UI usa esto
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
        # data['calificacion_como_piloto'] = usuario.get_calificacion_como_piloto()
        # data['calificacion_como_copiloto'] = usuario.get_calificacion_como_copiloto()

        tarjetas_de_creditos = usuario.get_tarjetas_de_credito()
        data['get_tarjetas_de_credito'] = [obj.asJson() for obj in
                                           tarjetas_de_creditos] if tarjetas_de_creditos else None
        data['viajes_en_espera_de_confirmacion'] = len(usuario.get_viajes_en_espera_como_copiloto())
        cuentas_bancarias = usuario.get_cuentas_bancarias()
        data['get_cuentas_bancarias'] = [obj.asJson() for obj in cuentas_bancarias] if cuentas_bancarias else None
        autos = usuario.get_autos()
        data['get_vehiculos'] = [obj.asJson() for obj in autos] if autos else None
        data['usuario']['reputacion_como_piloto'] = usuario.get_puntaje_como_piloto()
        data['usuario']['reputacion_como_copiloto'] = usuario.get_puntaje_como_copiloto()

    except Usuario.DoesNotExist:
        data.setdefault('error', []).append('No exisite un perfil para el user {0}'.format(request.user))
    return JsonResponse(data)


# ----------   Alta   --------------

@login_required
def crear_viaje_ajax(request):
    try:
        metodo = 'POST'
        request_data = getattr(request, metodo)
        fecha = request_data['fecha'].split('-')
        fecha = [int(x) for x in fecha]
        hora = request_data['hora'].split(':')
        hora = [int(x) for x in hora]
        fecha_hora = datetime.datetime(fecha[0], fecha[1], fecha[2], hora[0], hora[1])
        print(fecha_hora)
        datos_viaje = {
            'comentario': request_data['comentario'],
            'fecha_hora_salida': fecha_hora,
            'duracion': request_data['duracion'],
            'origen': request_data['origen'],
            'gasto_total': request_data['costo'],
            'destino': request_data['destino'],
            'auto_id': request_data['auto_id'],
            'auto_lugares_ocupados_de_antemano': Auto.objects.get(pk=request_data['auto_id']).capacidad - int(
                request_data['capacidad_restante']),
            'cuenta_bancaria_id': request_data['cuenta_bancaria'],
            'se_repite': (
                request_data['repeticion'], -1 if request_data['repeticion'] == 'diario' else fecha_hora.weekday())
        }
        # si es un update hay que borrar el existente
        viaje_id = request_data.get('viaje_id', None)
        viaje_anterior = None
        if viaje_id:
            print("es un update para el viaje, se desactiva")
            viaje_anterior = Viaje.objects.get(pk=viaje_id)
            viaje_anterior.desactivar()

        # crea el nuevo viaje
        mensaje_json = request.user.usuario.set_nuevo_viaje(datos_viaje)

        if viaje_anterior:
            if mensaje_json['creado']:
                viaje_anterior.delete()
            else:
                # restatura el viaje anterior, ya que el nuevo no se pudo crear
                viaje_anterior.activar()

        print(mensaje_json)
    except ValueError:
        mensaje_json = {
            'creado': False,
            'error': [{200: 'El a&ntilde;o esta fuera del rango'}]
        }
    return JsonResponse(mensaje_json)


@login_required
def crear_auto(request):
    response = {
        'error': True
    }
    r = request.POST
    if int(r['capacidad']) > 1:
        try:
            auto = Auto.objects.create(
                usuario=request.user.usuario,
                marca=r['marca'],
                modelo=r['modelo'],
                capacidad=r['capacidad'],
                dominio=r['dominio'].upper()
            )
            response['data'] = auto.asJson()
            response['error'] = False
            response['msg'] = 'auto agregado'
        except IntegrityError:
            response['error'] = True
            response['msg'] = 'Ya tenes este auto registrado'
    else:
        response['msg'] = 'La capacidad debe ser mayor o igual a 2'
    return JsonResponse(response)


@login_required
def crear_cuenta_bancaria(request):
    response = {
        'error': True
    }
    r = request.POST
    try:
        cuenta = CuentaBancaria.objects.create(
            usuario=request.user.usuario,
            cbu=r['cbu'],
            entidad=r['entity']
        )

    except IntegrityError:
        cuenta = CuentaBancaria.objects.get(usuario=request.user.usuario, cbu=r['cbu'])
        if cuenta.esta_activo:
            response['msg'] = 'Ya tenes esta cuenta registrada'
            return JsonResponse(response)

    cuenta.activar()
    cuenta.cbu = r['cbu']
    cuenta.entidad = r['entity']
    cuenta.save()

    response['data'] = cuenta.asJson()
    response['error'] = False
    response['msg'] = 'Cuenta creada'

    return JsonResponse(response)


@login_required
def crear_tarjeta(request):
    response = {
        'error': True
    }
    r = request.POST
    try:
        tarjeta = Tarjeta.objects.create(
            usuario=request.user.usuario,
            numero=r['cardNumber']
        )
        print('no exploto')

    except IntegrityError:
        print('0exploto')
        tarjeta = Tarjeta.objects.get(usuario=request.user.usuario, numero=r['cardNumber'])
        print(tarjeta)

        if tarjeta.esta_activo:
            response['msg'] = 'Ya tenes esta tarjeta registrada'
            return JsonResponse(response)

    tarjeta.esta_activo = True
    tarjeta.ccv = r['ccv']
    tarjeta.fechaDeVencimiento = r['fechaVto']
    tarjeta.fechaDeCreacion = r['fechaCreacion']
    tarjeta.save()

    response['data'] = tarjeta.asJson()
    response['error'] = False
    response['msg'] = 'tarjeta creada'

    return JsonResponse(response)


# ---------   Modificacion   ----------

@login_required
def actualizar_auto(request):
    response = {}
    try:
        r = request.POST
        usuario = request.user.usuario
        auto = Auto.objects.get(pk=r['id_auto'], usuario=usuario)
        if not usuario.tiene_el_auto_en_uso(auto):
            auto.dominio = r['dominio']
            auto.marca = r['marca']
            auto.modelo = r['modelo']
            auto.save()
            response['data'] = auto.asJson()
            response['error'] = False
            return JsonResponse(response)
        response['msg'] = 'El vehiculo se encuentra en uso, no se puede modificar'
        response['error'] = True
        return JsonResponse(response)

    except Auto.DoesNotExist:
        response['error'] = True
        response['msg'] = 'no existe esa auto!!!'
        return JsonResponse(response)


@login_required
def actualizar_tarjeta(request):
    data = {
        'error': True
    }

    try:
        r = request.POST

        tarjeta_a_actualizar = Tarjeta.objects.get(pk=r['id_tarjeta'], usuario=request.user.usuario)
        try:
            otra_tarjeta = Tarjeta.objects.get(numero=r['cardNumber'], usuario=request.user.usuario)
        except Tarjeta.DoesNotExist:
            otra_tarjeta = None

        tarjeta = tarjeta_a_actualizar

        if otra_tarjeta and tarjeta_a_actualizar.pk != otra_tarjeta.pk:
            if otra_tarjeta.esta_activo:
                data['msg'] = 'Ya tenes esta tarjeta registrada'
                return JsonResponse(data)
            else:
                tarjeta_a_actualizar.desactivar()
                otra_tarjeta.activar()
                tarjeta = otra_tarjeta

        tarjeta.numero = r['cardNumber']
        tarjeta.ccv = r['ccv']
        tarjeta.fechaDeCreacion = r['fechaCreacion']
        tarjeta.fechaDeVencimiento = r['fechaVto']
        tarjeta.save()
        data['error'] = False
        data['msg'] = 'Datos actualizados correctamente'
    except:
        import sys
        print("el peor error ", sys.exc_info()[1])

    return JsonResponse(data)


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
        password = r['password']
        usuario.user.username = r['email']
        usuario.user.email = r['email']
        if len(password) >= 8:
            usuario.user.set_password(password)
        usuario.user.save()
        usuario.save()
        response['data'] = usuario.asJson()
        response['error'] = False
        return JsonResponse(response)
    except IntegrityError:
        response['error'] = True
        response['msg'] = 'El mail ya esta en uso.'
        return JsonResponse(response)

    except:
        import sys
        print(sys.exc_info())
        response['error'] = True
        response['msg'] = 'no se pudo actualizar el perfil'
        return JsonResponse(response)


@login_required
def actualizar_cuenta_bancaria(request):
    data = {
        'error': True
    }

    try:
        r = request.POST
        cuenta_a_actualizar = CuentaBancaria.objects.get(pk=r['id_cuenta'], usuario=request.user.usuario)
        try:
            otra_cuenta = CuentaBancaria.objects.get(cbu=r['cbu'], usuario=request.user.usuario)
        except CuentaBancaria.DoesNotExist:
            otra_cuenta = None

        cuenta = cuenta_a_actualizar

        if otra_cuenta and cuenta_a_actualizar.pk != otra_cuenta.pk:
            if otra_cuenta.esta_activo:
                data['msg'] = 'Ya tenes esta cuenta bancaria registrada'
                return JsonResponse(data)
            else:
                cuenta_a_actualizar.desactivar()
                otra_cuenta.activar()
                cuenta = otra_cuenta

        cuenta.cbu = r['cbu']
        cuenta.entidad = r['entity']
        cuenta.save()
        data['error'] = False
        data['msg'] = 'Datos actualizados correctamente'
    except:
        import sys
        print("el peor error ", sys.exc_info()[1])

    return JsonResponse(data)


# ----------   Baja   ------------


@login_required
def borrar_auto(request):
    response = {}
    try:
        r = request.POST
        auto = Auto.objects.get(pk=r['id'])
        if request.user.usuario.elimiar_auto(auto):
            response['error'] = False
            response['msg'] = 'eliminado'
        else:
            response['error'] = True
            response['msg'] = 'El auto esta en uso! '
        return JsonResponse(response)
    except:
        response['error'] = True
        response['msg'] = 'No se pudo eliminar'
        return JsonResponse(response)


@login_required
def borrar_tarjeta(request):
    response = {}
    try:
        r = request.POST
        tarjeta = Tarjeta.objects.get(pk=r['id_tarjeta'], usuario=request.user.usuario)
        if request.user.usuario.elimiar_tarjeta(tarjeta):
            raise PermissionError
        tarjeta.usuario.remove(request.user.usuario)
        response['error'] = False
        response['msg'] = 'Tarjeta borrada'
        return JsonResponse(response)
    except PermissionError:
        response['error'] = True
        response['msg'] = 'La tarjeta esta en uso en algun viaje'
        return JsonResponse(response)
    except:
        import sys
        print(sys.exc_info())
        response['error'] = True
        response['msg'] = 'No se pudo borrar la tarjeta'
        return JsonResponse(response)


@login_required
def borrar_cuenta_bancaria(request):
    response = {}
    try:
        r = request.POST
        cuenta = CuentaBancaria.objects.get(pk=r['id_cuenta'])
        result = request.user.usuario.elimiar_cuenta_bancaria(cuenta)
        if not result:
            raise PermissionError
        response['error'] = False
        response['msg'] = 'cuenta borrada'
        return JsonResponse(response)
    except PermissionError:
        response['error'] = True
        response['msg'] = 'La cuenta esta en uso en algun viaje'
        return JsonResponse(response)
    except:
        response['error'] = True
        response['msg'] = 'No se pudo borrar la cuenta'
        return JsonResponse(response)


"""
 
 Metodos necesarios para los viajes 
 
 
"""


def cancelar_ir_en_viaje(request):
    """ esto lo usa solamente el copiloto"""
    data = {}
    r = request.POST
    id = r['viaje_copiloto_id']
    viajeC = ViajeCopiloto.objects.get(pk=id)
    if viajeC.estaConfirmado:
        viajeC.calificacion_a_copiloto = -1
        viajeC.calificacion_a_copiloto_mensaje = "Calificacion negativa por cancelar inscripcion estando confirmado"
        data['msg'] = ' Se desinscribio correctamente, se califico negativo.'
    else:
        viajeC.estaConfirmado = False
        data['msg'] = ' Se desinscribio correctamente'
    viajeC.estaConfirmado = False
    viajeC.rechazoElPiloto = False
    viajeC.save()
    return JsonResponse(data)


def solicitar_ir_en_viaje(request):
    data = {}
    r = request.POST
    id = r['viaje_id']
    id_tarjeta = r['tarjeta_id']
    fecha_solicitada = timezone.datetime.fromtimestamp(float(r['fecha_viaje']))
    try:
        '''Reglas de negocio para inscribirse a un viaje
            - tener tarjeta
            - no deber calif de mas de 30 dias
            - no estar en otro viaje en el mismo horario 
        '''
        viaje = Viaje.objects.get(pk=id)

        if not (request.user.usuario.get_tarjetas_de_credito()):
            data['error'] = True
            data['msg'] = 'No tienes tarjeta de credito, registre una para poder inscribirse'
            return JsonResponse(data)

        if request.user.usuario.tiene_calificicaciones_pendientes_desde_mas_del_maximo_de_dias_permitidos():
            data['error'] = True
            data['msg'] = 'Debe calificaciones de mas de 30 dias'
            return JsonResponse(data)

        if request.user.usuario.se_superpone_algun_viaje(fecha_solicitada, viaje.duracion):
            data['error'] = True
            data['msg'] = 'Hay un viaje que se superpone en la fecha y hora solicitada'
            return JsonResponse(data)

        tarjeta = Tarjeta.objects.get(pk=id_tarjeta)

        rta = viaje.set_agregar_copiloto_en_lista_de_espera(usuario=request.user.usuario, fecha=fecha_solicitada,
                                                            tarjeta=tarjeta)
        data['error'] = False
        data['msg'] = "Solicitud enviada correctamente"
        return JsonResponse(data)
    except IntegrityError:
        import sys
        print(sys.exc_info())
        vc = ViajeCopiloto.objects.get(usuario=request.user.usuario, fecha_del_viaje=fecha_solicitada, viaje=viaje)
        data['error'] = True
        if vc.estaConfirmado == None:
            data['msg'] = 'Ya enviaste solicitud para este viaje.<br> Se paciente =)'
        if vc.estaConfirmado == True:
            data['msg'] = 'Ya estas confirmado en este viaje'
        if vc.estaConfirmado == False and vc.rechazoElPiloto:
            data['msg'] = 'El piloto te ha rechazado en este viaje'
        if vc.estaConfirmado == False and not vc.rechazoElPiloto:
            data['msg'] = 'Has cancelado la solicitud en este viaje'

        return JsonResponse(data)
    except:
        import sys
        print(sys.exc_info())
        print('a la mierda todo')
        return JsonResponse({'error': 'algo salio mal'})


def lista_de_copilotos_confirmados(request):
    data = {'data': []}
    r = request.POST
    id = r['viaje_id']
    fecha_viaje_unix = r.get('fecha_hora_unix', None)

    viaje = Viaje.objects.get(pk=id)
    if fecha_viaje_unix:
        # si se requiere de una fecha en particular, se filtra por esa fecha
        viajeCopilotos = viaje.get_copilotos_confirmados_en_fecha(
            timezone.datetime.fromtimestamp(int(fecha_viaje_unix)))
    else:
        # sino todas la fechas mayores a hoy. Las fechas anteriores a hoy estan finalizados.
        viajeCopilotos = ViajeCopiloto.objects.filter(viaje=viaje, fecha_del_viaje__gte=timezone.now(),
                                                      estaConfirmado=True)
    for obj in viajeCopilotos:
        current_data = model_to_dict(obj.usuario, exclude=('foto_de_perfil'))
        current_data.update(model_to_dict(obj))
        current_data.update(model_to_dict(obj.usuario.user, fields='username'))
        current_data.update({'viajeCopiloto_id': obj.pk})
        current_data.update({'estado': obj.get_estado()})
        current_data.update({'esta_calificado': obj.esta_el_copiloto_calificado()})
        current_data.update({'es_para_proxima_fecha': obj.fecha_del_viaje == obj.viaje.proxima_fecha_de_salida()})
        data['data'].append(current_data)

    return JsonResponse(data)


def lista_de_copitolos_en_espera(request):
    ## esta el vista que llama el ajax cuando carga el modal
    data = {'data': []}
    r = request.POST
    id = r['viaje_id']
    viaje = Viaje.objects.get(pk=id)
    viajes_copilotos = ViajeCopiloto.objects.filter(viaje=viaje, estaConfirmado=None,
                                                    fecha_del_viaje__gte=timezone.now()).order_by('fecha_del_viaje')

    for obj in viajes_copilotos:
        current_data = model_to_dict(obj.usuario, exclude=('foto_de_perfil'))
        current_data.update(model_to_dict(obj))
        current_data.update(model_to_dict(obj.usuario.user, fields='username'))
        current_data.update({'viajeCopiloto_id': obj.pk})
        current_data.update({'es_para_proxima_fecha': obj.fecha_del_viaje == obj.viaje.proxima_fecha_de_salida()})
        data['data'].append(current_data)

    return JsonResponse(data)


def confirmar_copiloto(request):
    data = {'error': True}
    r = request.POST
    id_viajeCopiloto = r['viaje_copiloto_id']
    viajeCopiloto = ViajeCopiloto.objects.get(pk=id_viajeCopiloto)

    if viajeCopiloto.usuario != viajeCopiloto.viaje.auto.usuario:
        if not viajeCopiloto.usuario.tiene_calificicaciones_pendientes_desde_mas_del_maximo_de_dias_permitidos():

            if not viajeCopiloto.usuario.se_superpone_algun_viaje(viajeCopiloto.fecha_del_viaje,
                                                                  viajeCopiloto.viaje.duracion):

                if viajeCopiloto.confirmarCopiloto():
                    print('se confirmo')
                    data['error'] = False
                    data['msg'] = 'confirmado'
                    url = get_url_viaje_copiloto(request, viajeCopiloto)
                    mailer.send_email(viajeCopiloto.usuario.user.email,
                                      subject="El piloto a confirmado su viaje",
                                      message="Usted a sido confirmado en el viaje.\n Para ver los detalles ingrese a: "
                                              "{0}".format(url)
                                      )
                else:
                    data['msg'] = 'no se confirmo, no hay lugar'
            else:
                data['msg'] = 'El copiloto esta confirmado en otro viaje, dentro del mismo horario'
        else:
            data['msg'] = 'El copiloto tiene calificaciones pendientes, no se puede confirmar.'
    else:
        data['msg'] = 'Es piloto en ese viaje, no puede ser piloto y copiloto al mismo tiempo'
    return JsonResponse(data)


def rechazar_copiloto(request):
    # el copiloto no eta confirmado todavia
    data = {}
    r = request.POST
    viaje_copiloto_id = r['viaje_copiloto_id']
    viaje_copiloto = ViajeCopiloto.objects.get(pk=viaje_copiloto_id)
    viaje_copiloto.rechazarCopiloto()

    mailer.send_email(viaje_copiloto.usuario.user.email,
                      subject="El piloto a rechazado su solicitud",
                      message="El piloto ha decidido rechazar la solicitud al viaje {0}".format(
                          get_url_viaje_copiloto(request, viaje_copiloto))
                      )

    return JsonResponse(data)


def cancelar_copiloto(request):
    data = {}
    r = request.POST
    viaje_copiloto_id = r['viaje_copiloto_id']
    viaje_copiloto = ViajeCopiloto.objects.get(pk=viaje_copiloto_id)
    viaje_copiloto.cancelarCopiloto()

    mailer.send_email(viaje_copiloto.usuario.user.email,
                      subject="El piloto a cancelado su solicitud",
                      message="El piloto ha decidido quitar la confirmacion al viaje {0},\nY se reintegrara el total cobrado por cada viaje. (El costo por cada viaje fue de={1}) ".format(
                          get_url_viaje_copiloto(request, viaje_copiloto),viaje_copiloto.viaje.get_costo_por_pasajero())
                      )
    return JsonResponse(data)


def calificar_copiloto(request):
    # TODO: retornar un json mas amigable :)
    data = {}
    r = request.POST
    viaje_copiloto_id = r['viaje_copiloto_id']
    calificacion = r['calificacion']
    comentario = r['comentario']
    viajeCopiloto = ViajeCopiloto.objects.get(pk=viaje_copiloto_id)
    viajeCopiloto.calificar_a_copiloto(calificacion, comentario)
    return JsonResponse(data)


def ver_calificacion_de_copiloto(request):
    data = {}
    r = request.POST
    viaje_copiloto_id = r['viaje_copiloto_id']
    viajeCopiloto = ViajeCopiloto.objects.get(pk=viaje_copiloto_id)
    data['calificacion'] = viajeCopiloto.calificacion_a_copiloto
    data['calificacion_mensaje'] = viajeCopiloto.calificacion_a_copiloto_mensaje
    return JsonResponse(data)


def ver_calificacion_de_piloto(request):
    data = {}
    r = request.POST
    viaje_copiloto_id = r['viaje_copiloto_id']
    viajeCopiloto = ViajeCopiloto.objects.get(pk=viaje_copiloto_id)
    data['calificacion'] = viajeCopiloto.calificacion_a_piloto
    data['calificacion_mensaje'] = viajeCopiloto.calificacion_a_piloto_mensaje
    return JsonResponse(data)


def calificar_piloto(request):
    # TODO: retornar un json mas amigable :)
    data = {}
    r = request.POST
    viaje_copiloto_id = r['viaje_copiloto_id']
    calificacion = r['calificacion']
    comentario = r['comentario']
    viajeCopiloto = ViajeCopiloto.objects.get(pk=viaje_copiloto_id)
    viajeCopiloto.calificar_a_piloto(calificacion, comentario)
    return JsonResponse(data)


def elimiar_viaje(request):
    # elimina absolutamente el viaje
    data = {}
    r = request.POST
    id_viaje = r['viaje_id']
    viaje = Viaje.objects.get(pk=id_viaje)
    viaje.eliminar()
    return JsonResponse(data)


def datos_del_viaje(request):
    viaje = Viaje.objects.get(pk=request.POST['viaje_id'])
    data = model_to_dict(viaje)
    return JsonResponse(data)


def buscar_viajes_ajax(request):
    data = {
        'viajes': []
    }

    origen = request.POST.get('origen', None)
    destino = request.POST.get('destino', None)
    fecha = request.POST.get('fecha', None)
    hora = request.POST.get('hora', None)

    precio_minimo = int(request.POST['precio_min']) if request.POST.get('precio_min', None) else None
    precio_maximo = int(request.POST['precio_max']) if request.POST.get('precio_max', None) else None

    viajes = Viaje.objects.filter(
        origen__icontains=origen,
        destino__icontains=destino,
        activo=True
    )

    # filtra por fecha y hora
    if fecha:
        viajes = list(filter(lambda x: x.caeEnLaFecha(fecha), viajes))
        f = datetime.datetime.strptime(fecha, '%Y-%m-%d')

        for viaje in viajes:
            fecha = timezone.datetime(f.year, f.month, f.day, viaje.fecha_hora_salida.hour,
                                      viaje.fecha_hora_salida.minute, tzinfo=viaje.fecha_hora_salida.tzinfo)
            viaje.fecha_hora_salida = fecha

    if hora:
        viajes = list(filter(lambda x: x.caeEnLaHora(hora), viajes))

    # chequea si hay que filtrar por costo
    if precio_minimo:
        viajes = list(filter(lambda x: x.get_costo_por_pasajero() >= precio_minimo, viajes))
    if precio_maximo:
        viajes = list(filter(lambda x: x.get_costo_por_pasajero() <= precio_maximo, viajes))

    data['viajes'] = list(map(lambda x: x.asJsonPublicacion(request.user.usuario), viajes))
    return JsonResponse(data)


def preguntas_sin_responder_conversacion_publica(request):
    data = {}
    preguntas = ConversacionPublica.objects.filter(viaje=request.POST['viaje_id'], respuesta__isnull=True)
    data['preguntas'] = list(map(lambda x: model_to_dict(x), preguntas))
    return JsonResponse(data)


def responder_pregunta_conversacion_publica(request):
    conversacion = ConversacionPublica.objects.get(pk=request.POST['id'])
    conversacion.respuesta = request.POST['respuesta']
    conversacion.fechaHoraRespuesta = timezone.now()
    conversacion.save()
    print(conversacion)
    return JsonResponse(model_to_dict(conversacion))
