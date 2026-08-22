"""Consultas de la app registros: inventario consolidado (RF-26), avistamientos por especie."""
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import Fotografia, Registro


def contar_actividad_por_departamento():
    """Actividad del inventario agrupada por departamento y municipio (fuera
    del MVP original, pedido explícito del 22/08/2026) — solo avistamientos
    publicados, igual que el resto de cifras del inventario consolidado
    (RF-26). Nunca coordenadas: departamento/municipio son tan públicos
    como `lugar`, no rozan la reserva de RN-06."""
    filas = (
        Registro.publicados.values('departamento', 'municipio')
        .annotate(total=Count('id'))
        .order_by('-total', 'departamento', 'municipio')
    )
    por_departamento = {}
    for fila in filas:
        depto = por_departamento.setdefault(
            fila['departamento'], {'nombre': fila['departamento'], 'total': 0, 'municipios': []},
        )
        depto['total'] += fila['total']
        depto['municipios'].append({'nombre': fila['municipio'], 'total': fila['total']})
    return sorted(por_departamento.values(), key=lambda depto: -depto['total'])


def listar_de_usuario(usuario, estado=None):
    registros = Registro.objects.filter(usuario=usuario).select_related('especie').order_by('-fecha_envio')
    if estado:
        registros = registros.filter(estado=estado)
    return registros


def obtener_de_usuario(pk, usuario):
    return Registro.objects.select_related('especie').get(pk=pk, usuario=usuario)


def contar_observadores_participantes():
    return Registro.publicados.values('usuario').distinct().count()


def contar_avistamientos_publicados():
    return Registro.publicados.count()


def listar_fotos_de_especie(especie):
    """Fotos de los avistamientos aprobados de una especie: la Capa 2 alimentando la
    Capa 1 (RF-21), tal como lo describe CLAUDE.md, apartado 2."""
    return (
        Fotografia.objects.filter(registro__in=Registro.publicados.filter(especie=especie))
        .select_related('registro__usuario')
        .order_by('-fecha_subida')
    )


def listar_ultimos_publicados(cantidad=6):
    """Los avistamientos aprobados más recientes, para mostrar actividad de la comunidad."""
    return (
        Registro.publicados.select_related('especie', 'usuario')
        .order_by('-fecha_avistamiento', '-fecha_envio')[:cantidad]
    )


def listar_avistamientos_publicos():
    """RF-26: todos los avistamientos aprobados, del más reciente al más antiguo."""
    return (
        Registro.publicados.select_related('especie', 'usuario')
        .order_by('-fecha_avistamiento', '-fecha_envio')
    )


def ranking_observadores():
    """Seudónimos ordenados por cantidad de avistamientos aprobados — nunca el
    nombre real ni el correo (RN-02), el catálogo público solo conoce el seudónimo.
    Cada fila trae también la racha de días seguidos registrando de ese usuario."""
    filas = list(
        Registro.publicados.values('usuario_id', 'usuario__seudonimo')
        .annotate(total_aportes=Count('id'))
        .order_by('-total_aportes', 'usuario__seudonimo')
    )
    rachas = calcular_rachas_por_usuario()
    for fila in filas:
        fila['racha'] = rachas.get(fila['usuario_id'], 0)
    return filas


def _racha_desde_fechas(fechas):
    """Días consecutivos hasta hoy — o hasta ayer si hoy todavía no hay actividad:
    la racha sigue viva mientras no pase un día entero sin registrar."""
    if not fechas:
        return 0
    hoy = timezone.localdate()
    cursor = hoy if hoy in fechas else hoy - timedelta(days=1)
    racha = 0
    while cursor in fechas:
        racha += 1
        cursor -= timedelta(days=1)
    return racha


def calcular_racha_de_usuario(usuario):
    """Días seguidos que un usuario ha registrado avistamientos (cualquier estado:
    lo que cuenta para la racha es el hábito de registrar, no si ya se aprobó)."""
    fechas = set(
        Registro.objects.filter(usuario=usuario)
        .annotate(dia=TruncDate('fecha_envio'))
        .values_list('dia', flat=True)
        .distinct()
    )
    return _racha_desde_fechas(fechas)


def calcular_rachas_por_usuario():
    """La racha de cada usuario con al menos un registro, en una sola consulta —
    para no golpear la base de datos una vez por fila del ranking."""
    fechas_por_usuario = {}
    filas = Registro.objects.annotate(dia=TruncDate('fecha_envio')).values_list('usuario_id', 'dia').distinct()
    for usuario_id, dia in filas:
        fechas_por_usuario.setdefault(usuario_id, set()).add(dia)
    return {usuario_id: _racha_desde_fechas(fechas) for usuario_id, fechas in fechas_por_usuario.items()}


def contar_todos_por_estado():
    """Cuántos registros hay en cada estado, para el panel de administrador."""
    conteos = {estado: 0 for estado, _ in Registro.Estado.choices}
    for fila in Registro.objects.values('estado').annotate(total=Count('id')):
        conteos[fila['estado']] = fila['total']
    return conteos


def contar_por_estado_de_usuario(usuario):
    """Cuántos registros tiene un usuario en cada estado, para su página de cuenta."""
    conteos = {estado: 0 for estado, _ in Registro.Estado.choices}
    filas = Registro.objects.filter(usuario=usuario).values('estado').annotate(total=Count('id'))
    for fila in filas:
        conteos[fila['estado']] = fila['total']
    return conteos


def contar_especies_distintas_de_usuario(usuario):
    """Especies distintas que un usuario ha avistado, contando solo aportes ya aprobados."""
    return (
        Registro.publicados.filter(usuario=usuario, especie__isnull=False)
        .values('especie').distinct().count()
    )


def listar_para_identificar():
    """Registros que piden ayuda de la comunidad para identificar la especie (RF-19, RF-29)."""
    return (
        Registro.objects.filter(sin_identificar=True)
        .select_related('usuario')
        .prefetch_related('fotografias')
        .annotate(total_comentarios=Count('comentarios_identificacion'))
        .order_by('-fecha_envio')
    )


def obtener_para_identificar(pk):
    """Un registro sin identificar con su hilo de comentarios y votos ya cargados."""
    return (
        Registro.objects.filter(sin_identificar=True)
        .select_related('usuario')
        .prefetch_related('fotografias', 'comentarios_identificacion__usuario', 'comentarios_identificacion__votos')
        .get(pk=pk)
    )
