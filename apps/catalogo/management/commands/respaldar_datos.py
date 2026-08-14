"""Comando de gestión: respalda la información del inventario (RNF-11).

Uso:
    python manage.py respaldar_datos [--destino carpeta]

Genera un volcado JSON con fecha y hora en el nombre, con los datos de
las cuatro apps del dominio (cuentas, catalogo, registros, curaduria).
No incluye sesiones ni el log de administración de Django: eso no es
"información del inventario", es estado transitorio del servidor.

Para restaurar un respaldo:
    python manage.py loaddata respaldos/ojo_avizor_AAAAMMDD_HHMMSS.json
"""
import datetime
from pathlib import Path

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand

_APPS_A_RESPALDAR = ['cuentas', 'catalogo', 'registros', 'curaduria']


class Command(BaseCommand):
    help = 'Genera un respaldo JSON con la información del inventario (RNF-11).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--destino', type=str, default=None,
            help='Carpeta donde guardar el respaldo (por defecto: respaldos/ en la raíz del proyecto).',
        )

    def handle(self, *args, **options):
        carpeta = Path(options['destino']) if options['destino'] else Path(settings.BASE_DIR) / 'respaldos'
        carpeta.mkdir(parents=True, exist_ok=True)

        marca_de_tiempo = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        archivo = carpeta / f'ojo_avizor_{marca_de_tiempo}.json'

        with open(archivo, 'w', encoding='utf-8') as salida:
            management.call_command('dumpdata', *_APPS_A_RESPALDAR, indent=2, stdout=salida)

        self.stdout.write(self.style.SUCCESS(f'Respaldo generado en {archivo}'))
