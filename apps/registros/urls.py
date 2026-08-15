from django.urls import path

from . import views

app_name = 'registros'

urlpatterns = [
    path('nuevo/', views.registro_crear, name='crear'),
    path('nuevo/enviado/', views.registro_enviado, name='enviado'),
    path('mios/', views.registro_mis, name='mis_registros'),
    path('<int:pk>/corregir/', views.registro_corregir, name='corregir'),
]
