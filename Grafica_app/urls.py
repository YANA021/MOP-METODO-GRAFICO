from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('metodo-grafico/', views.metodo_grafico, name='metodo_grafico'),
    path('exportar/<str:formato>/', views.exportar_resultado, name='exportar_resultado'),
    path('metodo-simplex/', TemplateView.as_view(template_name='home.html'), name='metodo_simplex'),
    path('login/', TemplateView.as_view(template_name='home.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='home.html'), name='register'),
]
