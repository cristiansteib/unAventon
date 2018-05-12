from django.test import TestCase, Client
from .models import Usuario, Auto, Viaje, CuentaBancaria, TipoViaje, ViajeCopiloto, Tarjeta
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
import pytz
import random


class MockModels():
    password = 'passwordtest0'

    @staticmethod
    def randomize():
        return str(random.randrange(100000, 990000))

    def mock_user(self):
        return User.objects.create_user(
            username=self.randomize(),
            password=self.password
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
            dominio=self.randomize(),
        )

    def mock_cuentaBancaria(self, usuario):
        return CuentaBancaria.objects.create(
            usuario=usuario,
            cbu=self.randomize()
        )

    def mock_tarjeta(self):
        return Tarjeta.objects.create(
            numero=self.randomize(),
            fechaDeVencimiento=datetime.datetime(2099, 11, 20, 20, 8, 7, 127325,tzinfo=pytz.UTC),
            ccv=self.randomize(),
        )

    def mock_tipoViaje(self):
        return TipoViaje.objects.create(
            tipo="larga distancia",
            descripcion="alguna descripcion"
        )

    def mock_viaje(self, tipo, cbu, auto):
        return Viaje.objects.create_viaje(
            origen='La plata',
            destino='BsAs',
            tipoViaje=tipo,
            duracion=2,
            fechaHoraSalida=datetime.datetime(2099, 11, 20, 20, 8, 7, 127325, tzinfo=pytz.UTC),
            cuentaBancaria=cbu,
            auto=auto,
            gasto_total=500,
            comentario='una mochila por pesona',
        )

    def mock_ViajeCopiloto(self, copiloto, viaje):
        return ViajeCopiloto.objects.create(
            usuario=copiloto,
            viaje=viaje,
            fechaHoraDeSolicitud=timezone.now()
        )


class  BaseTest(TestCase):

    def createSomeData(self):
        mocker = MockModels()

        user_list = [mocker.mock_user() for n in range(0, 9)]

        self.conductor_1 = mocker.mock_usuario(user_list[0])
        self.conductor_2 = mocker.mock_usuario(user_list[1])
        self.copiloto_1 = mocker.mock_usuario(user_list[2])
        self.copiloto_2 = mocker.mock_usuario(user_list[3])
        self.copiloto_3 = mocker.mock_usuario(user_list[4])
        self.copiloto_4 = mocker.mock_usuario(user_list[5])
        self.copiloto_5 = mocker.mock_usuario(user_list[6])
        self.copiloto_6 = mocker.mock_usuario(user_list[7])
        self.conductor_3 = mocker.mock_usuario((user_list[8]))

        self.cuenta_bancaria1 = mocker.mock_cuentaBancaria(self.conductor_1)
        self.cuenta_bancaria2 = mocker.mock_cuentaBancaria(self.conductor_2)
        self.cuenta_bancaria3 = mocker.mock_cuentaBancaria(self.conductor_3)

        self.auto1 = mocker.mock_auto(self.conductor_1)
        self.auto2 = mocker.mock_auto(self.conductor_2)
        self.auto3 = mocker.mock_auto(self.conductor_2)

        self.tipo_viaje = mocker.mock_tipoViaje()
        self.v1 = mocker.mock_viaje(self.tipo_viaje, self.cuenta_bancaria1, self.auto1)
        self.v2 = mocker.mock_viaje(self.tipo_viaje, self.cuenta_bancaria2, self.auto2)
        self.v3 = mocker.mock_viaje(self.tipo_viaje, self.cuenta_bancaria2, self.auto3)

        self.viaje1 = Viaje.objects.get(id=self.v1['id'])
        self.viaje2 = Viaje.objects.get(id=self.v2['id'])
        self.viaje3 = Viaje.objects.get(id=self.v3['id'])

        self.tarjeta1 = mocker.mock_tarjeta()
        self.tarjeta1.usuario.add(self.conductor_1)
        self.tarjeta1.usuario.add(self.conductor_2)


        mocker.mock_ViajeCopiloto(self.copiloto_1, self.viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_2, self.viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_3, self.viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_4, self.viaje1)
        mocker.mock_ViajeCopiloto(self.copiloto_5, self.viaje1)

        mocker.mock_ViajeCopiloto(self.copiloto_1, self.viaje2)
        mocker.mock_ViajeCopiloto(self.copiloto_5, self.viaje2).confirmarCopiloto()

        mocker.mock_ViajeCopiloto(self.copiloto_2, self.viaje3).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.conductor_1, self.viaje3).confirmarCopiloto()

        self.copiloto_1.calificarPiloto(1, self.conductor_1, self.viaje1, 'todo bien')
        self.conductor_1.calificarCopiloto(1, self.copiloto_1, self.viaje1, 'genial')




class unAventonTest(TestCase):

    def setUp(self):
        mocker = MockModels()
        self.tipo_viaje = mocker.mock_tipoViaje()
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
            gasto_total=1000,
            comentario='una mochila por pesona',
        )

        self.assertEqual(viaje['creado'], True, msg="No se pudo crear el viaje. {0}".format(viaje['error']))


class TestMetodosDeModels(BaseTest):

    def setUp(self):
        self.createSomeData()

    def tearDown(self):
        User.objects.all().delete()
        Usuario.objects.all().delete()
        Auto.objects.all().delete()
        CuentaBancaria.objects.all().delete()
        Viaje.objects.all().delete()
        TipoViaje.objects.all().delete()
        ViajeCopiloto.objects.all().delete()

    def test_copiloto_confirmado_tiene_calificaciones_pendientes_para_el_piloto(self):
        self.assertEqual(len(self.copiloto_2.calificacionesPendientesParaPiloto()), 2,
                         msg='error, el copiloto_2 aun no confirmo al conductor_1 por el viaje 1 ni al conductor_2 por el viaje 3')


    def test_copiloto_no_confirmado_no_tiene_calificaciones_pendientes_para_el_piloto(self):
        self.assertEqual(len(self.copiloto_4.calificacionesPendientesParaPiloto()),0)

    def test_copiloto_sin_viajes_no_tiene_calificaciones_pendientes_para_el_piloto(self):
        self.assertEqual(len(self.copiloto_6.calificacionesPendientesParaPiloto()), 0, msg='No deberia, si no tiene viajes!!')

    def test_piloto_tiene_calificaciones_pendientes_para_copilotos_de_su_viaje(self):
        self.assertEqual(len(self.conductor_1.calificacionesPendientesParaCopilotos()),2,msg='error, aun debe calificar a copiloto_2 y copiloto_3')

    def test_viajes_en_espera_como_copiloto(self):

        self.assertEqual(self.copiloto_1.viajesEnEsperaComoCopiloto().count() == 1, True)

    def test_viajes_confirmados_como_copiloto(self):
        '''
        mocker = MockModels()
        mocker.mock_ViajeCopiloto(self.copiloto_1, viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_2, viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_4, viaje1)

        mocker.mock_ViajeCopiloto(self.copiloto_1, viaje2)
        mocker.mock_ViajeCopiloto(self.copiloto_5, viaje2).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_6, viaje2)
        '''
        self.assertEqual(self.copiloto_1.viajesConfirmadosComoCopiloto().count() == 1, True)

    def test_un_usuario_es_copiloto_en_un_viaje_dado(self):
        '''
        mocker = MockModels()
        mocker.mock_ViajeCopiloto(self.copiloto_1, viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_2, viaje2)
        '''
        self.assertEqual(self.copiloto_2.esCopilotoEnViaje(self.viaje1), True)

    def test_un_usuario_no_es_copiloto_en_un_viaje_dado(self):
        self.assertEqual(self.copiloto_6.esCopilotoEnViaje(self.viaje1), False, msg='no deberia ser copiloto de ese viaje')

    def test_un_usuario_es_piloto_en_un_viaje_dado(self):

        '''
        mocker = MockModels()
        mocker.mock_ViajeCopiloto(self.copiloto_1, viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_2, viaje2)
        '''
        self.assertEqual(self.conductor_1.esPilotoEnViaje(self.viaje1), True, 'No es conductor de ese viaje')

    def test_un_usuario_no_es_piloto_en_un_viaje_dado(self):
        self.assertEqual(self.conductor_2.esPilotoEnViaje(self.viaje1),False, 'No es conductor de ese viaje')

    def test_conductor_califica_copiloto_de_su_viaje(self):
        '''
        mocker = MockModels()
        mocker.mock_ViajeCopiloto(self.copiloto_1, viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_4,viaje2).confirmarCopiloto()
        '''
        self.assertEqual(self.copiloto_1.calificacionComoCopiloto(), 1, msg='El copiloto no pertenece a su viaje')
    
    def test_conductor_califica_copiloto_de_un_viaje_que_no_es_suyo(self):
        self.conductor_1.calificarCopiloto(1,self.copiloto_5,self.viaje2,'se re cagaba')
        self.assertEqual(self.copiloto_5.calificacionComoCopiloto(), None, msg='No deberia tener calificaiones porque lo califico un conductor de un viaje distinto')
    
    def test_conductor_calificado_como_piloto_con_calificacion_previa(self):

        self.assertEqual(self.conductor_1.calificacionComoPiloto(),1,msg='Lo califico solo 1 usuario, debe ser 1')

    def test_conductor_sin_calificar_como_piloto(self):

        self.assertEqual(self.conductor_2.calificacionComoPiloto(),None,msg='Deberia ser None, nadie lo califico como piloto aun')

    def test_pasajero_calificado_como_copiloto(self):
    
        self.assertEqual(self.copiloto_1.calificacionComoCopiloto(), 1, msg='Deberia ser 1, solo lo califiacron una vez')

    def test_pasajero_sin_calificar_como_copiloto(self):
        self.assertEqual(self.copiloto_4.calificacionComoCopiloto(), None, msg='Deberia ser None, nadie lo califico')

    def test_cantidad_de_tarjetas_de_un_usuario(self):
        self.assertEqual(len(self.conductor_1.tarjetas_de_credito())==1,True,msg='deberia tener solo 1 tarjeta asociada')

    def test_cantidad_de_usuarios_que_comparten_misma_tarjeta(self):

        self.assertEqual(len(self.tarjeta1.usuario.all())==2,True,msg='2 usuario comparten la misma tarjeta, conductor1 y conductor 2')

class TestAjax(BaseTest):

    def setUp(self):
        self.createSomeData()
        self.client = Client()
        #para simular que esta logueado, muchas vistas lo requieren
        self.client.post('/login', {'email': self.conductor_1.user.username, 'password': MockModels.password})

    def tearDown(self):
        User.objects.all().delete()
        Usuario.objects.all().delete()
        Viaje.objects.all().delete()

    def getJson(self, url, data ):
        response = self.client.get(url,data)
        return response.json()

    def test_lista_de_espera_de_copilotos_para_un_viaje_dado(self):
        data = self.getJson('/ajax/copilotosEnEspera',{'viajeId':self.viaje1.id})
        self.assertEqual((
            (data['lista'][0]['usuario']['id']) == (self.copiloto_4.id))
            and
            ((data['lista'][1]['usuario']['id']) == (self.copiloto_5.id)),
            True,
            msg='Solo deberia haber 2 copilotos en espera, copiloto_4 y copiloto_5')

    def test_lista_de_espera_de_copilotos_para_un_viaje_inexistente(self):
        data = self.getJson('/ajax/copilotosEnEspera',{'viajeId': '-2'})
        self.assertEqual('error' in data,True)

    def test_lista_de_espera_de_copilotos_sin_parametros(self):
        data = self.getJson('/ajax/copilotosEnEspera',{'viajeId': ''})
        self.assertEqual('error' in data, True)

    def test_viajes_activos(self):
        #para el usuario logueado
        data = self.getJson('/ajax/misViajesActivos',{})
        self.assertEqual(len(data['viajes'])==1,True,msg='solo tiene UN viaje activo')

    def test_lista_de_calificaciones_pendientes_a_copilotos(self):
        pass
        #data = self.getJson('ajax/califPendientesCopilotos', {})
        pass

    def test_lista_de_calificaciones_a_pilotos(self):
        #data = self.getJson('ajax/califPendientesPilotos', {})
        pass

    def test_datos_relacionados_al_usuario_logueado(self):
        #data = self.getJson('ajax/datosRelacionandosAlUsuario', {})
        pass

    'ajax/copilotosEnEspera'
    'ajax/misViajesActivos'
    'ajax/califPendientesCopilotos'    
    'ajax/califPendientesPilotos'
    'ajax/datosRelacionandosAlUsuario'
    

class TestViews(TestCase):
    pass
