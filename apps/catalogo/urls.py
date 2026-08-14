from django.urls import path

from . import views

app_name = 'catalogo'

urlpatterns = [
    # Público — sin autenticación (RN-05)
    path('', views.especie_listar_publico, name='publico_listado'),
    path('inventario/', views.inventario, name='inventario'),
    path('<int:pk>/', views.especie_detalle, name='especie_detalle'),

    # Gestión de fichas — Revisor y Administrador (RF-16, RF-17, RF-13)
    path('gestionar/', views.especie_listar, name='especie_listar'),
    path('gestionar/nueva/', views.especie_crear, name='especie_crear'),
    path('gestionar/<int:pk>/editar/', views.especie_editar, name='especie_editar'),
    path('gestionar/<int:pk>/retirar/', views.especie_retirar, name='especie_retirar'),
]
