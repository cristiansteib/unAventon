from django.test import TestCase, Client
from .models import Usuario, Auto, Viaje, CuentaBancaria, TipoViaje, ViajeCopiloto
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
        )

    def mock_cuentaBancaria(self, usuario):
        return CuentaBancaria.objects.create(
            usuario=usuario,
            cbu=self.randomize()
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
            gastoTotal=500,
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

        user_list = [mocker.mock_user() for n in range(0, 8)]

        self.conductor_1 = mocker.mock_usuario(user_list[0])
        self.conductor_2 = mocker.mock_usuario(user_list[1])
        self.copiloto_1 = mocker.mock_usuario(user_list[2])
        self.copiloto_2 = mocker.mock_usuario(user_list[3])
        self.copiloto_3 = mocker.mock_usuario(user_list[4])
        self.copiloto_4 = mocker.mock_usuario(user_list[5])
        self.copiloto_5 = mocker.mock_usuario(user_list[6])
        self.copiloto_6 = mocker.mock_usuario(user_list[7])

        self.cuenta_bancaria1 = mocker.mock_cuentaBancaria(self.conductor_1)
        self.cuenta_bancaria2 = mocker.mock_cuentaBancaria(self.conductor_2)
        self.auto1 = mocker.mock_auto(self.conductor_1)
        self.auto2 = mocker.mock_auto(self.conductor_2)

        self.tipo_viaje = mocker.mock_tipoViaje()
        self.v1 = mocker.mock_viaje(self.tipo_viaje, self.cuenta_bancaria1, self.auto1)
        self.v2 = mocker.mock_viaje(self.tipo_viaje, self.cuenta_bancaria2, self.auto2)

        self.viaje1 = Viaje.objects.get(id=self.v1['id'])
        self.viaje2 = Viaje.objects.get(id=self.v2['id'])

        mocker.mock_ViajeCopiloto(self.copiloto_1, self.viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_2, self.viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_3, self.viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_4, self.viaje1)
        mocker.mock_ViajeCopiloto(self.copiloto_1, self.viaje2)
        mocker.mock_ViajeCopiloto(self.copiloto_5, self.viaje2).confirmarCopiloto()

        self.copiloto_1.calificarPiloto(1, self.conductor_1, self.viaje1, 'todo bien')


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
            gastoTotal=1000,
            comentario='una mochila por pesona',
        )

        self.assertEqual(viaje['creado'], True, msg="No se pudo crear el viaje. {0}".format(viaje['error']))

class TestMetodosDeModels(BaseTest):


    def setUp(self):
        self.createSomeData()

    """
        mocker = MockModels()

        user_list = [mocker.mock_user() for n in range(0,8)]

        self.conductor_1 = mocker.mock_usuario(user_list[0])
        self.conductor_2 = mocker.mock_usuario(user_list[1])
        self.copiloto_1 = mocker.mock_usuario(user_list[2])
        self.copiloto_2 = mocker.mock_usuario(user_list[3])
        self.copiloto_3 = mocker.mock_usuario(user_list[4])
        self.copiloto_4 = mocker.mock_usuario(user_list[5])
        self.copiloto_5 = mocker.mock_usuario(user_list[6])
        self.copiloto_6 = mocker.mock_usuario(user_list[7])

        self.cuenta_bancaria1 = mocker.mock_cuentaBancaria(self.conductor_1)
        self.cuenta_bancaria2 = mocker.mock_cuentaBancaria(self.conductor_2)
        self.auto1 = mocker.mock_auto(self.conductor_1)
        self.auto2 = mocker.mock_auto(self.conductor_2)

        self.tipo_viaje = mocker.mock_tipoViaje()
        self.v1 = mocker.mock_viaje(self.tipo_viaje, self.cuenta_bancaria1, self.auto1)
        self.v2 = mocker.mock_viaje(self.tipo_viaje, self.cuenta_bancaria2, self.auto2)
    """

    def tearDown(self):
        User.objects.all().delete()
        Usuario.objects.all().delete()
        Auto.objects.all().delete()
        CuentaBancaria.objects.all().delete()
        Viaje.objects.all().delete()
        TipoViaje.objects.all().delete()
        ViajeCopiloto.objects.all().delete()

    def test_copiloto_confirmado_tiene_calificaciones_pendientes_para_el_piloto(self):
        self.assertEqual(len(self.conductor_1.calificacionesPendientesParaCopilotos().filter(usuario=self.copiloto_1)), 1)
        self.assertEqual(len(self.conductor_1.calificacionesPendientesParaCopilotos().filter(usuario=self.copiloto_2)), 1)
        self.assertEqual(len(self.conductor_1.calificacionesPendientesParaCopilotos().filter(usuario=self.copiloto_3)), 1)

    def test_copiloto_no_confirmado_no_tiene_calificaciones_pendientes_para_el_piloto(self):
        self.assertEqual(len(self.conductor_1.calificacionesPendientesParaCopilotos().filter(usuario=self.copiloto_4)),0)

    def test_copiloto_sin_viajes_no_tiene_calificaciones_pendientes_para_el_piloto(self):
        self.assertEqual(len(self.copiloto_6.calificacionesPendientesParaPiloto()), 0, msg='No deberia, si no tiene viajes!!')

    def test_viajesEnEsperaComoCopiloto(self):
        
        #viaje1 = Viaje.objects.get(id=self.v1['id'])
        #viaje2 = Viaje.objects.get(id=self.v2['id'])
        '''
        mocker = MockModels()
        mocker.mock_ViajeCopiloto(self.copiloto_1, viaje1)
        mocker.mock_ViajeCopiloto(self.copiloto_2, viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_3, viaje1).confirmarCopiloto()

        mocker.mock_ViajeCopiloto(self.copiloto_1, viaje2)
        mocker.mock_ViajeCopiloto(self.copiloto_5, viaje2).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_6, viaje2)
        '''
        
        self.assertEqual(self.copiloto_1.viajesEnEsperaComoCopiloto().count() == 2, True)
    """
    def test_viajesConfirmadosComoCopiloto(self):
        viaje1 = Viaje.objects.get(id=self.v1['id'])
        viaje2 = Viaje.objects.get(id=self.v2['id'])
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

    def test_esCopilotoEnViaje(self):
        '''
        anda bien, pero si no esta confirmado, deberia devolver True o no???
        '''
        viaje1 = Viaje.objects.get(id=self.v1['id'])
        viaje2 = Viaje.objects.get(id=self.v2['id'])
        '''
        mocker = MockModels()
        mocker.mock_ViajeCopiloto(self.copiloto_1, viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_2, viaje2)
        '''
        self.assertEqual(self.copiloto_2.esCopilotoEnViaje(viaje1), False)

    def test_esPilotoEnViaje(self):
        viaje1 = Viaje.objects.get(id=self.v1['id'])
        viaje2 = Viaje.objects.get(id=self.v2['id'])

        mocker = MockModels()
        mocker.mock_ViajeCopiloto(self.copiloto_1, viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_2, viaje2)

        self.assertEqual(self.conductor_1.esPilotoEnViaje(viaje1), True, 'No es conductor de ese viaje')

    def test_calificarCopiloto(self):

        viaje1 = Viaje.objects.get(id=self.v1['id'])
        viaje2 = Viaje.objects.get(id=self.v2['id'])

        mocker = MockModels()
        mocker.mock_ViajeCopiloto(self.copiloto_1, viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_4,viaje2).confirmarCopiloto()

        califCopiloto1 = self.conductor_1.calificarCopiloto(1, self.copiloto_1, viaje1, 'todo bien')
        self.assertEqual(califCopiloto1, True, msg='El copiloto a confirmar no pertenece a su viaje')
        califCopiloto2 = self.conductor_1.calificarCopiloto(1, self.copiloto_4,viaje2,'okok')
        self.assertEqual(califCopiloto2, False, msg='No deberia poder calificar a un copiloto que no es de mis viajes')

    def test_calificacionComoPiloto(self):
        viaje1 = Viaje.objects.get(id=self.v1['id'])

        mocker = MockModels()
        mocker.mock_ViajeCopiloto(self.copiloto_1, viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_2, viaje1)

        self.assertEqual(self.conductor_1.calificacionComoPiloto(),None,msg='Deberia ser None')
        self.copiloto_1.calificarPiloto(1,self.conductor_1,viaje1,'todo bien')
        self.assertEqual(self.conductor_1.calificacionComoPiloto(),1,msg='Deberia ser 1')

    def test_calificacionComoCopiloto(self):
        viaje1 = Viaje.objects.get(id=self.v1['id'])

        mocker = MockModels()
        mocker.mock_ViajeCopiloto(self.copiloto_1, viaje1).confirmarCopiloto()
        mocker.mock_ViajeCopiloto(self.copiloto_2, viaje1)

        self.assertEqual(self.copiloto_1.calificacionComoCopiloto(), None, msg='Deberia ser None')
        self.conductor_1.calificarCopiloto(0,self.copiloto_1,viaje1,'todo en orden')
        self.assertEqual(self.copiloto_1.calificacionComoCopiloto(),0,msg='Deberia ser 0')
    """
"""   
class TestAjax(BaseTest):


    def setUp(self):
        self.createSomeData()

    def test_lista_espera(self):


        mocker = MockModels()
        user = mocker.mock_user()

        c = Client()
        response1 = c.post('/login',{'email':user.username,'password':MockModels.password})
        print(response1.url)
        response1 = c.get('/ajax/copilotosEnEspera')
        print(response1.content)

    def tearDown(self):
        User.objects.all().delete()
        Usuario.objects.all().delete()

    def test_viajes_activos(self):
        pass

    def test_lista_calificaciones_copilotos(self):
        pass

    def test_lista_calificaciones_pilotos(self):
        pass

    def test_datos_del_usuario(self):
        pass
    '''
    'ajax/copilotosEnEspera'
    'ajax/misViajesActivos'
    'ajax/califPendientesCopilotos'    
    'ajax/califPendientesPilotos'
    'ajax/datosRelacionandosAlUsuario'
    
    '''
"""







class TestViews(TestCase):
    pass

