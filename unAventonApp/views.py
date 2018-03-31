from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request,'unAventonApp/index.html')

def login(request):
    return render(request,'unAventonApp/login.html')

def signIn(request):
    return render(request, 'unAventonApp/signIn.html')