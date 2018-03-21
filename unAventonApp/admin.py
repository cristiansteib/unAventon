from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(ConversationPrivateThread)
admin.site.register(ConversationPublicThread)
admin.site.register(Profile)
admin.site.register(Trip)
admin.site.register(Creditcard)
admin.site.register(BankEntity)