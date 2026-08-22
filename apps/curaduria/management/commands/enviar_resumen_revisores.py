"""Comando de gestión: aviso resumido a los revisores (RF-24).

Fuera del MVP original, construido por pedido explícito del 22/08/2026.
Manda un solo correo con el total de registros pendientes a cada Revisor
y Administrador con las notificaciones activadas — no uno por cada
registro nuevo, para no saturar. Si no hay nada pendiente, no manda nada.

Pensado para ejecutarse una vez al día (o a la semana) vía una tarea
programada del sistema operativo o del proveedor de hosting — este
proyecto no usa Celery ni ninguna otra cola de tareas (RNF-08: costos
sostenibles), así que la periodicidad la decide quien programe la tarea,
no el comando en sí.

Uso:
    python manage.py enviar_resumen_revisores

Ejemplo de tarea programada (cron, todos los días a las 7 a.m.):
    0 7 * * * cd /ruta/al/proyecto && venv/bin/python manage.py enviar_resumen_revisores
"""
from django.core.management.base import BaseCommand

from apps.curaduria import services


class Command(BaseCommand):
    help = 'Manda un aviso resumido por correo a los revisores con registros pendientes (RF-24).'

    def handle(self, *args, **options):
        enviados = services.enviar_resumen_pendientes_a_revisores()
        if enviados:
            self.stdout.write(self.style.SUCCESS(f'Resumen enviado a {enviados} revisor(es).'))
        else:
            self.stdout.write('Nada que avisar: no hay pendientes o nadie tiene el correo activado.')
