"""Comando de gestión: importa fichas de especie desde un CSV (RF-14).

Uso:
    python manage.py importar_especies ruta/al/archivo.csv --usuario correo@ejemplo.com

Columnas esperadas en el CSV (cabecera obligatoria, separador coma):
    nombre_cientifico   obligatoria, única
    familia             opcional
    orden               opcional
    distribucion        opcional
    tamano_cm           opcional, numérico
    historia_natural    opcional
    dato_curioso        opcional
    nombres_comunes     opcional, varios nombres separados por ';'

Ver datos_ejemplo/especies_ejemplo.csv para un archivo de referencia.
"""
from django.core.management.base import BaseCommand, CommandError

from apps.catalogo import services
from apps.cuentas.models import Usuario


class Command(BaseCommand):
    help = 'Importa fichas de especie desde un archivo CSV (RF-14).'

    def add_arguments(self, parser):
        parser.add_argument('archivo_csv', type=str, help='Ruta al archivo CSV a importar.')
        parser.add_argument(
            '--usuario', type=str, required=True,
            help='Correo de un usuario con rol Revisor o Administrador, que figurará como creador de las fichas.',
        )

    def handle(self, *args, **options):
        try:
            creado_por = Usuario.objects.get(correo=options['usuario'])
        except Usuario.DoesNotExist:
            raise CommandError(f"No existe un usuario con el correo {options['usuario']!r}.")
        if creado_por.rol not in (Usuario.Rol.REVISOR, Usuario.Rol.ADMINISTRADOR):
            raise CommandError('El usuario indicado debe tener rol Revisor o Administrador.')

        try:
            archivo = open(options['archivo_csv'], newline='', encoding='utf-8-sig')
        except OSError as exc:
            raise CommandError(f'No se pudo abrir el archivo: {exc}')

        with archivo:
            resultado = services.importar_especies_desde_csv(archivo, creado_por=creado_por)

        self.stdout.write(self.style.SUCCESS(f"{len(resultado['creadas'])} ficha(s) creada(s)."))
        if resultado['omitidas']:
            self.stdout.write(self.style.WARNING(
                f"{len(resultado['omitidas'])} omitida(s) por ya existir: {', '.join(resultado['omitidas'])}"
            ))
        if resultado['errores']:
            self.stdout.write(self.style.ERROR(f"{len(resultado['errores'])} fila(s) con error:"))
            for numero_fila, mensaje in resultado['errores']:
                self.stdout.write(self.style.ERROR(f'  Fila {numero_fila}: {mensaje}'))
