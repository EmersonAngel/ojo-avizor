from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('seudonimo', 'correo', 'rol', 'estado', 'is_staff')
    list_filter = ('rol', 'estado', 'is_staff')
    search_fields = ('seudonimo', 'correo', 'nombre_real', 'username')
    ordering = ('seudonimo',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Datos personales', {'fields': ('nombre_real', 'correo', 'seudonimo')}),
        ('Rol y estado', {'fields': ('rol', 'estado')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'date_joined', 'fecha_registro')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'correo', 'nombre_real', 'seudonimo', 'rol', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('fecha_registro',)
