from django.urls import path, re_path
from .views import (
    viaje,
    index,
    login,
    signIn,
    logout as logout_view,
    signInRegister,
    viajes_inscriptos,
    buscar_viajes,
    mis_viajes,
    crear_viaje,
    mi_perfil,
    upload_foto,
    mis_viajes_finalizados,
    agregar_pregunta_conversacion_publica,
    ver_calificaciones,
    ver_calificaciones_de_usuario
)

from .ajax import *

name = 'unAventonApp'

urlpatterns = [
    path('', index, name='index'),
    path('login', login, name='login'),
    path('signin', signIn, name='signin'),
    path('signinReg', signInRegister, name='signin_register'),
    path('logout', logout_view, name='logout'),
    path('viajesInscriptos', viajes_inscriptos, name='viajes_inscriptos'),
    path('buscarViajes', buscar_viajes, name='buscar_viajes'),
    path('miPerfil', mi_perfil, name='miPerfil'),
    path('verCalificaciones', ver_calificaciones, name='ver_calificaciones'),
    re_path(r'^verCalificaciones/(?P<id>[0-9]+)/$', ver_calificaciones_de_usuario, name='ver_calificaciones_de_usuario'),
    re_path(r'^viaje/(?P<id>[0-9]+)/(?P<timestamp>[0-9]+)/$', viaje, name='viaje'),
    path('misViajes', mis_viajes, name='mis_viajes'),
    path('misViajesFinalizados', mis_viajes_finalizados, name='mis_viajes_finalizados'),
    path('crearViaje', crear_viaje, name='crear_viaje'),
    path('uploadFoto', upload_foto, name='upload_foto'),
    path('agregarPregPublica', agregar_pregunta_conversacion_publica, name='agregar_pregunta_conversacion_publica'),

    path('ajax/copilotosEnEspera', lista_de_espera_de_copilotos_para_un_viaje,
         name='lista_espera'),
    path('ajax/misViajesActivos', viajes_activos, name='viajes_activos'),
    path('ajax/califPendientesCopilotos', lista_de_calificaciones_pendientes_a_copilotos,
         name='lista_calificaciones_copilotos'),
    path('ajax/califPendientesPilotos', lista_de_calificaciones_pendientes_a_pilotos,
         name='lista_calificaciones_pilotos'),
    path('ajax/datosRelacionandosAlUsuario', datos_relacionados_al_usuario,
         name='datos_del_usuario'),
    path('ajax/crearViaje', crear_viaje_ajax,
         name='crear_viaje_ajax'),
    path('ajax/updateProfile', actualizar_datos_perfil, name='actualizar_perfil'),
    path('ajax/createCreditCard', crear_tarjeta, name='crear_tarjeta'),
    path('ajax/createBankAccount', crear_cuenta_bancaria, name='crear_cuenta_bancaria'),
    path('ajax/updateCreditCard', actualizar_tarjeta, name='actualizar_tarjeta'),
    path('ajax/updateBankAccount', actualizar_cuenta_bancaria, name='actualizar_cuenta_bancaria'),
    path('ajax/createCar', crear_auto, name='crear_auto'),
    path('ajax/updateCar', actualizar_auto, name='actualizar_auto'),
    path('ajax/deleteCar', borrar_auto, name='borrar_auto'),
    path('ajax/deleteBankAccount', borrar_cuenta_bancaria, name='borrar_cuenta_bancaria'),
    path('ajax/deleteCreditCard', borrar_tarjeta, name='borrar_tarjeta'),

    path('ajax/getListaCalificacionesPendientesCopilotos', lista_de_calificaciones_pendientes_a_copilotos,
         name='calificaciones_pendients_cop'),
    path('ajax/getListaCalificacionesPendientesPilotos', lista_de_calificaciones_pendientes_a_pilotos,
         name='calificaciones_pendients_pi'),
    path('ajax/getListaCopilotosConfirmados', lista_de_copilotos_confirmados, name='copilotos_confirmados'),
    path('ajax/getListaCopilotosEnEspera', lista_de_copitolos_en_espera, name='copilotos_en_espera'),

    path('ajax/solicitarIrEnViaje', solicitar_ir_en_viaje, name='solicitar_ir_a_viaje'),
    path('ajax/cancelarIrEnViaje', cancelar_ir_en_viaje, name='cancelar_ir_a_viaje'),

    path('ajax/confirmarCopiloto', confirmar_copiloto, name='confirmar_copiloto'),
    path('ajax/rechazarCopiloto', rechazar_copiloto, name='rechazar_copiloto'),
    path('ajax/cancelarCopiloto', cancelar_copiloto, name='cancelar_copiloto'),

    path('ajax/eliminarViaje', elimiar_viaje, name='eliminar_viaje'),
    path('ajax/viajeDatos', datos_del_viaje, name='datos_viaje'),
    path('ajax/buscarViaje', buscar_viajes_ajax, name='buscar_viaje_ajax'),

    path('ajax/calificarCopiloto', calificar_copiloto, name='calificar_a_copiloto'),
    path('ajax/calificarPiloto', calificar_piloto, name='calificar_a_piloto'),
    path('ajax/calificacionCopiloto', ver_calificacion_de_copiloto, name='ver_calificacion_a_copiloto'),
    path('ajax/calificacionPiloto', ver_calificacion_de_piloto, name='ver_calificacion_a_piloto'),

]
