from django.core.mail import send_mail
from django.conf import settings

def send_email(mail, subject='', message='', list_of_mails=None):
    if not list_of_mails:
        list_of_mails = [mail]
    if not settings.EMAIL_HOST_USER:
        print("NO SE  ENVIA MAIL, HOST USER SIN CONFIGURAR")
        return
    send_mail(
        'unAventon: ' + subject,
        message,
        settings.EMAIL_HOST_USER,
        list_of_mails,
        fail_silently=False,
    )
