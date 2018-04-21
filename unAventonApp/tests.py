from django.test import TestCase
from .models import Usuario, Auto, Viaje, CuentaBancaria, TipoViaje, ViajeCopiloto
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
import pytz
import random


class MockModels():

    @staticmethod
    def randomize():
        return str(random.randrange(100000, 990000))

    def mock_user(self):
        return User.objects.create_user(
            username=self.randomize(),
            password='passwordtest0'
        )

    def mock_usuario(self, user):
        return Usuario.objects.create(
            user=user,
            nombre='Pepe',
            apellido='Pepa',
            fechaDeNacimiento='1992-10-10',
            dni='20.200.200'
        )

    def mock_auto(self, usuario, marca='Ford', modelo='Eco Sport', capacidad=5):
        return Auto.objects.create(
            usuario=usuario,
            marca=marca,
            modelo=modelo,
            capacidad=capacidad,
        )

    def mock_cuentaBancaria(self, usuario):
        return CuentaBancaria.objects.create(
            usuario=usuario,
            cbu=self.randomize()
        )


class unAventonTest(TestCase):

    def setUp(self):
        self.tipo_viaje = TipoViaje.objects.create(
            tipo="larga distancia",
            descripcion="algun descripcion"
        )
        mocker = MockModels()
        user1 = mocker.mock_user()
        self.usuario = mocker.mock_usuario(user1)
        self.cuenta_bancaria = mocker.mock_cuentaBancaria(self.usuario)
        self.auto = mocker.mock_auto(self.usuario)

    def tearDown(self):
        User.objects.all().delete()
        Usuario.objects.all().delete()

    def test_usuarioPuedeDarDeAltaUnViaje(self):
        viaje = Viaje.objects.create_viaje(
            origen='La plata',
            destino='BsAs',
            tipoViaje=self.tipo_viaje,
            duracion=2,
            fechaHoraSalida=datetime.datetime(2099, 11, 20, 20, 8, 7, 127325, tzinfo=pytz.UTC),
            cuentaBancaria=self.cuenta_bancaria,
            auto=self.auto,
            gastoTotal=1000,
            comentario='una mochila por pesona',
        )

        self.assertEqual(viaje['creado'], True, msg="No se pudo crear el viaje. {0}".format(viaje['error']))


"""
class unAventonTestViajes(TestCase):

    def setUp(self):
        pass

    def tearDown(self):

        User.objects.all().delete()
        Usuario.objects.all().delete()
        Auto.objects.all().delete()
        CuentaBancaria.objects.all().delete()
        Viaje.objects.all().delete()
        TipoViaje.objects.all().delete()

    def cargarVechiculoAUnPiloto(self, piloto):
        auto = Auto.objects.create(
            usuario=piloto,
            marca='Ford',
            modelo='Eco Sport',
            capacidad='5',
        )
        auto.save()
        return auto

    def cargarCuentaBancariaAUnUsuario(self, unUsuario):
        unaCuentaBancaria = CuentaBancaria.objects.create(
            cbu='123123123123123',
        )
        unaCuentaBancaria.usuario.add(unUsuario)
        #unaCuentaBancaria.save()
        return unaCuentaBancaria

    def mockViaje(self, unVehiculo, unaCuentaBancaria):
        tipoViaje = TipoViaje.objects.create(
            tipo='corta distancia',
        )

        viaje = Viaje.objects.create_viaje(
            origen='La plata',
            destino='BsAs',
            tipoViaje=tipoViaje,
            duracion=2,
            fechaHoraSalida='2012-12-12 10:00',
            cuentaBancaria=unaCuentaBancaria,
            auto=unVehiculo,
            gastoTotal=1000,
            comentario='una mochila por pesona',
        )
        return viaje

    def mockUsuario(self):
        import random
        user = User.objects.create_user(
            username=str(random.randrange(1000,99000)),
            password='passwordtest0'
        )
        conductor = Usuario.objects.create(
            user=user,
            nombre='Laura',
            apellido='LauraApellido',
            fechaDeNacimiento='1992-10-10',
            dni='20.200.200'
        )
        return conductor


    def test_usuarioPuedeDarDeAltaUnViajeTeniendoAutoYCuentaBancaria(self):
        '''tiene CBU y vehiculo.'''

        unConductor = self.mockUsuario()
        #otroConductor = self.mockUsuario()

        unCBU = self.cargarCuentaBancariaAUnUsuario(unConductor)
        unAuto = self.cargarVechiculoAUnPiloto(unConductor)

        viaje = self.mockViaje(unAuto,unCBU)
        self.assertTrue(viaje['creado'],True)


        # checkear que tenga vehiculo
        # checkear que tenga cbu
        # checkear que no tenga calif pendientes
        # checkear que no se solape con otro viaje


class TestCalificaciones(TestCase):
    '''para probar todo lo referido a calificaciones, no pruebo nada de pagos'''
    def setUp(self):
        pass

    def tearDown(self):

        User.objects.all().delete()
        Usuario.objects.all().delete()
        Auto.objects.all().delete()
        CuentaBancaria.objects.all().delete()
        Viaje.objects.all().delete()
        TipoViaje.objects.all().delete()
        ViajeCopiloto.objects.all().delete()

    def cargarCuentaBancariaAUnUsuario(self, conductor):
        unaCuentaBancaria = CuentaBancaria.objects.create(
            cbu=str(random.randrange(100000,500000)),
        )
        unaCuentaBancaria.usuario.add(conductor)
        #unaCuentaBancaria.save()
        return unaCuentaBancaria

    def mockUsuario(self):
        user = User.objects.create_user(
            username=str(random.randrange(1000, 99000)),
            password='passwordtest0'
        )
        usuario = Usuario.objects.create(
            user=user,
            nombre='Laura',
            apellido='LauraApellido',
            fechaDeNacimiento='1992-10-10',
            dni='20.200.200'
        )
        return usuario

    def mockViaje(self, unVehiculo, unaCuentaBancaria):
        tipoViaje = TipoViaje.objects.create(
            tipo='corta distancia',
        )

        viaje = Viaje.objects.create_viaje(
            origen='La plata',
            destino='BsAs',
            tipoViaje=tipoViaje,
            duracion=2,
            fechaHoraSalida='2012-12-12 10:00',
            cuentaBancaria=unaCuentaBancaria,
            auto=unVehiculo,
            gastoTotal=1000,
            comentario='una mochila por pesona',
        )
        return viaje

    def crearViaje(self, auto, cbu):
        tipoViaje = TipoViaje.objects.create(
            tipo='corta distancia',
        )

        v = Viaje(
            origen='La plata',
            destino='BsAs',
            tipoViaje=tipoViaje,
            duracion=2,
            fechaHoraSalida='2012-12-12 10:00',
            cuentaBancaria=cbu,
            auto=auto,
            gastoTotal=1000,
            comentario='una mochila por pesona',
        )
        return v

    def cargarVechiculoAUnPiloto(self, piloto):
        auto = Auto.objects.create(
            usuario=piloto,
            marca='Ford',
            modelo='Eco Sport',
            capacidad='5',
        )
        auto.save()
        return auto

    def cargarCopilotoEnViaje(self,copiloto,viaje):
        copi = ViajeCopiloto.objects.create(
            usuario=copiloto,
            viaje=viaje,
            #estaConfirmado=True,
            fechaHoraDeSolicitud=timezone.now(),    #porque no lo crea solo??
        )
        copi.confirmarCopiloto()
        return copi

    def test_conductorNoPuedeCrearViajeSiTieneCalificacionesPendientes(self):


        #viaje anterior del cual quedan calificaciones pendientes
        conductor_1 = self.mockUsuario()
        copiloto_1 = self.mockUsuario()
        copiloto_2 = self.mockUsuario()
        copiloto_3 = self.mockUsuario()
        copiloto_4 = self.mockUsuario()
        auto1 = self.cargarVechiculoAUnPiloto(conductor_1)
        cbu1 = self.cargarCuentaBancariaAUnUsuario(conductor_1)
        v1 = self.mockViaje(auto1, cbu1)
        viaje1 = Viaje.objects.get(id=v1[id])

        self.cargarCopilotoEnViaje(copiloto_1, viaje1)
        self.cargarCopilotoEnViaje(copiloto_2, viaje1)
        self.cargarCopilotoEnViaje(copiloto_3, viaje1)
        self.cargarCopilotoEnViaje(copiloto_4, viaje1)


        print ('###############  datos cargados viaje 1')

        conductor_2 = self.mockUsuario()
        copiloto_5 = self.mockUsuario()
        copiloto_6 = self.mockUsuario()
        auto2 = self.cargarVechiculoAUnPiloto(conductor_2)
        cbu2 = self.cargarCuentaBancariaAUnUsuario(conductor_2)
        v2 = self.mockViaje(auto2, cbu2)
        viaje2 = Viaje.objects.get(id=v2[id])

        self.cargarCopilotoEnViaje(copiloto_5, viaje2)
        self.cargarCopilotoEnViaje(copiloto_6, viaje2)

        print('###############  datos cargados viaje 2')



        print ('calif pendientes', conductor_1.calificacionesPendientesParaCopilotos().count())
        #print (copiloto_1.esCopilotoEnViaje(viaje1))



        conductor_1.calificarCopiloto(1,copiloto_1,viaje1,'masteeeeer')

        print(conductor_1.calificacionesPendientesParaCopilotos().count())







"""
