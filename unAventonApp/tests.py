from django.test import TestCase
from unAventonApp.models import Usuario, Auto
from django.contrib.auth.models import User
from django.utils import timezone


# Create your tests here.
class unAventonTest(TestCase):

    def setUp(self):
        user = User.objects.create_user(
                'usuariotest',
                password='passwordtest'
            )
        self.usuario = Usuario.objects.create(
            user=user,
            nombre='Pepe',
            apellido='PepeApellido',
            fechaDeNacimiento='1992-10-10',
            dni='20.200.200'
        )



    def tearDown(self):
        User.objects.all().delete()
        Usuario.objects.all().delete()


    def test_usuarioPuedeDarDeAltaUnAuto(self):
        auto = Auto.objects.create(
            usuario=self.usuario,
            marca='Ford',
            modelo='Eco Sport',
            capacidad='5',
        )



class unAventonTestViajes(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            'usuariotest',
            password='passwordtest'
        )
        self.usuario = Usuario.objects.create(
            user=user,
            nombre='Pepe',
            apellido='PepeApellido',
            fechaDeNacimiento='1992-10-10',
            dni='20.200.200'
        )
        self.auto = Auto.objects.create(
            usuario=self.usuario,
            marca='Ford',
            modelo='Eco Sport',
            capacidad='5',
        )


    def tearDown(self):
        User.objects.all().delete()
        Usuario.objects.all().delete()
        Auto.objects.all().delete()


    def test_usuarioPuedeDarDeAltaUnViajeTeniendoAutoYCuentaBancaria(self):
        pass
