from unAventonApp.modules.Git import Git
from django.conf import settings
from django import template
from unAventonApp.models import Usuario, ViajeCopiloto
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
    return estados[1]


@register.filter(is_safe=True)
def estadoCopilotoViaje(viajeCopilotoId):
    viajeCopiloto = ViajeCopiloto.objects.get(pk=viajeCopilotoId)
    return getEstado(viajeCopiloto).capitalize()


@register.filter(is_safe=True)
def estadoCopilotoViajeClass(viajeCopilotoId):
    viajeCopiloto = ViajeCopiloto.objects.get(pk=viajeCopilotoId)
    estado = getEstado(viajeCopiloto)
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
    estado = getEstado(viajeCopiloto)
    if estado == "finalizado":
        return "<button class='btn btn-default' onclick=calificarPiloto({0})>Calificar</button>".format(viajeCopilotoId)
    return "<button class='btn btn-default' disabled>Calificar</button>"

