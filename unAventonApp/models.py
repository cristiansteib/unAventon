from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.db.models import Count, Min, Sum, Avg
import json
from django.utils import timezone


class Usuario(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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

    def puedeCrearViaje(self):
        # no tiene calificaciones pendientes
        # tiene auto
        # tiene tarjeta de credito
        # no tiene otro viaje en el mismo horario
        return True

    def tieneCalificicacionesPendientes(self):
        return False

    def calificacionComoPiloto(self):
        return Calificacion.objects.filter(
            paraUsuario=self, viaje__in=Viaje.objects.filter(
                auto__usuario=self
            )
        ).aggregate(
            calificacion=Sum('calificacion')
        )['calificacion']

    def calificacionComoCopiloto(self):
        return Calificacion.objects.filter(
            paraUsuario=self,
            viaje__in=self.viajesConfirmadosComoCopiloto().values('viaje_id')).aggregate(
            calificacion=Sum('calificacion'))['calificacion']

    def calificacionesPendientesParaPiloto(self):
        viajes_confirmados_como_copiloto = self.viajesConfirmadosComoCopiloto()
        if not viajes_confirmados_como_copiloto:
            return []
        return viajes_confirmados_como_copiloto.exclude(
            viaje__in=Calificacion.objects.filter(
                viaje__in=viajes_confirmados_como_copiloto.values_list('viaje'),
                deUsuario=self).values_list('viaje'))

    def calificacionesPendientesParaCopilotos(self):
        viajes = Viaje.objects.filter(auto__usuario=self)  # todos mis viajes
        if not viajes:
            return None
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

    def calificarPiloto(self, calificacion, aUsuario, enViaje, comentario):
        if self.esCopilotoEnViaje(enViaje):
            self.__calificar(calificacion, aUsuario, enViaje, comentario)
            return True
        return False

    def calificarCopiloto(self, calificacion, aUsuario, enViaje, comentario):
        if self.esPilotoEnViaje(enViaje):
            self.__calificar(calificacion, aUsuario, enViaje, comentario)
            return True
        return False

    def viajesEnEsperaComoCopiloto(self):
        return ViajeCopiloto.objects.filter(usuario=self, estaConfirmado=False)

    def viajesConfirmadosComoCopiloto(self):
        return ViajeCopiloto.objects.filter(usuario=self, estaConfirmado=True)

    def viajesCreados(self):
        """ Todos los viajes que creo el usuario"""
        return Viaje.objects.filter(auto__usuario=self)

    def viajesCreadosActivos(self):
        """ Todos los viajes que creados por el usuario, no finalizados"""
        return self.viajesCreados().filter(fechaHoraSalida__gt=timezone.now())

    def viajesFinalizados(self):
        """ Todos los viajes que creados por el usuario, finalizados"""
        return self.viajesCreados().exclude(self.viajesCreadosActivos())

    def esPilotoEnViaje(self, viaje):
        return viaje.auto.usuario == self

    def esCopilotoEnViaje(self, viaje):
        try:
            ViajeCopiloto.objects.get(usuario=self, viaje=viaje)
            return True
        except ViajeCopiloto.DoesNotExist:
            return False

    def tarjetas_de_credito(self):
        return Tarjeta.objects.filter(usuario=self)

    def autos(self):
        return Auto.objects.filter(usuario=self)

    def cuentas_bancarias(self):
        return CuentaBancaria.objects.filter(usuario=self)

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
    def create_viaje(self, *args, **kwargs):
        __json = {
            'creado': False,
            'error': []
        }
        usuario = kwargs['auto'].usuario

        if usuario != kwargs['cuentaBancaria'].usuario:
            __json['error'].append({0: 'La cuenta bancaria no corresponde al usuario conductor'})
        if usuario.tieneCalificicacionesPendientes():
            __json['error'].append({1: 'El usuario tiene calificaciones pendientes'})
        # TODO
        # if usuario.viajesCreadosActivos():
        #    __json['error'].append({2: 'El usuario tiene viajes creados en el rango horario'})
        if not len(__json['error']):
            # no hay errores, entonces se guarda
            viaje = self.create(*args, **kwargs)
            __json['id'] = viaje.pk
            __json['creado'] = True

        return __json

        # return viaje


class Viaje(models.Model):
    auto = models.ForeignKey(Auto, on_delete=models.DO_NOTHING)
    tipoViaje = models.ForeignKey(TipoViaje, on_delete=models.DO_NOTHING, null=True, default=None)
    cuentaBancaria = models.ForeignKey(CuentaBancaria, on_delete=models.DO_NOTHING)
    gasto_total = models.FloatField(default=0.0)
    comentario = models.CharField(max_length=150)
    origen = models.CharField(max_length=20)
    destino = models.CharField(max_length=20)
    fechaHoraSalida = models.DateTimeField()
    duracion = models.IntegerField()
    comision = models.FloatField(default=0.5)

    objects = ViajeManager()

    def __str__(self):
        return "id={0} {1} , de {2} a {3}, fecha {4}".format(self.pk, self.auto.usuario, self.origen, self.destino,
                                                             self.fechaHoraSalida)

    def total_a_reintegrar_al_conductor(self):
        value = self.total_cobrado() - self.comision_a_cobrar()
        return value if value > 0 else 0

    def comision_a_cobrar(self):
        return self.comision * self.gasto_total

    def total_cobrado(self):
        return len(self.copilotos_confirmados()) * self.gasto_por_pasajero()

    def gasto_por_pasajero(self):
        return self.gasto_total / self.auto.capacidad

    def asJson(self):
        data = {
            'id': self.pk,
            'origen': self.origen,
            'destino': self.destino,
            'fecha_hora_salida': self.fechaHoraSalida,
            'fecha_hora_salida_unix': self.fechaHoraSalida.timestamp(),
            'costo_total': self.gasto_total,
            'costo_por_pasajero': self.gasto_por_pasajero(),
            'duracion': self.duracion,
            'auto': self.auto.asJson(),
            'hay_lugar': self.hay_lugar(),
            'asientos_disponibles': self.asientos_disponibles(),
            'usuarios_confirmados': None
        }
        usuarios_confirmados = self.copilotos_confirmados()
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
            'costo_por_pasajero': self.gasto_por_pasajero(),
            'duracion': self.duracion,
            'auto': self.auto.asJson()
        }

    def copilotos_confirmados(self):
        return Usuario.objects.filter(
            pk__in=ViajeCopiloto.objects.filter(
                viaje=self,
                estaConfirmado=True
            ).values('usuario__pk')
        )

    def asientos_disponibles(self):
        asientos_ocupados = ViajeCopiloto.objects.filter(
            viaje=self,
            estaConfirmado=True
        ).aggregate(
            Count('usuario')
        )['usuario__count']
        return self.auto.capacidad - asientos_ocupados

    def hay_lugar(self):
        return True if self.asientos_disponibles() else False

    def copilotos_en_lista_de_espera(self):
        return ViajeCopiloto.objects.filter(viaje=self, estaConfirmado=False)

    def agregar_copiloto_en_lista_de_espera(self, usuario):
        ViajeCopiloto.objects.create(
            viaje=self,
            usuario=usuario
        )

    def conversacion_publica(self):
        return ConversacionPublica.objects.filter(viaje=self).order_by('fechaHoraPregunta')

    def conversacion_privada(self):
        return ConversacionPrivada.objects.filter(viaje=self).order_by('fechaHora')


class ViajeCopiloto(models.Model):
    class Meta:
        unique_together = (('usuario', 'viaje'),)

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE)
    estaConfirmado = models.BooleanField(default=False)
    fechaHoraDeSolicitud = models.DateTimeField(auto_created=True)

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
