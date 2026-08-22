from django.urls import path

from . import views

app_name = 'curaduria'

urlpatterns = [
    path('', views.bandeja, name='bandeja'),
    path('<int:pk>/', views.detalle, name='detalle'),
    path('<int:pk>/aprobar/', views.aprobar, name='aprobar'),
    path('<int:pk>/devolver/', views.devolver, name='devolver'),
    path('<int:pk>/agregar-nombre-propuesto/', views.agregar_nombre_propuesto, name='agregar_nombre_propuesto'),
]
