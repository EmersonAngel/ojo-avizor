"""Vistas planas (JsonResponse) de la API para la app móvil nativa.

Sin Django REST Framework: son 4 endpoints acotados que reutilizan la
lógica de negocio existente (RegistroForm, crear_registro,
listar_especies, listar_de_usuario) en vez de duplicarla. Añadir DRF
completo por esto sería una dependencia pesada sin necesidad real.
"""
import json

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.catalogo.repositories import listar_especies
from apps.registros import repositories as registros_repositories
from apps.registros import services as registros_services
from apps.registros.forms import RegistroForm

from .auth import requiere_token
from .models import TokenAcceso


@csrf_exempt
@require_http_methods(['POST'])
def iniciar_sesion(request):
    try:
        datos = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'detalle': 'JSON inválido.'}, status=400)
    correo = (datos.get('correo') or '').strip().lower()
    password = datos.get('password') or ''
    usuario = authenticate(request, username=correo, password=password)
    if usuario is None:
        return JsonResponse({'detalle': 'Credenciales inválidas.'}, status=401)
    _, token_en_claro = TokenAcceso.crear(usuario)
    return JsonResponse({'token': token_en_claro, 'seudonimo': usuario.seudonimo, 'rol': usuario.rol})


@csrf_exempt
@requiere_token
@require_http_methods(['GET'])
def especies_listado(request):
    especies = listar_especies().prefetch_related('nombres_comunes')
    datos = [
        {
            'id': especie.pk,
            'nombre_cientifico': especie.nombre_cientifico,
            'nombres_comunes': [nc.nombre for nc in especie.nombres_comunes.all()],
            'foto_referencia': (
                request.build_absolute_uri(especie.foto_referencia.url) if especie.foto_referencia else None
            ),
        }
        for especie in especies
    ]
    return JsonResponse({'especies': datos})


@csrf_exempt
@requiere_token
@require_http_methods(['POST'])
def registro_crear(request):
    form = RegistroForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'errores': form.errors}, status=400)
    try:
        registro = registros_services.crear_registro(
            usuario=request.user, fotos=request.FILES.getlist('fotos'), **form.cleaned_data,
        )
    except ValidationError as error:
        return JsonResponse({'errores': {'__all__': error.messages}}, status=400)
    return JsonResponse({'id': registro.pk, 'estado': registro.estado}, status=201)


@csrf_exempt
@requiere_token
@require_http_methods(['GET'])
def racha(request):
    """Días seguidos registrando (fuera del MVP original, pedido explícito
    del 22/08/2026) — mismo cálculo que la versión web, ver
    apps.registros.repositories.calcular_racha_de_usuario."""
    return JsonResponse({'racha': registros_repositories.calcular_racha_de_usuario(request.user)})


@csrf_exempt
@requiere_token
@require_http_methods(['GET'])
def registros_mios(request):
    registros = registros_repositories.listar_de_usuario(request.user)[:50]
    datos = [
        {
            'id': registro.pk,
            'especie': registro.especie.nombre_cientifico if registro.especie else None,
            'lugar': registro.lugar,
            'fecha_avistamiento': registro.fecha_avistamiento.isoformat(),
            'estado': registro.estado,
        }
        for registro in registros
    ]
    return JsonResponse({'registros': datos})
