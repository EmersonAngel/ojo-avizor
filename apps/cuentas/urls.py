from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = 'cuentas'

urlpatterns = [
    path('registrar/', views.registrar, name='registrar'),
    path('mi-cuenta/', views.mi_cuenta, name='mi_cuenta'),
    path('mi-cuenta/solicitar-revisor/', views.solicitar_revisor, name='solicitar_revisor'),
    path('mi-cuenta/notificaciones/', views.actualizar_notificaciones, name='actualizar_notificaciones'),
    path('panel/', views.panel_admin, name='panel_admin'),
    path('panel/solicitudes/<int:pk>/aprobar/', views.solicitud_revisor_aprobar, name='solicitud_revisor_aprobar'),
    path('panel/solicitudes/<int:pk>/rechazar/', views.solicitud_revisor_rechazar, name='solicitud_revisor_rechazar'),
    path(
        'entrar/',
        auth_views.LoginView.as_view(template_name='cuentas/sesion_iniciar.html'),
        name='iniciar_sesion',
    ),
    path('salir/', auth_views.LogoutView.as_view(), name='cerrar_sesion'),

    # Recuperar contraseña (auth_views built-in de Django). Cada vista fija su
    # propio success_url con el namespace 'cuentas:', porque el valor por
    # defecto de Django busca el nombre de URL sin namespace y no lo
    # encontraría en este urls.py (app_name = 'cuentas').
    path(
        'recuperar-contrasena/',
        auth_views.PasswordResetView.as_view(
            template_name='cuentas/contrasena_recuperar.html',
            email_template_name='cuentas/correo_recuperar_contrasena.txt',
            subject_template_name='cuentas/correo_recuperar_contrasena_asunto.txt',
            success_url=reverse_lazy('cuentas:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'recuperar-contrasena/enviado/',
        auth_views.PasswordResetDoneView.as_view(template_name='cuentas/contrasena_recuperar_enviado.html'),
        name='password_reset_done',
    ),
    path(
        'recuperar-contrasena/confirmar/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='cuentas/contrasena_confirmar.html',
            success_url=reverse_lazy('cuentas:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'recuperar-contrasena/completo/',
        auth_views.PasswordResetCompleteView.as_view(template_name='cuentas/contrasena_completa.html'),
        name='password_reset_complete',
    ),
]
