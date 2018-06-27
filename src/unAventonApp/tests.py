from django.test import TestCase, Client
from .models import Usuario, Auto, Viaje, CuentaBancaria, ViajeCopiloto, Tarjeta
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
import pytz
import random


class AppTest(TestCase):

    def setUp(self):
        user = User.objects.create_user('usuario1', 'usario@mail', 'password')

        self.usuario = Usuario.objects.create(
            user=user,
            nombre='Cristian',
            fechaDeNacimiento=timezone.datetime(day=10, month=6, year=1992),
            apellido='Steib',
            dni='36698267')

        self.auto = Auto.objects.create(
            dominio='HUH 588',
            marca='Ford',
            modelo='Ka',
            capacidad=5,
            usuario=self.usuario)

        self.cuenta_bancaria = CuentaBancaria.objects.create(
            usuario=self.usuario,
            cbu='123423r34t654643',
            entidad='Santander Rio'
        )

    def tearDown(self):
        self.usuario.delete()
        self.auto.delete()
        self.cuenta_bancaria.delete()

    def test_Si_usuario_puede_crear_viaje_teniendo_cuenta_bancaria_y_un_auto(self):
        fecha_y_hora_de_salida = datetime.datetime.now() + datetime.timedelta(days=5)

        datos_viaje = {
            'comentario': '',
            'fecha_hora_salida': timezone.datetime.fromtimestamp(fecha_y_hora_de_salida.timestamp()),
            'duracion': 1,
            'origen': 'La Plata',
            'gasto_total': 1000,
            'destino': 'Tandil',
            'auto_id': self.auto.id,
            'cuenta_bancaria_id': self.cuenta_bancaria.id,
            'se_repite': ('nunca', -1)
        }

        self.viaje = Viaje.objects.create_viaje(self.usuario, **datos_viaje)
        self.assertEqual(self.viaje['creado'], True, 'No se pudo crear el viaje')

    def test_Si_usuario_puede_crear_viaje_teniendo_viaje_semanal_sin_tener_en_el_mismo_dia(self):
        fecha_y_hora_de_salida = datetime.datetime.now() + datetime.timedelta(days=5)

        datos_viaje = {
            'comentario': '',
            'fecha_hora_salida': timezone.datetime.fromtimestamp(fecha_y_hora_de_salida.timestamp()),
            'duracion': 1,
            'origen': 'La Plata',
            'gasto_total': 1000,
            'destino': 'Tandil',
            'auto_id': self.auto.id,
            'cuenta_bancaria_id': self.cuenta_bancaria.id,
            'se_repite': ('semanal', -1)
        }

        self.viaje = Viaje.objects.create_viaje(self.usuario, **datos_viaje)
        self.assertEqual(self.viaje['creado'], True, 'No se pudo crear el viaje semanal')

    def test_Si_usuario_puede_crear_viaje_una_semana_antes_teniendo_viaje_semanal_en_el_mismo_dia_de_semana_que_ya_tiene_al_mismo_horario(
            self):
        fecha_y_hora_de_salida = datetime.datetime.now() + datetime.timedelta(days=5)

        datos_viaje = {
            'comentario': '',
            'fecha_hora_salida': timezone.datetime.fromtimestamp(fecha_y_hora_de_salida.timestamp()),
            'duracion': 1,
            'origen': 'La Plata',
            'gasto_total': 1000,
            'destino': 'Tandil',
            'auto_id': self.auto.id,
            'cuenta_bancaria_id': self.cuenta_bancaria.id,
            'se_repite': ('semanal', fecha_y_hora_de_salida.weekday())
        }

        viaje = Viaje.objects.create_viaje(self.usuario, **datos_viaje)
        self.assertEqual(viaje['creado'], True, 'No se pudo crear el viaje semanal')

        # ahora cambio la fecha para el mismo dia de la semana
        datos_viaje['fecha_hora_salida'] = fecha_y_hora_de_salida + datetime.timedelta(days=7)
        viaje = Viaje.objects.create_viaje(self.usuario, **datos_viaje)
        self.assertEqual(viaje['creado'], False, 'Se pudo crear el viaje semanal y no deberia, '
                                                 'ya tiene uno para el mismo dia de la semana,'
                                                 ' una semana atras. ' + str(viaje))

    def test_Si_usuario_NO_puede_crear_viaje_teniendo_viaje_semanal_en_el_mismo_dia_de_semana_que_ya_tiene_al_mismo_horario(
            self):
        fecha_y_hora_de_salida = datetime.datetime.now() + datetime.timedelta(days=30)

        datos_viaje = {
            'comentario': '',
            'fecha_hora_salida': timezone.datetime.fromtimestamp(fecha_y_hora_de_salida.timestamp()),
            'duracion': 1,
            'origen': 'La Plata',
            'gasto_total': 1000,
            'destino': 'Tandil',
            'auto_id': self.auto.id,
            'cuenta_bancaria_id': self.cuenta_bancaria.id,
            'se_repite': ('semanal', fecha_y_hora_de_salida.weekday())
        }

        viaje = Viaje.objects.create_viaje(self.usuario, **datos_viaje)
        self.assertEqual(viaje['creado'], True, 'No se pudo crear el viaje semanal')

        # ahora cambio la fecha para el mismo dia de la semana
        datos_viaje['fecha_hora_salida'] = fecha_y_hora_de_salida + datetime.timedelta(days=-7)
        viaje = Viaje.objects.create_viaje(self.usuario, **datos_viaje)
        self.assertEqual(viaje['creado'], True, 'NO Se pudo crear el viaje semanal deberia' + str(viaje))
