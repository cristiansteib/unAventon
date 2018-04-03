
from django.test import TestCase
from unAventonApp.models import Driver, Car, BankEntity, Creditcard, Profile, Trip, ConversationPublicThread, ConversationPrivateThread
from django.contrib.auth.models import User
from django.utils import timezone


# Create your tests here.
class ModelIntegrityTest(TestCase):

    def setUp(self):
        ''' crea el entorno necesario para poder ejecutar las pruebas'''
        self.user = User.objects.create_user('usuario', 'mail@alg.xom', 'clavesecreta')

        self.banco = BankEntity.objects.create(name="Santander Rio S.A.")
        self.perfil = Profile.objects.create(name='Mariano',
                                             lastName='Ferr',
                                             user=self.user,
                                             dni='33444555',
                                             birthdate='1992-10-06')
        self.driver = Driver.objects.create(profile=self.perfil)
        self.car = Car.objects.create(driver=self.driver,
                                      domain='FGW443',
                                      brand='ford',
                                      model='focus',
                                      year='2013',
                                      capacity='4')
        self.tarjeta1 = Creditcard.objects.create(profile=self.perfil,
                                                  entity=self.banco,
                                                  expirationDate='2020-2-2',
                                                  CVV='2222',
                                                  cardNumber='121254545')
        self.tarjeta2 = Creditcard.objects.create(profile=self.perfil,
                                                  entity=self.banco,
                                                  expirationDate='2021-2-2',
                                                  CVV='222',
                                                  cardNumber='1212545453')
        self.viaje = Trip.objects.create(driver=self.driver,
                                         car=self.car,
                                         creationDateTime=timezone.now,
                                         expirationDateTime=timezone.now() + timezone.timedelta(days=360),
                                         destinationLatitude='11',
                                         destinationLongitude='11',
                                         beginningLatitude='22',
                                         beginningLongitude='22')

    def test_borraPerfilySeBorranSusTarjeta(self):
        ''' Se borra un perfil, se tienen que borrar todas sus tarjetas '''
        self.perfil.delete()
        self.assertEqual(Creditcard.objects.filter(profile=self.perfil).count(), 0)

    def test_borraPerfilySeBorranSusViajes(self):
        self.perfil.delete()
        self.assertEqual(Trip.objects.filter(driver=self.driver).count(), 0)


class TestPasajeros(TestCase):

    def test_enUnSoloViajeConfirmado(self):
        ''' sdffsd '''
        pass

    def test_puedeCancelarSuscripcioDeViaje(self):
        pass

    def test_puedeSolicitarNViajes(self):
        pass

    def test_bajaLaReputacionAlCancelarElViajeConfirmado(self):
        pass

    def test_NoBajaLaReputacionAlCancelarElViajeConfirmado(self):
        pass

    def test_seLePuedeCobrar(self):
        pass

    def test_puedePreguntarEnCualquierViaje(self):
        pass


class TestConductor(TestCase):
    def test_soloUnViajeEnUnMismoMomento(self):
        pass

    def test_seLePuedeCobrar(self):
        pass

    def test_puedeResponderPreguntasDeSusViajes(self):
        pass

    def test_noPuedeResponderPreguntasDeOtrosViajes(self):
        pass

    def test_soloPuedeCalificarPasajerosDeSuViaje(self):
        pass

    def test_seAplicaLaCalificacionPositiva(self):
        pass

    def test_seAplicaCalificacionNegativa(self):
        pass

    def test_seAplicaCalificaionNeutra(self):
        pass


class TestViaje(TestCase):
    def test_listaVaiejsDisponibles(self):
        pass

    def test_buscarPorHoraDia(self):
        pass

    def test_buscarPorUbicacion(self):
        ''' tener en cuenta que la busqueda no deberia
        ser de coordenadas exxactas, sino establecer un rango minimo
        de cercania del origen y destino
        '''
        pass


class TestMensajeria(TestCase):

    def test_pasajeroPuedePreguntarEnCanalPublico(self):
        '''deberia poder consultar en cualquier viaje'''
        pass
