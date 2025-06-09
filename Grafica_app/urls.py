from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('metodo-grafico/', TemplateView.as_view(template_name='home.html'), name='metodo_grafico'),
    path('metodo-simplex/', TemplateView.as_view(template_name='home.html'), name='metodo_simplex'),
    path('login/', TemplateView.as_view(template_name='home.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='home.html'), name='register'),
]
