from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('metodo-grafico/', views.metodo_grafico, name='metodo_grafico'),
    path('metodo-simplex/', views.metodo_simplex, name='metodo_simplex'),
    path('login/', views.login_view, name='login'),
    path('Registrarse/', views.register_view, name='Registrarse'),
]
