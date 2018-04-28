from unAventonApp.modules.Git import Git
from django.conf import settings
from django import template
from unAventonApp.models import Usuario

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
    return Git(settings.BASE_DIR).git('log','-1','--pretty=format:Last commit %ar')
