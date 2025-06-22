from django.urls import path
from django.views.generic import TemplateView
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('metodo-grafico/', login_required(views.metodo_grafico), name='metodo_grafico'),
     path(
        'metodo-grafico/resultado/',
        login_required(views.resultado_metodo_grafico),
        name='resultado_metodo_grafico',
    ),
    path(
        'metodo-grafico/export/<str:formato>/',
        login_required(views.exportar_resultado),
        name='exportar_resultado',
    ),
    path(
        'metodo-simplex/',
        login_required(TemplateView.as_view(template_name='home.html')),
        name='metodo_simplex',
    ),
    path('perfil/', login_required(views.perfil_show), name='perfil_show'),
    path('perfil/editar/', login_required(views.perfil_edit), name='perfil_edit'),
    path('historial/', login_required(views.historial), name='historial'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
