from unAventonApp.modules.Git import Git
from django.conf import settings
from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()
@register.filter(is_safe=True)
def currentbranch(value):
    return (Git(settings.BASE_DIR).getActuallBranch())

