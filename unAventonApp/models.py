from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.utils import timezone
import ast


class Usuario(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=15)
    apellido = models.CharField(max_length=15)
    fechaDeNacimiento = models.DateField()
    dni = models.CharField(max_length=15)

    def calificacionComoPiloto(self):
        pass

    def calificacionComoCopiloto(self):
        pass

    def calificacionesPendientesParaPiloto(self):
        raise NotImplementedError

    def calificacionesPendientesParaCopilotos(self):
        raise NotImplementedError

    def __calificar(self, calificacion, aUsuario, enViaje, comentario):
        c = Calificacion()
        c.deUsuario = self
        c.paraUsuario = aUsuario
        c.comentario = comentario
        c.viaje = enViaje
        c.calificacion = calificacion
        c.save()

    def calificarPiloto(self, calificacion, aUsuario, enViaje, comentario):
        if not self.esCopilotoEnViaje(enViaje):
            return False
        self.__calificar(calificacion, aUsuario, enViaje, comentario)
        return True

    def calificarCopiloto(self, calificacion, aUsuario, enViaje, comentario):
        if not self.esPilotoEnViaje(enViaje):
            return False
        self.__calificar(calificacion, aUsuario, enViaje, comentario)
        return True

    def viajesEnEsperaComoCopiloto(self):
        return ViajeCopiloto.objects.filter(usuario=self, estaConfirmado=False)

    def viajesConfirmadosComoCopiloto(self):
        return ViajeCopiloto.objects.filter(usuario=self, estaConfirmado=True)

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
    cbu = models.DateField()


class Auto(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    dominio = models.CharField(max_length=15)
    marca = models.CharField(max_length=15)
    modelo = models.CharField(max_length=15)
    capacidad = models.IntegerField()


class TipoViaje(models.Model):
    tipo = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=150)


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


class ViajeCopiloto(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE)
    estaConfirmado = models.BooleanField(default=False)
    fechaHoraDeSolicitud = models.DateTimeField(auto_created=True)

    def confirmarCopiloto(self):
        self.estaConfirmado = True
        self.save()


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

