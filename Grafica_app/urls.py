from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('metodo-grafico/', views.metodo_grafico, name='metodo_grafico'),
    path('metodo-grafico/export/<str:formato>/', views.exportar_resultado, name='exportar_resultado'),
    path('metodo-simplex/', TemplateView.as_view(template_name='home.html'), name='metodo_simplex'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path(
        'register/',
        TemplateView.as_view(
            template_name='register.html',
            extra_context={
                'title': 'Registro',
                'name_placeholder': 'Nombre completo',
                'username_placeholder': 'Usuario',
                'email_placeholder': 'Email',
                'password_placeholder': 'Contraseña',
                'button_text': 'Registrarse',
                'question_text': '¿Ya tienes una cuenta?',
                'login_text': 'Iniciar sesión',
            },
        ),
        name='register',
    ),
]
