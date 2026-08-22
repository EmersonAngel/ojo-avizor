from django.urls import path

from . import views

app_name = 'registros'

urlpatterns = [
    # Público — sin autenticación
    path('', views.avistamientos_publicos, name='avistamientos_publicos'),
    path('ranking/', views.ranking_observadores, name='ranking_observadores'),

    path('nuevo/', views.registro_crear, name='crear'),
    path('nuevo/enviado/', views.registro_enviado, name='enviado'),
    path('mios/', views.registro_mis, name='mis_registros'),
    path('<int:pk>/corregir/', views.registro_corregir, name='corregir'),

    # Ayuda de la comunidad para identificar (RF-19, RF-29)
    path('identificar/', views.identificar_listar, name='identificar_listar'),
    path('identificar/<int:pk>/', views.identificar_detalle, name='identificar_detalle'),
    path('identificar/comentario/<int:pk>/votar/', views.identificar_votar_comentario, name='identificar_votar_comentario'),
]
