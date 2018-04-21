from django.urls import path
from .views import (
    index,
    login,
    signIn,
    logout,
    signInRegister
)

from .ajax import (
    lista_de_espera_de_copilotos_para_un_viaje,
    mis_viajes_activos,
    lista_de_calificaciones_pendientes_a_copilotos
)

name = 'unAventonApp'

urlpatterns = [
    path('', index, name='index'),
    path('login', login, name='login'),
    path('signin', signIn, name='signin'),
    path('signinReg', signInRegister, name='signin_register'),
    path('logout', logout, name='logout'),

    path('ajax/copilotosEnEspera', lista_de_espera_de_copilotos_para_un_viaje, name='lista_espera'),
    path('ajax/misViajesActivos', mis_viajes_activos, name='viajes_activos'),
    path('ajax/califPendientesCopilotos', lista_de_calificaciones_pendientes_a_copilotos, name='lista_calificaciones_copilotos')

]
