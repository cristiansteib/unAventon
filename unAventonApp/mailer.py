from django.core.mail import send_mail
from django.conf import settings
import threading


class senderThread(threading.Thread):
    def __init__(self, from_mail, list_of_mails, subject, message):
        threading.Thread.__init__(self)
        self.from_mail = from_mail
        self.list_of_mails = list_of_mails
        self.subject = subject
        self.message = message

    def run(self):
        self.send_email()

    def send_email(self):
        print('enviando mails a: {0}'.format(str(self.list_of_mails)))
        send_mail(
            self.subject,
            self.message,
            self.from_mail,
            self.list_of_mails,
            fail_silently=False,
        )


def send_email(mail, subject='', message='', list_of_mails=None):
    if not list_of_mails:
        list_of_mails = [mail]
    if not settings.EMAIL_HOST_USER:
        print("NO SE  ENVIA MAIL, HOST USER SIN CONFIGURAR")
        return
    subject = 'unAventon: ' + subject
    from_mail = settings.EMAIL_HOST_USER
    thread = senderThread(from_mail, list_of_mails, subject, message)
    thread.start()
