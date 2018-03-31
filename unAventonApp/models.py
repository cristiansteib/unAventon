from django.db import models
from django.contrib.auth.models import User





class Profile(models.Model):
    ''' es el modelo customizado de user '''
    nombre = models.CharField(max_length=15)
    apellido = models.CharField(max_length=15)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    fechaDeNacimiento = models.DateField()
    dni = models.CharField(max_length=10)
    calificacionComoConductor = models.FloatField(default=0)
    calificacionComoConductorCantidad = models.IntegerField(default=0)
    calificacionComoPasajero = models.FloatField(default=0)
    calificacionComoPasajeroCantidad = models.IntegerField(default=0)

    def __str__(self):
        return "{0} {1}".format(self.nombre, self.apellido)



class Driver(models.Model):
    pass

class Passanger(models.Model):
    pass



class BankEntity(models.Model):
    '''
    Sirve para mantener los nombres de las entidades
    para las tarjetas de creditos
    '''
    nombre = models.CharField(max_length=30)



class Creditcard(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    entidad = models.ForeignKey(BankEntity, on_delete=models.PROTECT)
    fechaVencimiento = models.DateField(auto_now_add=True, blank=True)
    numeroDeTarjeta = models.CharField(max_length=16)
    numeroDeSeguridadCVV = models.CharField(max_length=4)



class Trip(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    creationDateTime = models.DateTimeField(auto_now_add=True)
    expirationDateTime = models.DateTimeField()
    destinationLatitude = models.DecimalField(max_digits=9, decimal_places=6)
    destinationLongitude = models.DecimalField(max_digits=9, decimal_places=6)
    beginningLatitude = models.DecimalField(max_digits=9, decimal_places=6)
    beginningLongitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return "Trip {0}".format(self.id)


class ConversationPublicThread(models.Model):
    ''' las conversaciones publicas con pregunta respuesta'''
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    question = models.CharField(max_length=250)
    answer = models.CharField(max_length=250, default=None, null=True)
    answerDateTime = models.DateTimeField()
    questionDateTime = models.DateTimeField()
    enable = models.BooleanField(default=True)


class ConversationPrivateThread(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    message = models.CharField(max_length=250)
    messageDateTime = models.DateTimeField()
    enable = models.BooleanField(default=True)


# vehiculo...