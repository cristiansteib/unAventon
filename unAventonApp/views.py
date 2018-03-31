from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hola")

def login(request):
    return render(request,'unAventonApp/login.html')

def signIn(request):
    return render(request,'unAventonApp/singIn.html')