from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import ast


class Profile(models.Model):
    ''' es el modelo customizado de user '''
    name = models.CharField(max_length=15)
    lastName = models.CharField(max_length=15)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    birthdate = models.DateField()
    dni = models.CharField(max_length=10)

    def __str__(self):
        return "{0} {1}".format(self.name, self.lastName)


class Driver(models.Model):
    profile = models.OneToOneField(Profile, unique=True, on_delete=models.CASCADE)
    calification = models.FloatField(default=0)
    calificationCount = models.IntegerField(default=0)

    def calificatePositive(self):
        self.__calificate(+1)

    def calificateNeutral(self):
        self.__calificate(0)

    def calificateNegative(self):
        self.__calificate(-1)

    def __calificate(self, punctuation):
        self.calification = self.calification + punctuation
        self.calificationCount += 1
        self.save()


class Passenger(models.Model):
    profile = models.OneToOneField(Profile, unique=True, on_delete=models.CASCADE)
    calification = models.FloatField(default=0)
    calificationCount = models.IntegerField(default=0)

    def calificatePositive(self):
        self.__calificate(+1)

    def calificateNeutral(self):
        self.__calificate(0)

    def calificateNegative(self):
        self.__calificate(-1)

    def __calificate(self, punctuation):
        self.calification = self.calification + punctuation
        self.calificationCount += 1
        self.save()


class Car(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    domain = models.CharField(max_length=8, unique=True)
    brand = models.CharField(max_length=15)
    model = models.CharField(max_length=15)
    year = models.IntegerField()
    capacity = models.IntegerField()


class BankEntity(models.Model):
    '''
    Sirve para mantener los nombres de las entidades
    para las tarjetas de creditos
    '''
    name = models.CharField(max_length=30)


class Creditcard(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    entity = models.ForeignKey(BankEntity, on_delete=models.PROTECT)
    expirationDate = models.DateField(auto_now_add=True, blank=True)
    cardNumber = models.CharField(max_length=16)
    CVV = models.CharField(max_length=4)


class Trip(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    creationDateTime = models.DateTimeField(auto_now_add=True)
    expirationDateTime = models.DateTimeField()
    passengersConfirmed = models.CharField(default='[]', max_length=200)
    passengersRequestQueue = models.CharField(default='[]', max_length=20)
    destinationLatitude = models.DecimalField(max_digits=9, decimal_places=6)
    destinationLongitude = models.DecimalField(max_digits=9, decimal_places=6)
    beginningLatitude = models.DecimalField(max_digits=9, decimal_places=6)
    beginningLongitude = models.DecimalField(max_digits=9, decimal_places=6)

    def confirmPassenger(self, passenger_id):
        ''' un pasajero que esta en la lista de espera de confirmacion, puede ser agregado
          como confirmado'''
        if not self.isInRequestQueue(passenger_id):
            return False
        queueConfirmed = ast.literal_eval(self.passengersConfirmed)
        queueConfirmed.append(passenger_id)
        self.passengersConfirmed = str(queueConfirmed)
        self.save()
        return True

    def isInRequestQueue(self, passenger_id):
        queueReq = ast.literal_eval(self.passengersRequestQueue)
        if passenger_id not in queueReq:
            return False
        return True

    def addPassengerToRequestQueue(self, passenger_id):
        ''' se agrega a la cola de espera de confirmacion'''
        queueReq = ast.literal_eval(self.passengersRequestQueue)
        queueReq.append(passenger_id)
        self.passengersRequestQueue = str(queueReq)
        self.save()

    def __str__(self):
        return "Trip {0}".format(self.id)


class ConversationPublicThread(models.Model):
    ''' las conversaciones publicas con pregunta respuesta'''
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)  # quien hizo la pregunta
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    question = models.CharField(max_length=250)
    answer = models.CharField(max_length=250, default=None, null=True)
    answerDateTime = models.DateTimeField(blank=True, null=True, default=True)
    questionDateTime = models.DateTimeField(default=timezone.now())
    enable = models.BooleanField(default=True)


class ConversationPrivateThread(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    message = models.CharField(max_length=250)
    messageDateTime = models.DateTimeField()
    enable = models.BooleanField(default=True)
