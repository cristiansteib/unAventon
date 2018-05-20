from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.db.models import Count, Min, Sum, Avg
import json
from django.utils import timezone
from django.conf import settings
import datetime
from collections import namedtuple


class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=15, )
    apellido = models.CharField(max_length=15)
    fechaDeNacimiento = models.DateField(default=None, null=True)
    dni = models.CharField(max_length=15, default=None, null=True)

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
        viajes_semanales = self.get_viajes_semanales_activos_para_weekday(week_day).filter(fecha_hora_salida__lte=fecha_hora_salida)


        viajes_mismo_dia = viajes_activos.filter(
            fecha_hora_salida__year=fecha_hora_salida.year,
            fecha_hora_salida__month=fecha_hora_salida.month,
            fecha_hora_salida__day=fecha_hora_salida.day)

        sp = self.__se_superpone_rango_horario
        if sp(fecha_hora_salida, duracion, viajes_mismo_dia) or sp(fecha_hora_salida, duracion, viajes_diarios) or sp(fecha_hora_salida, duracion, viajes_semanales):
            mensaje['error'].append({102: 'Tenes algun viaje como piloto en el mismo rango horario.'})

        ##check que no este en uso en otro viaje en el mismo rango horario como copiloto
        viajes_como_copiloto = Viaje.objects.filter(
            pk__in=self.get_viajes_confirmados_como_copiloto().values('viaje_id'))
        if self.__se_superpone_rango_horario(fecha_hora_salida, duracion, viajes_como_copiloto):
            mensaje['error'].append(
                {103: 'Tenes algun viaje aceptado como copiloto en el mismo rango horario ingresado.'})

        return True if not len(mensaje['error']) else False, mensaje

    @staticmethod
    def __se_superpone_rango_horario(fecha_hora_salida, duracion, viajes):
        duracion = int(duracion)

        def get_overlap(lowest_value, start1, end1, start2, end2):
            Range = namedtuple('Range', ['start', 'end'])
            r1 = Range(start=start1, end=end1)
            r2 = Range(start=start2, end=end2)
            latest_start = max(r1.start, r2.start)
            earliest_end = min(r1.end, r2.end)
            delta = (earliest_end - latest_start)
            return max(lowest_value, delta)


        def sumar_tiempo(hora, minutos, incremento):
            delta = datetime.timedelta(hours=incremento)
            hora_final = datetime.datetime(1, 1, 1, hora, minutos) + delta
            return hora_final

        import datetime
        fecha_hora_salida_start = datetime.datetime(1, 1, 1, fecha_hora_salida.hour, fecha_hora_salida.minute)
        fecha_hora_salida_end = sumar_tiempo(fecha_hora_salida.hour, fecha_hora_salida.minute, duracion)
        slow_value = datetime.timedelta(0,0)
        for viaje in viajes:
            viaje_datetime_start = datetime.datetime(1, 1, 1, viaje.fecha_hora_salida.hour, viaje.fecha_hora_salida.minute)
            viaje_datetime_end = sumar_tiempo(viaje.fecha_hora_salida.hour, viaje.fecha_hora_salida.minute, viaje.duracion)

            overlap = get_overlap(slow_value, viaje_datetime_start, viaje_datetime_end, fecha_hora_salida_start, fecha_hora_salida_end )
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
        p1 = self.get_calificaciones_pendientes_para_piloto().filter(
            viaje__fecha_hora_salida__lte=timezone.now() - timezone.timedelta(days=maximo_dias))
        p2 = self.get_calificaciones_pendientes_para_copilotos().filter(
            viaje__fecha_hora_salida__lte=timezone.now() - timezone.timedelta(days=maximo_dias))
        return len(p1) + len(p2)

    def tiene_calificicaciones_pendientes(self):
        return self.get_calificaciones_pendientes_para_piloto() or self.get_calificaciones_pendientes_para_copilotos()

    def get_calificacion_como_piloto(self):
        return Calificacion.objects.filter(
            paraUsuario=self, viaje__in=Viaje.objects.filter(
                auto__usuario=self
            )
        ).aggregate(
            calificacion=Sum('calificacion')
        )['calificacion']

    def get_calificacion_como_copiloto(self):
        return Calificacion.objects.filter(
            paraUsuario=self,
            viaje__in=self.get_viajes_confirmados_como_copiloto().values('viaje_id')).aggregate(
            calificacion=Sum('calificacion'))['calificacion']

    def get_calificaciones_pendientes_para_piloto(self):

        viajes_confirmados_como_copiloto = self.get_viajes_confirmados_como_copiloto()
        if not viajes_confirmados_como_copiloto:
            return models.QuerySet(ViajeCopiloto)
        return viajes_confirmados_como_copiloto.exclude(
            viaje__in=Calificacion.objects.filter(
                viaje__in=viajes_confirmados_como_copiloto.values_list('viaje'),
                deUsuario=self).values_list('viaje'))

    def get_calificaciones_pendientes_para_copilotos(self):
        viajes = Viaje.objects.filter(auto__usuario=self)  # todos mis viajes
        if not viajes:
            return models.QuerySet(ViajeCopiloto)
        viajesCopiloto = ViajeCopiloto.objects.filter(viaje__in=viajes, estaConfirmado=True).exclude(
            usuario__in=Calificacion.objects.filter(viaje__in=viajes, deUsuario=self).values_list('paraUsuario')
        )
        return viajesCopiloto

    def __calificar(self, calificacion, aUsuario, enViaje, comentario):
        c = Calificacion()
        c.deUsuario = self
        c.paraUsuario = aUsuario
        c.comentario = comentario
        c.viaje = enViaje
        c.calificacion = calificacion
        c.save()

    def set_calificar_piloto(self, calificacion, aUsuario, enViaje, comentario):
        if self.es_copiloto_en_viaje(enViaje):
            self.__calificar(calificacion, aUsuario, enViaje, comentario)
            return True
        return False

    def set_calificar_copiloto(self, calificacion, aUsuario, enViaje, comentario):
        if self.es_piloto_en_viaje(enViaje):
            self.__calificar(calificacion, aUsuario, enViaje, comentario)
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
        return Tarjeta.objects.filter(usuario=self)

    def get_autos(self):
        return Auto.objects.filter(usuario=self)

    def get_cuentas_bancarias(self):
        return CuentaBancaria.objects.filter(usuario=self)

    def set_nuevo_viaje(self, datos):
        json_info = Viaje.objects.create_viaje(usuario=self, **datos)
        return json_info
    def get_viajes_unicos_activos(self):
        return self.get_viajes_creados_activos().filter(se_repite__contains='nunca')

class Tarjeta(models.Model):
    usuario = models.ManyToManyField(Usuario)
    numero = models.CharField(max_length=16)
    fechaDeVencimiento = models.DateField()
    ccv = models.IntegerField()

    def asJson(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'fecha_de_vencimiento': self.fechaDeVencimiento
        }


class CuentaBancaria(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cbu = models.CharField(max_length=20)
    entidad = models.CharField(max_length=20, default=None, null=True)

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

    def __str__(self):
        return '{0} ---> {1}'.format(self.usuario, self.dominio)

    def asJson(self):
        # TODO: falta completar
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
            #viaje.delete()
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

    def buscar_viaje(self,origen, destino, fecha):
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

    def get_asientos_disponibles(self):
        asientos_ocupados = ViajeCopiloto.objects.filter(
            viaje=self,
            estaConfirmado=True
        ).aggregate(
            Count('usuario')
        )['usuario__count']
        return self.auto.capacidad - asientos_ocupados

    def hay_lugar(self):
        return True if self.get_asientos_disponibles() else False

    def get_copilotos_en_lista_de_espera(self):
        return ViajeCopiloto.objects.filter(viaje=self, estaConfirmado=False)

    def set_agregar_copiloto_en_lista_de_espera(self, usuario):
        return ViajeCopiloto.objects.create(
            viaje=self,
            usuario=usuario
        )

    def get_conversacion_publica(self):
        return ConversacionPublica.objects.filter(viaje=self).order_by('fechaHoraPregunta')

    def get_conversacion_privada(self):
        return ConversacionPrivada.objects.filter(viaje=self).order_by('fechaHora')


class ViajeCopiloto(models.Model):
    class Meta:
        unique_together = (('usuario', 'viaje', 'fecha_del_viaje'),)

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE)
    fecha_del_viaje = models.DateTimeField()
    estaConfirmado = models.BooleanField(default=False)
    fecha_hora_de_solicitud = models.DateTimeField(auto_created=True, default=timezone.now())

    def confirmarCopiloto(self):
        if self.viaje.hay_lugar():
            self.estaConfirmado = True
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


class Calificacion(models.Model):
    class Meta:
        unique_together = (('deUsuario', 'paraUsuario', 'viaje'),)

    deUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='Calificacion.deUsuario+')
    paraUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, )
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=150, default=None, null=True)
    calificacion = models.IntegerField()
