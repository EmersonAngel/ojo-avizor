from django.urls import path

from . import views

app_name = 'api_movil'

urlpatterns = [
    path('login/', views.iniciar_sesion, name='login'),
    path('especies/', views.especies_listado, name='especies'),
    path('registros/', views.registro_crear, name='registros_crear'),
    path('registros/mios/', views.registros_mios, name='registros_mios'),
]
