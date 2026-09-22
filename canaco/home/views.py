from django.shortcuts import render

# Create your views here.
def index (request):
    return render(request, 'home/index.html')

def base (request):
    return render(request, 'home/base.html')

def categoria(request):
    return render(request, 'home/categoria.html')

def contactanos(request):
    return render(request, 'home/contactanos.html')

def crear_publicaciones(request):
    return render(request, 'home/crear_publicaciones')

def crear_usuario(request):
    return render(request, 'home/crear_usuario')