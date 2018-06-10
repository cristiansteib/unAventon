from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.db.models import Count, Min, Sum, Avg
import json
from django.utils import timezone
from django.conf import settings
import datetime
from collections import namedtuple
from django.core.files.storage import FileSystemStorage
from . import utils
import datetime


fotoStorage = FileSystemStorage(location='media/')

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=15, )
    apellido = models.CharField(max_length=15)
    fechaDeNacimiento = models.DateField(default=None, null=True)
    dni = models.CharField(max_length=15, default=None, null=True)
    foto_de_perfil = models.ImageField(storage=fotoStorage, default='assets/default-user.png')


    def asJsonMinified(self):
        return {
            'id': self.pk,
            'nombre': self.nombre,
            'apellido': self.apellido,
        }

    def asJson(self):
        data = self.asJsonMinified()
        data.update(
            {
                'mail': self.user.email,
                'dni': self.dni,
                'fecha_de_nacimiento': self.fechaDeNacimiento
            }
        )
        return data

    def __str__(self):
        return "{0} {1}".format(self.nombre, self.apellido)

    def puede_crear_viaje(self, fecha_hora_salida, duracion):
        # no tiene calificaciones pendientes
        # tiene auto
        # tiene tarjeta de credito
        # no tiene otro viaje en el mismo horario
        mensaje = {'error': []}
        # esta tratando de hacer un viaje de un dia anterior?
        if fecha_hora_salida < timezone.datetime.now():
            mensaje['error'].append({110: 'El viaje debe ser posterior a la fecha actual.'})

        pendientes = self.tiene_calificicaciones_pendientes_desde_mas_del_maximo_de_dias_permitidos()

        if pendientes:
            plural = "es" if pendientes > 1 else ""
            mensaje['error'].append(
                {101: 'Tenes {0} calificacion{1} pendiente{2} por hacer'.format(pendientes, plural, plural[1])})
        ##check que no este en uso en otro viaje en el mismo rango horario como piloto
        viajes_activos = self.get_viajes_creados_activos().filter(fecha_hora_salida__lte=fecha_hora_salida)

        viajes_diarios = self.get_viajes_diarios_activos().filter(fecha_hora_salida__lte=fecha_hora_salida)
        week_day = datetime.datetime.fromtimestamp(fecha_hora_salida.timestamp()).weekday()
        viajes_semanales = self.get_viajes_semanales_activos_para_weekday(week_day).filter(
            fecha_hora_salida__lte=fecha_hora_salida)
        viajes_mismo_dia = viajes_activos.filter(
            fecha_hora_salida__year=fecha_hora_salida.year,
            fecha_hora_salida__month=fecha_hora_salida.month,
            fecha_hora_salida__day=fecha_hora_salida.day)
        sp = self.__se_superpone_rango_horario
        if sp(fecha_hora_salida, duracion, viajes_mismo_dia) or sp(fecha_hora_salida, duracion, viajes_diarios) or sp(
                fecha_hora_salida, duracion, viajes_semanales):
            mensaje['error'].append({102: 'Tenes algun viaje como piloto en el mismo rango horario.'})

        ##check que no este en uso en otro viaje en el mismo rango horario como copiloto
        viajes_como_copiloto = Viaje.objects.filter(
            pk__in=self.get_viajes_confirmados_como_copiloto().values('viaje_id'))

        if self.__se_superpone_rango_horario(fecha_hora_salida, duracion, viajes_como_copiloto):
            mensaje['error'].append(
                {103: 'Tenes algun viaje aceptado como copiloto en el mismo rango horario ingresado.'})

        return True if not len(mensaje['error']) else False, mensaje

    def se_superpone_algun_viaje_como_copiloto(self):
        pass

    def se_superpone_algun_viaje_como_piloto(self):
        pass

    def se_superpone_algun_viaje(self):
        return self.se_superpone_algun_viaje_como_copiloto() or self.se_superpone_algun_viaje_como_piloto()

    @staticmethod
    def __se_superpone_rango_horario(fecha_hora_inicio, duracion, viajesCollection):
        duracion = int(duracion)


        fecha_hora_salida_start = datetime.datetime(1, 1, 1, fecha_hora_inicio.hour, fecha_hora_inicio.minute)
        fecha_hora_salida_end = utils.sumar_horas(fecha_hora_inicio.hour, fecha_hora_inicio.minute, duracion, 0)
        slow_value = datetime.timedelta(0, 0)

        for viaje in viajesCollection:
            viaje_datetime_start = datetime.datetime(1, 1, 1, viaje.fecha_hora_salida.hour,
                                                     viaje.fecha_hora_salida.minute)
            viaje_datetime_end = utils.sumar_horas(viaje.fecha_hora_salida.hour, viaje.fecha_hora_salida.minute,
                                              viaje.duracion, 0)

            overlap = utils.get_overlap(slow_value, viaje_datetime_start, viaje_datetime_end, fecha_hora_salida_start,
                                  fecha_hora_salida_end)
            if overlap > datetime.timedelta(0, 0):
                return True
        return False

    def get_viajes_diarios_activos(self):
        return self.get_viajes_creados_activos().filter(se_repite__contains='diario')

    def get_viajes_semanales_activos(self):
        return self.get_viajes_creados_activos().filter(se_repite__contains='semanal')

    def get_viajes_semanales_activos_para_weekday(self, weekday):
        return self.get_viajes_semanales_activos().filter(se_repite__contains=weekday)

    def tiene_calificicaciones_pendientes_desde_mas_del_maximo_de_dias_permitidos(self):
        maximo_dias = settings.APP_MAX_DIAS_CALIFICACION_PENDIENTES
        return 0

    def tiene_calificicaciones_pendientes(self):
        return self.get_calificaciones_pendientes_para_piloto() or self.get_calificaciones_pendientes_para_copilotos()

    def get_calificacion_como_piloto(self):
        pass

    def get_calificacion_como_copiloto(self):
        pass

    def get_calificaciones_pendientes_para_piloto(self):
        pass

    def get_calificaciones_pendientes_para_copilotos(self):
        pass

    def __calificar(self, calificacion, aUsuario, enViaje, comentario):
        pass

    def set_calificar_piloto(self, enViaje, calificacion, comentario):
        if self.es_copiloto_en_viaje(enViaje):
            self.__calificar(calificacion, enViaje.auto.usuario , enViaje, comentario)
            return True
        return False

    def set_calificar_copiloto(self , viaje=None, calificacion=None, copiloto=None, comentario=None):
        if self.es_piloto_en_viaje(viaje):
            self.__calificar(calificacion, copiloto, viaje, comentario)
            return True
        return False

    def get_viajes_en_espera_como_copiloto(self):
        return ViajeCopiloto.objects.filter(usuario=self, estaConfirmado=False)

    def get_viajes_confirmados_como_copiloto(self):
        return ViajeCopiloto.objects.filter(usuario=self, estaConfirmado=True)

    def get_viajes_creados(self):
        """ Todos los viajes que creo el usuario"""
        return Viaje.objects.filter(auto__usuario=self)

    def get_viajes_creados_activos(self):
        """ Todos los viajes que creados por el usuario, no finalizados"""
        return self.get_viajes_creados().filter(activo=True)

    def get_viajes_finalizados(self):
        """ Todos los viajes que creados por el usuario, finalizados"""
        return self.get_viajes_creados().exclude(self.get_viajes_creados_activos())

    def es_piloto_en_viaje(self, viaje):
        return viaje.auto.usuario == self

    def es_copiloto_en_viaje(self, viaje):
        try:
            ViajeCopiloto.objects.get(usuario=self, viaje=viaje)
            return True
        except ViajeCopiloto.DoesNotExist:
            return False

    def get_tarjetas_de_credito(self):
        return Tarjeta.objects.filter(usuario=self, esta_activo=True)

    def get_autos(self):
        return Auto.objects.filter(usuario=self,esta_activo=True)

    def tiene_el_auto_en_uso(self, unAuto):
        return len(self.get_viajes_creados_activos().filter(auto=unAuto)) > 0

    def elimiar_auto(self, unAuto):
        """ primero verifico que el usuario no tenga en uso el vehiculo,
        si lo tiene en uso no se podra eliminar"""
        unAuto.desactivar()
        return True

    def get_cuentas_bancarias(self):
        return CuentaBancaria.objects.filter(usuario=self, esta_activo=True)

    def set_nuevo_viaje(self, datos):
        json_info = Viaje.objects.create_viaje(usuario=self, **datos)
        return json_info

    def get_viajes_unicos_activos(self):
        return self.get_viajes_creados_activos().filter(se_repite__contains='nunca')

    def tiene_la_cuenta_bancaria_en_uso(self, unaCuentaBancaria):
        return len(self.get_viajes_creados_activos().filter(cuenta_bancaria=unaCuentaBancaria, cuenta_bancaria__esta_activo=True )) > 0

    def elimiar_cuenta_bancaria(self, unaCuentaBancaria):
        """ primero verifico que el usuario no tenga la cuenta bancaria en uso,
        si lo tiene en uso no se podra eliminar"""

        if self.tiene_la_cuenta_bancaria_en_uso(unaCuentaBancaria):
            return False
        else:
            unaCuentaBancaria.desactivar()
            return True

    def tiene_la_tarjeta_en_uso(self, unaTarjeta):
        x1 = len(self.get_viajes_confirmados_como_copiloto().filter(tarjeta=unaTarjeta, viaje__activo=True))
        x2 = len(self.get_viajes_en_espera_como_copiloto().filter(tarjeta=unaTarjeta, viaje__activo=True))
        return x1 + x2 > 0

    def elimiar_tarjeta(self, unaTarjeta):
        """ primero verifico que el usuario no tenga la cuenta bancaria en uso,
        si lo tiene en uso no se podra eliminar"""
        if self.tiene_la_tarjeta_en_uso(unaTarjeta):
            return False
        else:
            unaTarjeta.desactivar()
            return True


class Tarjeta(models.Model):
    class Meta:
        unique_together = (('usuario', 'numero'),)

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)
    numero = models.CharField(max_length=16, null=True)
    fechaDeVencimiento = models.CharField(max_length=5, default=None, null=True)
    fechaDeCreacion = models.CharField(max_length=5, default=None, null=True)
    ccv = models.IntegerField(null=True)
    esta_activo = models.BooleanField(default=True)

    def desactivar(self):
        self.esta_activo = False
        self.save()

    def activar(self):
        self.esta_activo = True
        self.save()

    def asJson(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'fecha_de_vencimiento': self.fechaDeVencimiento,
            'fecha_de_creacion': self.fechaDeCreacion,
            'ccv': self.ccv
        }


class CuentaBancaria(models.Model):
    class Meta:
        unique_together = (('usuario', 'cbu'),)

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cbu = models.CharField(max_length=25)
    entidad = models.CharField(max_length=20, default=None, null=True)
    esta_activo = models.BooleanField(default=True)

    def desactivar(self):
        self.esta_activo = False
        self.save()

    def activar(self):
        self.esta_activo = True
        self.save()

    def __str__(self):
        return '{0} ---> {1}'.format(self.usuario, self.cbu)

    def asJson(self):
        return {
            'id': self.pk,
            'entidad': self.entidad,
            'cbu': self.cbu
        }


class Auto(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    dominio = models.CharField(max_length=15)
    marca = models.CharField(max_length=15)
    modelo = models.CharField(max_length=15)
    capacidad = models.IntegerField()
    esta_activo = models.BooleanField(default=True)

    def desactivar(self):
        self.esta_activo = False
        self.save()

    def __str__(self):
        return '{0} ---> {1}'.format(self.usuario, self.dominio)

    def asJson(self):
        return {
            'id': self.id,
            'marca': self.marca,
            'modelo': self.modelo,
            'capacidad': self.capacidad,
            'dominio': self.dominio,
        }


class TipoViaje(models.Model):
    tipo = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=150)

    def asJson(self):
        return json.dumps(
            {
                'id': self.pk,
                'tipoViaje': self.tipo,
                'descripcion': self.descripcion
            },
            sort_keys=True,
            indent=4)


class ViajeManager(models.Manager):
    def create_viaje(self, usuario=..., **kwargs):
        __json = {
            'creado': False,
            'error': []
        }

        cuenta_bancaria = CuentaBancaria.objects.filter(pk=kwargs['cuenta_bancaria_id'], usuario=usuario)
        if not cuenta_bancaria:
            __json['error'].append({0: 'La cuenta bancaria no corresponde al usuario conductor'})

        puede_crear, mensaje = usuario.puede_crear_viaje(kwargs['fecha_hora_salida'], kwargs['duracion'])
        if not puede_crear:
            __json['error'].extend(mensaje['error'])

        if not len(__json['error']):
            # no hay errores, entonces se guarda
            viaje = self.create(**kwargs)
            __json['id'] = viaje.pk
            __json['creado'] = True
            # viaje.delete()
        return __json

        # return viaje

    def buscar_viajes_activos(self, usuario=None, fecha=None):
        viajes = self.filter(activo=True)
        if usuario:
            viajes = viajes.filter(usuario=usuario)
        if fecha:
            viajes = viajes.filter(fecha_hora_salida=fecha)

        return viajes


class Viaje(models.Model):
    auto = models.ForeignKey(Auto, on_delete=models.DO_NOTHING)
    se_repite = models.CharField(default=None, null=True, max_length=50)
    cuenta_bancaria = models.ForeignKey(CuentaBancaria, on_delete=models.DO_NOTHING)
    gasto_total = models.FloatField(default=0.0)
    comentario = models.CharField(max_length=150)
    origen = models.CharField(max_length=20)
    destino = models.CharField(max_length=20)
    fecha_hora_salida = models.DateTimeField()
    duracion = models.FloatField()
    comision = models.FloatField(default=settings.APP_COMISION)
    activo = models.BooleanField(default=True)

    objects = ViajeManager()

    def __str__(self):
        return "id={0} {1} , de {2} a {3}, fecha {4}".format(self.pk, self.auto.usuario, self.origen, self.destino,
                                                             self.fecha_hora_salida)

    def proxima_fecha_de_salida(self):
        import ast
        se_repite = ast.literal_eval(self.se_repite)
        # se_repite una variable tipo tupla ej: ('semanal',3)
        # donde el elemento [1] es el weekday, solo valido para tipo semanal

        if self.se_repite.count('nun'):
            return self.fecha_hora_salida


        """ Calculo para viajes semanales"""

        if self.se_repite.count('sem'):
            # es mayor a hoy la fecha, asique retorno de una el valor
            if timezone.now() < self.fecha_hora_salida:
                print('fecha actual proxima')
                return self.fecha_hora_salida

            else:
                # todo: checkear bien, creo que anda
                # puede ser que sea en este dia, y la hora sea menor
                # si la hora es mayor, entonces es para la semana que viene, en ese weekday
                print('calculo la proxima')
                diferencia_en_dias = (timezone.now() - self.fecha_hora_salida).days
                multiplicador_de_semanas = (diferencia_en_dias // 7) + 1
                proxima_fecha = self.fecha_hora_salida + timezone.timedelta(weeks=multiplicador_de_semanas)
                return proxima_fecha

        """ Calculo para viajes diarios"""

        if self.se_repite.count('dia'):
            # es mayor a hoy la fecha, asique retorno de una el valor
            if timezone.now() < self.fecha_hora_salida:
                return self.fecha_hora_salida
            else:
                # todo: chekear bien, creo que anda
                # puede ser que sea en este dia, y la hora sea menor
                # si la hora es mayor, entonces es para mañana
                diferencia_en_dias = (timezone.now() - self.fecha_hora_salida).days
                multiplicador_de_dias = (diferencia_en_dias) + 1
                proxima_fecha = self.fecha_hora_salida + timezone.timedelta(days=multiplicador_de_dias)
                return proxima_fecha

        return "no calulado, no se contemplo alguna condicion."



    def buscar_viaje(self, origen, destino, fecha):
        pass

    def activar(self):
        self.activo = True
        self.save()

    def desactivar(self):
        self.activo = False
        self.save()

    def esta_activo(self):
        return self.activo

    def get_total_a_reintegrar_al_conductor(self):
        value = self.get_total_cobrado() - self.get_comision_a_cobrar()
        return value if value > 0 else 0

    def get_comision_a_cobrar(self):
        return self.comision * self.gasto_total

    def get_total_cobrado(self):
        return len(self.get_copilotos_confirmados()) * self.get_costo_por_pasajero()

    def get_costo_por_pasajero(self):
        return self.gasto_total / self.auto.capacidad

    def get_se_repite_asString(self):
        import ast
        frecuencia, dia = ast.literal_eval(self.se_repite)
        dias = ['domingo', 'lunes', 'martes', 'miercoles', 'jueves', 'viernes']
        if frecuencia == 'semanal':
            return "Se repite todas las semanas"
        elif frecuencia == 'diario':
            return "Se repite todos los " + dias[dia] + "."
        return "Sin datos"

    def asJson(self):
        data = {
            'id': self.pk,
            'origen': self.origen,
            'destino': self.destino,
            'fecha_hora_salida': self.fecha_hora_salida,
            'fecha_hora_salida_unix': self.fecha_hora_salida.timestamp(),
            'costo_total': self.gasto_total,
            'costo_por_pasajero': self.get_costo_por_pasajero(),
            'duracion': self.duracion,
            'auto': self.auto.asJson(),
            'hay_lugar': self.hay_lugar(),
            'get_asientos_disponibles': self.get_asientos_disponibles(),
            'usuarios_confirmados': None,
            'activo': self.esta_activo(),
            'se_repite': self.get_se_repite_asString()
        }
        usuarios_confirmados = self.get_copilotos_confirmados()
        if usuarios_confirmados:
            data['usuarios_confirmados'] = [obj.asJsonMinified() for obj in usuarios_confirmados]

        return data

    def asJsonPublicacion(self):
        return {
            'id': self.pk,
            'origen': self.origen,
            'destino': self.destino,
            'fecha_hora_salida': self.fechaHoraSalida,
            'fecha_hora_salida_unix': self.fechaHoraSalida.timestamp(),
            'costo_por_pasajero': self.get_costo_por_pasajero(),
            'duracion': self.duracion,
            'auto': self.auto.asJson()
        }

    def get_copilotos_confirmados(self):
        return Usuario.objects.filter(
            pk__in=ViajeCopiloto.objects.filter(
                viaje=self,
                estaConfirmado=True
            ).values('usuario__pk')
        )

    def get_count_copilotos_confirmados(self):
        return len(Usuario.objects.filter(
            pk__in=ViajeCopiloto.objects.filter(
                viaje=self,
                estaConfirmado=True
            ).values('usuario__pk')
        ))

    def get_asientos_disponibles(self):
        asientos_ocupados = ViajeCopiloto.objects.filter(
            viaje=self,
            estaConfirmado=True
        ).aggregate(
            Count('usuario')
        )['usuario__count']
        # se resta 1 por el piloto
        return self.auto.capacidad - asientos_ocupados - 1

    def hay_lugar(self):
        return True if self.get_asientos_disponibles() else False

    def get_copilotos_en_lista_de_espera(self):
        return ViajeCopiloto.objects.filter(viaje=self, estaConfirmado=None)

    def get_copilotos_en_lista_de_espera_siguiente_fecha(self):
        pass

    def get_count_copilotos_en_lista_de_espera(self):
        return len(ViajeCopiloto.objects.filter(viaje=self, estaConfirmado=None))

    def get_count_copilotos_en_lista_de_espera_siguiente_fecha(self):
        pass

    def set_agregar_copiloto_en_lista_de_espera(self, usuario, fecha):
        return ViajeCopiloto.objects.create(
            viaje=self,
            usuario=usuario,
            fecha_del_viaje=fecha
        )

    def get_conversacion_publica(self):
        return ConversacionPublica.objects.filter(viaje=self).order_by('fechaHoraPregunta')

    def get_conversacion_privada(self):
        return ConversacionPrivada.objects.filter(viaje=self).order_by('fechaHora')


class ViajeCopiloto(models.Model):
    class Meta:
        unique_together = (('usuario', 'viaje', 'fecha_del_viaje'),)

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # el copiloto
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE)
    fecha_del_viaje = models.DateTimeField()
    tarjeta = models.ForeignKey(Tarjeta, on_delete=models.DO_NOTHING, null=True)  # el copiloto
    estaConfirmado = models.NullBooleanField(default=None, null=True)
    fecha_hora_de_solicitud = models.DateTimeField(auto_created=True, default=timezone.now())
    calificacion_a_piloto = models.IntegerField(default=None, null=True)
    calificacion_a_piloto_mensaje = models.CharField(max_length=150, default=None, null=True)
    calificacion_a_copiloto = models.IntegerField(default=None, null=True)
    calificacion_a_copiloto_mensaje = models.CharField(max_length=150, default=None, null=True)

    def confirmarCopiloto(self):
        #todo: chequear que no este en otro viaje
        if self.viaje.hay_lugar():
            self.estaConfirmado = True
            self.save()
            return True
        else:
            return False

    def rechazarCopiloto(self):
        """ se supone que el copiloto nunca estuvo confirmado, simplemente rechaza
        la solicitud"""
        self.estaConfirmado = False
        self.save()

    def cancelarCopiloto(self):
        """ el copiloto estuvo aceptado, entonces se cancela y se decrementa un punto"""
        self.estaConfirmado = False
        self.calificacion_a_piloto = -1
        self.calificacion_a_piloto_mensaje = "Penalidad por cancelacion a un copiloto confirmado."
        self.save()


    def desconfirmarCopiloto(self):
        if self.viaje.hay_lugar():
            self.estaConfirmado = False
            self.save()
            return True
        else:
            return False

    def __str__(self):
        return "Copiloto: {0}, Confirmado: {1} ".format(str(self.usuario), "SI" if self.estaConfirmado else "NO")

    def asJson(self):
        return {
            'id': self.pk,
            'estaConfirmado': self.estaConfirmado,
            'viaje': self.viaje.pk,
            'usuario': self.usuario.asJson()
        }


class ConversacionPrivada(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=150)
    fechaHora = models.DateTimeField(auto_created=True)


class ConversacionPublica(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE)
    pregunta = models.CharField(max_length=150)
    respuesta = models.CharField(max_length=150, default=None, null=True)
    fechaHoraPregunta = models.DateTimeField(auto_created=True)
    fechaHoraRespuesta = models.DateTimeField()
