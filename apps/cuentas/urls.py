from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'cuentas'

urlpatterns = [
    path('registrar/', views.registrar, name='registrar'),
    path('mi-cuenta/', views.mi_cuenta, name='mi_cuenta'),
    path('mi-cuenta/solicitar-revisor/', views.solicitar_revisor, name='solicitar_revisor'),
    path('panel/', views.panel_admin, name='panel_admin'),
    path('panel/solicitudes/<int:pk>/aprobar/', views.solicitud_revisor_aprobar, name='solicitud_revisor_aprobar'),
    path('panel/solicitudes/<int:pk>/rechazar/', views.solicitud_revisor_rechazar, name='solicitud_revisor_rechazar'),
    path(
        'entrar/',
        auth_views.LoginView.as_view(template_name='cuentas/sesion_iniciar.html'),
        name='iniciar_sesion',
    ),
    path('salir/', auth_views.LogoutView.as_view(), name='cerrar_sesion'),
]
