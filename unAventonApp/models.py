from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.db.models import Count, Min, Sum, Avg
from django.utils import timezone
import ast
import json
from datetime import datetime


class Usuario(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=15)
    apellido = models.CharField(max_length=15)
    fechaDeNacimiento = models.DateField()
    dni = models.CharField(max_length=15)

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
        return Calificacion.objects.filter(viaje__in=Viaje.objects.filter(auto__usuario=self)).aggregate(
            calificacion=Sum('calificacion'))['calificacion__count']

    def calificacionComoCopiloto(self):
        return Calificacion.objects.filter(viaje__in=ViajeCopiloto.objects.filter(usuario=self)).aggregate(
            calificacion=Sum('calificacion'))['calificacion__count']

    def calificacionesPendientesParaPiloto(self):
        viajesConfirmadosComoCopiloto = ViajeCopiloto.objects.filter(
            usuario=self,
            estaConfirmado=True)  # todos mis viajes como copiloto
        if not viajesConfirmadosComoCopiloto:
            return None
        return viajesConfirmadosComoCopiloto.exclude(
            viaje__in=Calificacion.objects.filter(
                viaje__in=viajesConfirmadosComoCopiloto.values_list('viaje'),
                deUsuario=self).values_list('viaje'))

    def calificacionesPendientesParaCopilotos(self):
        viajes = Viaje.objects.filter(auto__usuario=self)  # todos mis viajes
        if not viajes:
            return None
        return ViajeCopiloto.objects.filter(viaje__in=viajes, estaConfirmado=True).exclude(
            viaje__in=Calificacion.objects.filter(viaje__in=viajes, deUsuario=self).values_list('viaje')
        )

    def __calificar(self, calificacion, aUsuario, enViaje, comentario):
        c = Calificacion()
        c.deUsuario = self
        c.paraUsuario = aUsuario
        c.comentario = comentario
        c.viaje = enViaje
        c.calificacion = calificacion
        c.save()

    def calificarPiloto(self, calificacion, aUsuario, enViaje, comentario):
        if self.esPilotoEnViaje(enViaje):
            return False
        self.__calificar(calificacion, aUsuario, enViaje, comentario)
        return True

    def calificarCopiloto(self, calificacion, aUsuario, enViaje, comentario):
        if self.esCopilotoEnViaje(enViaje):
            return False
        self.__calificar(calificacion, aUsuario, enViaje, comentario)
        return True

    def viajesEnEsperaComoCopiloto(self):
        return ViajeCopiloto.objects.filter(usuario=self, estaConfirmado=False)

    def viajesConfirmadosComoCopiloto(self):
        return ViajeCopiloto.objects.filter(usuario=self, estaConfirmado=True)

    def viajesCreados(self):
        """ Todos los viajes que creo el usuario"""
        return Viaje.objects.filter(auto__usuario=self)

    def viajesCreadosActivos(self):
        """ Todos los viajes que creados por el usuario, no finalizados"""
        return self.viajesCreados().filter(fechaHoraSalida__lt=datetime.now())

    def viajesFinalizados(self):
        """ Todos los viajes que creados por el usuario, finalizados"""
        return self.viajesCreados().exclude(self.viajesCreadosActivos())

    def esPilotoEnViaje(self, viaje):
        return viaje.auto.usuario == self

    def esCopilotoEnViaje(self, viaje):
        try:
            ViajeCopiloto.objects.get(usuario=self, viaje=viaje)
            return True
        except IntegrityError:
            return False


class Tarjeta(models.Model):
    usuario = models.ManyToManyField(Usuario)
    numero = models.CharField(max_length=16)
    fechaDeVencimiento = models.DateField()
    ccv = models.IntegerField()


class CuentaBancaria(models.Model):
    usuario = models.ManyToManyField(Usuario)
    cbu = models.CharField(max_length=20)

    def __str__(self):
        return "CBU = {0}".format(self.cbu)

    def asJson(self):
        return json.dumps(
            {
                'id': self.pk,
                'cbu': self.cbu
            },
            sort_keys=True,
            indent=4)


class Auto(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    dominio = models.CharField(max_length=15)
    marca = models.CharField(max_length=15)
    modelo = models.CharField(max_length=15)
    capacidad = models.IntegerField()

    def asJson(self):
        # todo
        pass


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


class Viaje(models.Model):
    auto = models.ForeignKey(Auto, on_delete=models.DO_NOTHING)
    tipoViaje = models.ForeignKey(TipoViaje, on_delete=models.DO_NOTHING)
    cuentaBancaria = models.ForeignKey(CuentaBancaria, on_delete=models.DO_NOTHING)
    gastoTotal = models.FloatField(default=0.0)
    comentario = models.CharField(max_length=150)
    origen = models.CharField(max_length=20)
    destino = models.CharField(max_length=20)
    fechaHoraSalida = models.DateTimeField()
    duracion = models.IntegerField()

    def crearViaje(self, usuario, *args, **kwargs):
        """
        Este metodo resuelve lo necesario para crear un viaje.
        Chequea las reglas de negocio que permiten creear un viaje.
        Y retorna un Json con los errores

        :param usuario:
        :param args:
        :param kwargs:
        :return:
        """

        __json = {
            'creado': False,
            'error': []
        }

        if not self.pk:
            if self.auto.usuario != self.cuentaBancaria.usuario:
                __json['error'].append({0: 'La cuenta bancaria no corresponde al usuario conductor'})
            if usuario.tieneCalificicacionesPendientes():
                __json['error'].append({1: 'El usuario tiene calificaciones pendientes'})
            if usuario.viajesCreadosActivos().filter():
                __json['error'].append({2: 'El usuario tiene viajes creados en el rango horario'})
            if not len(__json['error']):
                # no hay errores, entonces se guarda
                super(Viaje, self).save(args, kwargs)
                __json['creado'] = True

        return json.dumps(__json, sort_keys=True, indent=4 )

    def hayLugar(self):
        lugaresOcupados = ViajeCopiloto.objects.filter(
            viaje=self,
            estaConfirmado=True
        ).aggregate(Count('usuario'))['usuario__count']
        capacidad = self.auto.capacidad
        return lugaresOcupados < capacidad

    def copilotosEnListaDeEspera(self):
        return ViajeCopiloto.objects.filter(viaje=self, estaConfirmado=False)

    def agregarCopilotoEnListaDeEspera(self, usuario):
        ViajeCopiloto.objects.create(
            viaje=self,
            usuario=usuario
        )

    def conversacionPublica(self):
        return ConversacionPublica.objects.filter(viaje=self).order_by('fechaHoraPregunta')

    def conversacionPrivada(self):
        return ConversacionPrivada.objects.filter(viaje=self).order_by('fechaHora')

    def gastoPorPasajero(self):
        return self.gastoTotal / self.auto.capacidad

    def publicacionAsJson(self):
        """ Datos publicos para todos los usuarios """
        return json.dumps(
            {
                'auto': self.auto.asJson(),
                'tipoViaje': self.tipoViaje.asJson(),
                'gastoTotal': self.gastoTotal,
                'gastoPorPasajero': self.gastoPorPasajero,
                'origen': self.origen,
                'destino': self.destino,
                'fechaHoraSalida': self.fechaHoraSalida,
                'duracion': self.duracion
            },
            sort_keys=True,
            indent=4)

    def asJson(self):
        """ Hay datos privados, que solamente los deberia ver el usuario creador """
        return json.dumps(
            {
                'auto': self.auto.asJson(),
                'tipoViaje': self.tipoViaje.asJson(),
                'gastoTotal': self.gastoTotal,
                'gastoPorPasajero': self.gastoPorPasajero,
                'origen': self.origen,
                'destino': self.destino,
                'fechaHoraSalida': self.fechaHoraSalida,
                'duracion': self.duracion,
                'cuentaBancaria': self.cuentaBancaria.asJson()
            },
            sort_keys=True,
            indent=4)


class ViajeCopiloto(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE)
    estaConfirmado = models.BooleanField(default=False)
    fechaHoraDeSolicitud = models.DateTimeField(auto_created=True)

    def confirmarCopiloto(self):
        self.estaConfirmado = True
        self.save()

    def __str__(self):
        return "Copiloto: {0}, Confirmado: {1} ".format(str(self.usuario), "SI" if self.estaConfirmado else "NO")


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
    comentario = models.CharField(max_length=150)
    calificacion = models.IntegerField()
