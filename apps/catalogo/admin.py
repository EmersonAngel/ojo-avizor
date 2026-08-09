from django.contrib import admin

from .models import Especie, NombreComun


class NombreComunInline(admin.TabularInline):
    model = NombreComun
    extra = 1


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ('nombre_cientifico', 'familia', 'orden', 'creado_por', 'fecha_creacion')
    search_fields = ('nombre_cientifico', 'familia', 'orden', 'nombres_comunes__nombre')
    list_filter = ('familia', 'orden')
    inlines = [NombreComunInline]
    readonly_fields = ('fecha_creacion',)


@admin.register(NombreComun)
class NombreComunAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie', 'region', 'es_local', 'estado')
    list_filter = ('estado', 'es_local', 'region')
    search_fields = ('nombre', 'especie__nombre_cientifico')
