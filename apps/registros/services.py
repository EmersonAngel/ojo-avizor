"""Servicios de dominio de la app registros.

Creación de avistamientos, compresión de fotografías (RF-02, RNF-04) y
las transiciones de estado del Registro que le corresponden a esta app:
BORRADOR → PENDIENTE (envío) y DEVUELTO → PENDIENTE (corrección tras
RF-08). Las transiciones PENDIENTE → APROBADO/DEVUELTO viven en
apps.curaduria.services, junto con la Revision. Ninguna vista asigna
`estado` directamente (RN-01, RN-03).
"""
import csv
import io

from django.core.files.base import ContentFile
from django.db import transaction
from PIL import Image

from .colombia import DEPARTAMENTO_POR_DEFECTO, MUNICIPIO_POR_DEFECTO
from .models import ComentarioIdentificacion, Fotografia, Registro, VotoComentario

TAMANO_MAXIMO_PX = 1600
CALIDAD_JPEG = 80


class TransicionInvalida(Exception):
    pass


def comprimir_imagen(archivo):
    """Redimensiona y recomprime una imagen subida a JPEG liviano (RNF-04)."""
    imagen = Image.open(archivo)
    imagen = imagen.convert('RGB')
    imagen.thumbnail((TAMANO_MAXIMO_PX, TAMANO_MAXIMO_PX))
    buffer = io.BytesIO()
    imagen.save(buffer, format='JPEG', quality=CALIDAD_JPEG, optimize=True)
    nombre_base = archivo.name.rsplit('.', 1)[0]
    return ContentFile(buffer.getvalue(), name=f'{nombre_base}.jpg')


def agregar_fotografia(registro, archivo):
    return Fotografia.objects.create(registro=registro, archivo=comprimir_imagen(archivo))


def enviar_registro(registro):
    """BORRADOR → PENDIENTE (RF-01, RN-01)."""
    if registro.estado != Registro.Estado.BORRADOR:
        raise TransicionInvalida('Solo un registro en BORRADOR puede enviarse.')
    registro.estado = Registro.Estado.PENDIENTE
    registro.save(update_fields=['estado'])


@transaction.atomic
def crear_registro(*, usuario, especie, lugar, fecha_avistamiento, latitud=None, longitud=None,
                    comportamiento='', sustrato='', info_adicional='', sin_identificar=False,
                    nombre_comun_propuesto='', departamento=DEPARTAMENTO_POR_DEFECTO,
                    municipio=MUNICIPIO_POR_DEFECTO, fotos=()):
    """Crea un avistamiento y lo envía a revisión de inmediato (RF-01, RF-11)."""
    registro = Registro(
        usuario=usuario,
        especie=especie,
        lugar=lugar,
        departamento=departamento,
        municipio=municipio,
        fecha_avistamiento=fecha_avistamiento,
        latitud=latitud,
        longitud=longitud,
        comportamiento=comportamiento,
        sustrato=sustrato,
        info_adicional=info_adicional,
        sin_identificar=sin_identificar,
        nombre_comun_propuesto=nombre_comun_propuesto,
    )
    registro.full_clean()
    registro.save()
    for archivo in fotos:
        agregar_fotografia(registro, archivo)
    enviar_registro(registro)
    return registro


@transaction.atomic
def corregir_registro(registro, *, especie, lugar, fecha_avistamiento, latitud=None, longitud=None,
                       comportamiento='', sustrato='', info_adicional='', sin_identificar=False,
                       nombre_comun_propuesto='', departamento=DEPARTAMENTO_POR_DEFECTO,
                       municipio=MUNICIPIO_POR_DEFECTO, fotos=()):
    """DEVUELTO → PENDIENTE tras la corrección de su autor (RF-08)."""
    if registro.estado != Registro.Estado.DEVUELTO:
        raise TransicionInvalida('Solo se puede corregir un registro DEVUELTO.')
    registro.especie = especie
    registro.lugar = lugar
    registro.departamento = departamento
    registro.municipio = municipio
    registro.fecha_avistamiento = fecha_avistamiento
    registro.latitud = latitud
    registro.longitud = longitud
    registro.comportamiento = comportamiento
    registro.sustrato = sustrato
    registro.info_adicional = info_adicional
    registro.sin_identificar = sin_identificar
    registro.nombre_comun_propuesto = nombre_comun_propuesto
    registro.full_clean()
    registro.estado = Registro.Estado.PENDIENTE
    registro.save()
    for archivo in fotos:
        agregar_fotografia(registro, archivo)
    return registro


def crear_comentario_identificacion(*, registro, usuario, texto):
    """Un aportante ayuda a identificar un registro `sin_identificar` (RF-19, RF-29)."""
    texto = (texto or '').strip()
    if not texto:
        raise ValueError('El comentario no puede estar vacío.')
    return ComentarioIdentificacion.objects.create(registro=registro, usuario=usuario, texto=texto)


def generar_csv_avistamientos():
    """Exportación del inventario consolidado (fuera del MVP original, pedido
    explícito del 22/08/2026), para que la Fundación o el semillero lo usen
    en informes fuera de la plataforma. Solo columnas ya públicas — nunca
    coordenadas, nombre real ni correo (RN-02, RN-06)."""
    buffer = io.StringIO()
    escritor = csv.writer(buffer)
    escritor.writerow(['nombre_cientifico', 'nombre_comun', 'lugar', 'fecha_avistamiento', 'observador'])

    registros = (
        Registro.publicados.select_related('especie', 'usuario')
        .prefetch_related('especie__nombres_comunes')
        .order_by('-fecha_avistamiento')
    )
    for registro in registros:
        especie = registro.especie
        nombres_comunes = list(especie.nombres_comunes.all()) if especie else []
        escritor.writerow([
            especie.nombre_cientifico if especie else '',
            nombres_comunes[0].nombre if nombres_comunes else '',
            registro.lugar,
            registro.fecha_avistamiento.isoformat(),
            registro.usuario.seudonimo,
        ])
    return buffer.getvalue()


@transaction.atomic
def votar_comentario(*, comentario, usuario, valor):
    """Un Revisor o Administrador vota un comentario de identificación. Repetir el mismo
    voto lo retira; votar lo contrario lo cambia — un voto por usuario y comentario."""
    voto = VotoComentario.objects.filter(comentario=comentario, usuario=usuario).first()
    if voto is None:
        VotoComentario.objects.create(comentario=comentario, usuario=usuario, valor=valor)
    elif voto.valor == valor:
        voto.delete()
    else:
        voto.valor = valor
        voto.save(update_fields=['valor'])
