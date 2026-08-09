from django.contrib import admin

from .models import Revision


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'registro', 'revisor', 'decision', 'fecha')
    list_filter = ('decision',)
    search_fields = ('registro__lugar', 'revisor__seudonimo', 'motivo')
    readonly_fields = ('fecha',)
