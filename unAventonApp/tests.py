from django.test import TestCase
from .models import Usuario, Auto, Viaje, CuentaBancaria, TipoViaje
from django.contrib.auth.models import User
from django.utils import timezone


# Create your tests here.
class unAventonTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'usuariotest0',
            password='passwordtest0'
        )
        self.usuario1 = Usuario.objects.create(
            user=self.user,
            nombre='Laura',
            apellido='LauraApellido',
            fechaDeNacimiento='1992-10-10',
            dni='20.200.200'
        )

    def tearDown(self):
        User.objects.all().delete()
        Usuario.objects.all().delete()

    def test_usuarioPuedeDarDeAltaUnAuto(self):
        self.auto = Auto.objects.create(
            usuario=self.usuario1,
            marca='Ford',
            modelo='Eco Sport',
            capacidad='5',
        )


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

    def cargarViaje(self, unVehiculo, unaCuentaBancaria):
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
        '''tiene CBU y vehiculo. y no tiene calificaciones pendientes'''

        unConductor = self.cargarUsuario()
        unConductorCualquiera = self.cargarUsuario()

        unCBU = self.cargarCuentaBancariaAUnUsuario(unConductor)
        unAuto = self.cargarVechiculoAUnPiloto(unConductor)

        print ('-------------------->' ,unCBU.usuario.all())
        print ('------------------>',unConductor)

        viaje = self.cargarViaje(unAuto,unCBU)


        print(viaje)
        print(viaje.get('error',None))



        # checkear que tenga vehiculo
        # checkear que tenga cbu
        # checkear que no tenga calif pendientes
        # checkear que no se solape con otro viaje


class TestCalificaciones(TestCase):
    '''para probar todo lo referido a calificaciones'''
    def setUp(self):
        pass
