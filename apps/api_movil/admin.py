from django.contrib import admin

from .models import TokenAcceso


@admin.register(TokenAcceso)
class TokenAccesoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_creacion', 'fecha_ultimo_uso')
    readonly_fields = ('token_hash', 'fecha_creacion', 'fecha_ultimo_uso')
