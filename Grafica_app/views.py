from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def metodo_grafico(request):
    return render(request, 'metodo_grafico.html')


def metodo_simplex(request):
    return render(request, 'metodo_simplex.html')


def login_view(request):
    return render(request, 'login.html')


def register_view(request):
    return render(request, 'Registrarse.html')
