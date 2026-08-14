from django.urls import path

from . import views

app_name = 'curaduria'

urlpatterns = [
    path('', views.bandeja, name='bandeja'),
    path('<int:pk>/aprobar/', views.aprobar, name='aprobar'),
    path('<int:pk>/devolver/', views.devolver, name='devolver'),
]
