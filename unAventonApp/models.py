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

        if (self.se_superpone_algun_viaje_como_piloto(fecha_hora_salida, duracion)):
            mensaje['error'].append(
                {102: 'Tenes algun viaje como piloto en el mismo rango horario.'})

        if (self.se_superpone_algun_viaje_como_copiloto(fecha_hora_salida, duracion)):
            mensaje['error'].append(
                {103: 'Tenes algun viaje aceptado como copiloto en el mismo rango horario ingresado.'})

        return True if not len(mensaje['error']) else False, mensaje

    def se_superpone_algun_viaje_como_copiloto(self, fecha_hora_salida, duracion):
        ##check que no este en uso en otro viaje en el mismo rango horario como copiloto
        viajes_como_copiloto = Viaje.objects.filter(
            pk__in=self.get_viajes_confirmados_como_copiloto().values('viaje_id'))
        return self.__se_superpone_rango_horario(fecha_hora_salida, duracion, viajes_como_copiloto)

    def se_superpone_algun_viaje_como_piloto(self, fecha_hora_salida, duracion):
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
        return sp(fecha_hora_salida, duracion, viajes_mismo_dia) or sp(fecha_hora_salida, duracion,
                                                                       viajes_diarios) or sp(fecha_hora_salida,
                                                                                             duracion, viajes_semanales)

    def se_superpone_algun_viaje(self, fecha_hora_salida, duracion):
        return self.se_superpone_algun_viaje_como_copiloto(fecha_hora_salida, duracion) \
               or \
               self.se_superpone_algun_viaje_como_piloto(fecha_hora_salida, duracion)

    @staticmethod
    def __se_superpone_rango_horario(fecha_hora_inicio, duracion, viajesCollection):
        # FIXME: para viajes semanales, y diarios, si la fecha es anterior a otro viaje creado, no chequea el solapamiento
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
        # todas las calificaciones con sus comentarios como piloto
        pass

    def get_calificacion_como_copiloto(self):
        # todas las calificaciones con sus comentarios como piloto
        pass

    def get_puntaje_como_piloto(self):
        viajes_realizados = ViajeCopiloto.objects.filter(estaConfirmado=True, viaje__auto__usuario=self)
        puntaje = viajes_realizados.aggregate(Sum('calificacion_a_piloto'))['calificacion_a_piloto__sum']
        print('calif como piloto', puntaje)
        return puntaje

    def get_puntaje_como_copiloto(self):
        pass

    def get_calificaciones_pendientes_para_piloto(self):
        pass

    def get_calificaciones_pendientes_para_copilotos(self):
        pass

    def __calificar(self, calificacion, aUsuario, enViaje, comentario):
        pass

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

    def get_tarjetas_de_credito(self):
        return Tarjeta.objects.filter(usuario=self, esta_activo=True)

    def get_autos(self):
        return Auto.objects.filter(usuario=self, esta_activo=True)

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
        return len(self.get_viajes_creados_activos().filter(cuenta_bancaria=unaCuentaBancaria,
                                                            cuenta_bancaria__esta_activo=True)) > 0

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


class Viaje(models.Model):
    auto = models.ForeignKey(Auto, on_delete=models.DO_NOTHING)
    auto_lugares_ocupados_de_antemano = models.IntegerField(default=0)  # estos no se cobran
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

    def caeEnLaFecha(self, unaFecha):
        # retorna un booleano, si el viaje cae en la fecha unaFecha, no chequea por hora

        fecha = datetime.datetime.strptime(unaFecha, '%Y-%m-%d')
        # viaje semanal
        if self.se_repite.count('sem'):
            return (self.fecha_hora_salida.weekday() == fecha.weekday()) and (
                    self.fecha_hora_salida.date() <= fecha.date())
        # viaje unico
        elif self.se_repite.count('nun'):
            return self.fecha_hora_salida.date() == fecha.date()

        # viaje diario
        elif self.se_repite.count('dia'):
            return self.fecha_hora_salida.date() <= fecha.date()

        # TODO: @seba checkear

    def caeEnLaHora(self, unaHora):
        # retorna un booleano, si el viaje cae en la hora unaHora, no chequea por fecha
        def crear_hora(hora, minuto):
            return datetime.datetime(1, 1, 1, hora, minuto)

        delta = 1800  # margen de 30 minutos para matchear mas viajes, en segundos
        hora = datetime.datetime.strptime(unaHora, '%H:%M')
        horarios = (
            crear_hora(hora.hour, hora.minute), crear_hora(self.fecha_hora_salida.hour, self.fecha_hora_salida.minute))
        return delta >= (max(horarios) - min(horarios)).seconds

    # todo!!
    def datos_del_viaje_en_fecha(self, fecha):
        """ retorna un json con los datos asoc al
        viaje segun la fecha"""

        return {
            'viaje': self,
            'fecha_hora_salida': fecha,
            'fecha_hora_salida_unix': fecha.timestamp(),
            'get_comision_cobrada': self.get_comision_cobrada_en_fecha(fecha),
            'get_total_a_reintegrar_al_conductor': self.get_total_a_reintegrar_al_conductor_en_fecha(fecha),
            'get_count_copilotos_confirmados': self.get_count_copilots_confirmados_en_fecha(fecha),
            'tiene_calificacion_pendientes_a_copilotos': self.tiene_calificacion_pendientes_a_copilotos_en_fecha(fecha)

        }

    # ready
    def datos_del_viaje(self):
        return self.datos_del_viaje_en_fecha(self.proxima_fecha_de_salida())

    def eliminar(self):
        self.activo = False
        conjunto = set()

        viajeCopilotos = ViajeCopiloto.objects.filter(viaje=self, estaConfirmado=True)
        for viajCop in viajeCopilotos:
            if viajCop.fecha_del_viaje not in conjunto:
                viajCop.cancelarCopiloto()
            else:
                viajCop.rechazarCopiloto()
            conjunto.add(viajCop.fecha_del_viaje)

        self.save()

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

    def activar(self):
        self.activo = True
        self.save()

    def desactivar(self):
        self.activo = False
        self.save()

    def esta_activo(self):
        return self.activo

    # ready
    def get_total_a_reintegrar_al_conductor_en_fecha(self, fecha):
        value = self.get_total_cobrado_fecha(fecha) - self.get_comision_a_cobrar()
        return value if value > 0 else 0

    # ready
    def get_total_a_reintegrar_al_conductor(self):
        return self.get_total_a_reintegrar_al_conductor_en_fecha(self.proxima_fecha_de_salida())

    # ready
    def get_comision_a_cobrar(self):
        return self.comision * self.gasto_total

    # ready
    def get_total_cobrado_fecha(self, fecha):
        return len(self.get_copilotos_confirmados_en_fecha(fecha)) * self.get_costo_por_pasajero()

    # ready
    def get_total_cobrado(self):
        return self.get_total_cobrado_fecha(self.proxima_fecha_de_salida())

    def get_costo_por_pasajero(self):
        return self.gasto_total / self.auto.capacidad

    def get_estado_del_viaje(self):
        # todo ??
        """ retorna un string con el estado del viaje"""
        return ""

    def get_se_repite_asString(self):
        import ast
        frecuencia, dia = ast.literal_eval(self.se_repite)
        dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        if frecuencia == 'diario':
            return "Este viaje se repite todas los dias"
        elif frecuencia == 'semanal':
            return "Se repite todos los " + dias[dia].capitalize() + ", todas las semanas."
        elif frecuencia == 'nunca':
            return "Viaje unico"
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
            'se_repite': self.get_se_repite_asString(),
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
            'fecha_hora_salida': self.fecha_hora_salida,
            'fecha_hora_salida_unix': self.fecha_hora_salida.timestamp(),
            'costo_por_pasajero': self.get_costo_por_pasajero(),
            'duracion': self.duracion,
            'comentario': self.comentario,
            'se_repite': self.get_se_repite_asString(),
            'auto': self.auto.asJson()
        }

    # ready
    def get_copilotos_confirmados_en_fecha(self, fecha):
        return ViajeCopiloto.objects.filter(
            viaje=self,
            estaConfirmado=True,
            fecha_del_viaje=fecha
        )

    # ready
    def get_copilotos_confirmados(self):
        return self.get_copilotos_confirmados_en_fecha(self.proxima_fecha_de_salida())

    # ready
    def get_count_copilots_confirmados_en_fecha(self, fecha):
        return len(Usuario.objects.filter(
            pk__in=ViajeCopiloto.objects.filter(
                viaje=self,
                estaConfirmado=True,
                fecha_del_viaje=fecha
            ).values('usuario__pk')
        ))

    # ready
    def get_count_copilotos_confirmados(self):
        return self.get_count_copilots_confirmados_en_fecha(self.proxima_fecha_de_salida())

    # ready
    def get_asientos_disponibles_en_fecha(self, fecha):
        asientos_ocupados = ViajeCopiloto.objects.filter(
            viaje=self,
            fecha_del_viaje=fecha,
            estaConfirmado=True
        ).aggregate(
            Count('usuario')
        )['usuario__count']
        return self.auto.capacidad - asientos_ocupados - self.auto_lugares_ocupados_de_antemano

    # ready
    def get_asientos_disponibles(self):
        return self.get_asientos_disponibles_en_fecha(self.proxima_fecha_de_salida())

    # ready
    def hay_lugar_en_fecha(self, fecha):
        return True if self.get_asientos_disponibles_en_fecha(fecha) else False

    # ready
    def hay_lugar(self):
        return self.hay_lugar_en_fecha(self.proxima_fecha_de_salida())

    # ready
    def get_copilotos_en_lista_de_espera_en_fecha(self, fecha):
        return ViajeCopiloto.objects.filter(viaje=self, estaConfirmado=None, fecha_del_viaje=fecha)

    # ready
    def get_copilotos_en_lista_de_espera(self):
        return self.get_copilotos_en_lista_de_espera_en_fecha(self.proxima_fecha_de_salida())

    # ready
    def get_count_copilotos_en_lista_de_espera_en_fecha(self, fecha):
        return len(ViajeCopiloto.objects.filter(viaje=self, estaConfirmado=None, fecha_del_viaje=fecha))

    # ready
    def get_count_copilotos_en_lista_de_espera(self):
        return self.get_count_copilotos_en_lista_de_espera_en_fecha(self.proxima_fecha_de_salida())

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

    def tiene_calificacion_pendientes_a_copilotos_en_fecha(self, fecha):
        vc = ViajeCopiloto.objects.filter(
            viaje=self,
            fecha_del_viaje=fecha,
            estaConfirmado=True,
            calificacion_a_copiloto=None
        )
        for v in vc:
            print(v.pk)
        return True if vc else False

    def tiene_calificacion_pendientes_a_copilotos(self):
        self.tiene_calificacion_pendientes_a_copilotos_en_fecha(self.proxima_fecha_de_salida())

    def get_comision_cobrada_en_fecha(self, fecha):
        return self.get_comision_a_cobrar() if self.get_total_a_reintegrar_al_conductor_en_fecha(fecha) > 0 else 0

    # ready
    def get_comision_cobrada(self):
        return self.get_comision_cobrada_en_fecha(self.proxima_fecha_de_salida())


class ViajeCopiloto(models.Model):
    class Meta:
        unique_together = (('usuario', 'viaje', 'fecha_del_viaje'),)

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # el copiloto
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE)
    fecha_del_viaje = models.DateTimeField()
    tarjeta = models.ForeignKey(Tarjeta, on_delete=models.DO_NOTHING, null=True)  # el copiloto
    estaConfirmado = models.NullBooleanField(default=None, null=True)
    fecha_hora_de_solicitud = models.DateTimeField(auto_created=True, default=timezone.now)
    calificacion_a_piloto = models.IntegerField(default=None, null=True, blank=True)
    calificacion_a_piloto_mensaje = models.CharField(max_length=150, default=None, null=True, blank=True)
    calificacion_a_copiloto = models.IntegerField(default=None, null=True, blank=True)
    calificacion_a_copiloto_mensaje = models.CharField(max_length=150, default=None, null=True, blank=True)

    def calificar_a_copiloto(self, calificacion, comentario):
        self.calificacion_a_copiloto = calificacion
        self.calificacion_a_copiloto_mensaje = comentario
        self.save()

    def calificar_a_piloto(self, calificacion, comentario):
        self.calificacion_a_piloto = calificacion
        self.calificacion_a_piloto_mensaje = comentario
        self.save()

    def esta_el_copiloto_calificado(self):
        return self.calificacion_a_copiloto is not None

    def get_estado(self):
        estados = ("esperando", "confirmado", "rechazado", "finalizado")
        if self.estaConfirmado is None:
            return estados[0]
        if self.estaConfirmado is False:
            return estados[2]
        if (self.fecha_del_viaje < timezone.now()) and (self.estaConfirmado):
            return estados[3]
        if self.estaConfirmado:
            return estados[1]

    def confirmarCopiloto(self):
        # todo: chequear que no este en otro viaje
        if self.viaje.hay_lugar_en_fecha(self.fecha_del_viaje):
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
