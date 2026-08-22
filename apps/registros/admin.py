from django.contrib import admin

from .models import ComentarioIdentificacion, Fotografia, Registro, VotoComentario


class FotografiaInline(admin.TabularInline):
    model = Fotografia
    extra = 0
    readonly_fields = ('fecha_subida',)


@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ('id', 'especie', 'usuario', 'lugar', 'fecha_avistamiento', 'estado')
    list_filter = ('estado', 'sin_identificar')
    search_fields = ('lugar', 'especie__nombre_cientifico', 'usuario__seudonimo')
    readonly_fields = ('fecha_envio',)
    inlines = [FotografiaInline]


@admin.register(Fotografia)
class FotografiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'registro', 'fecha_subida')
    readonly_fields = ('fecha_subida',)


@admin.register(ComentarioIdentificacion)
class ComentarioIdentificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'registro', 'usuario', 'fecha_creacion')
    readonly_fields = ('fecha_creacion',)
    search_fields = ('texto', 'usuario__seudonimo')


@admin.register(VotoComentario)
class VotoComentarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'comentario', 'usuario', 'valor', 'fecha')
    list_filter = ('valor',)
    readonly_fields = ('fecha',)
