from unAventonApp.modules.Git import Git
from django.conf import settings
from django import template
from unAventonApp.models import Usuario, ViajeCopiloto
from django.utils import timezone
register = template.Library()


@register.filter(is_safe=True)
def currentbranch(value):
    return (Git(settings.BASE_DIR).getActuallBranch())


@register.filter(is_safe=True)
def currentuser(value):
    usuario = Usuario.objects.get(user=value)
    return "{0} {1}".format(usuario.nombre, usuario.apellido)


@register.filter(is_safe=True)
def lastupdate(value):
    return Git(settings.BASE_DIR).git('log', '-1', '--pretty=format:Last commit %ar')


@register.filter(is_safe=True)
def foto_de_perfil(usuarioId):
    usuario = Usuario.objects.get(pk=usuarioId)
    return str(usuario.foto_de_perfil.url)


def getEstado(viajeCopiloto):
    estados = ("esperando", "confirmado", "rechazado", "finalizado")
    if viajeCopiloto.estaConfirmado == None:
        return estados[0]
    if viajeCopiloto.estaConfirmado == False:
        return estados[2]
    if (viajeCopiloto.fecha_del_viaje < timezone.now()) and (viajeCopiloto.estaConfirmado == True):
        return estados[3]
    if viajeCopiloto.estaConfirmado == True:
        return estados[1]


@register.filter(is_safe=True)
def estadoCopilotoViaje(viajeCopilotoId):
    viajeCopiloto = ViajeCopiloto.objects.get(pk=viajeCopilotoId)
    return viajeCopiloto.get_estado().capitalize()


@register.filter(is_safe=True)
def estadoCopilotoViajeClass(viajeCopilotoId):
    viajeCopiloto = ViajeCopiloto.objects.get(pk=viajeCopilotoId)
    estado = viajeCopiloto.get_estado()
    clase = "table"
    if estado == "esperando":
        clase = "table-warning"

    if estado == "confirmado":
        clase = "table-success"

    if estado == "rechazado":
        clase = "table-danger"

    if estado == "finalizado":
        clase = "table-info"
    return clase


@register.filter(is_safe=True)
def copilotoViajeCalificarPiloto(viajeCopilotoId):
    # el estado del viaje tiene que estar finalizado para poder calificar al piloto
    viajeCopiloto = ViajeCopiloto.objects.get(pk=viajeCopilotoId)
    estado = viajeCopiloto.get_estado()
    if estado == "finalizado" and viajeCopiloto.estaConfirmado and viajeCopiloto.calificacion_a_piloto is None:
        return "<button class='btn btn-default' onclick=calificarPiloto({0})>Calificar</button>".format(viajeCopilotoId)
    if estado == "finalizado" and viajeCopiloto.estaConfirmado and viajeCopiloto.calificacion_a_piloto is not None:
        return "<button class='btn btn-default' onclick=verCalificacionDadaAPiloto({0})>Ver calificacion</button>".format(viajeCopilotoId)
    return "<button class='btn btn-default' disabled>Calificar</button>"



@register.filter(is_safe=True)
def copilotoCancelarInscripcion(viajeCopilotoId):
    # el estado del viaje tiene que estar finalizado para poder calificar al piloto
    viajeCopiloto = ViajeCopiloto.objects.get(pk=viajeCopilotoId)
    estado = viajeCopiloto.get_estado()
    if estado != "finalizado" and viajeCopiloto.estaConfirmado is None:
        return "<button class='btn btn-danger' onclick=cancelarInscripcion({0})>Cancelar inscripcion</button>".format(
            viajeCopilotoId)
    return "<button class='btn btn-default' disabled>Cancelar inscripcion</button>"
