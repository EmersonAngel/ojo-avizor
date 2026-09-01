"""Códigos reproductivos de eBird, para el recuadro de clasificación junto al
campo "Comportamiento" (fuera del MVP original, pedido explícito del
30/08/2026 y ajustado el 31/08/2026: se clasifican aparte, no se insertan en
el texto libre de comportamiento — Registro.codigos_reproductivos, un
JSONField con la misma idea que Especie.paises_distribucion).

La lista y las siglas son las oficiales de eBird — se verificaron contra
https://support.ebird.org/en/support/solutions/articles/48000837520-ebird-breeding-and-behavior-codes
el 31/08/2026, no de memoria. Los nombres y definiciones están traducidos
al español para el público del semillero; las siglas se dejan tal como las
usa eBird, porque son el estándar que ya conocen los observadores con más
experiencia.
"""
from django.utils.translation import gettext_lazy as _

CODIGOS_REPRODUCTIVOS = (
    (_('Confirmada'), (
        ('NY', _('Nido con pichones')),
        ('NE', _('Nido con huevos')),
        ('FS', _('Retirando saco fecal')),
        ('FY', _('Alimentando volantones')),
        ('CF', _('Llevando comida para las crías')),
        ('FL', _('Volantón recién salido del nido')),
        ('ON', _('Nido ocupado')),
        ('UN', _('Nido usado, sin actividad')),
        ('DD', _('Despliegue de distracción (finge estar herida)')),
        ('NB', _('Construyendo nido')),
        ('CN', _('Llevando material para el nido')),
    )),
    (_('Probable'), (
        ('PE', _('Evidencia fisiológica (ej. parche de incubación)')),
        ('B', _('Construyendo nido, especie que hace varios nidos falsos')),
        ('A', _('Comportamiento agitado o alarma')),
        ('N', _('Visita repetida a un posible nido')),
        ('C', _('Cortejo, exhibición o cópula')),
        ('T', _('Defensa de territorio')),
        ('P', _('Pareja en hábitat adecuado para anidar')),
        ('M', _('Varios cantando (7 o más) en el mismo hábitat')),
        ('S7', _('Canta en el mismo sitio, visto una semana o más antes')),
    )),
    (_('Posible'), (
        ('S', _('Canta en hábitat adecuado para anidar')),
        ('H', _('En hábitat adecuado durante su temporada reproductiva')),
    )),
    (_('Observado'), (
        ('F', _('Vuelo de paso, sin posarse')),
    )),
)

CODIGOS_VALIDOS = frozenset(
    codigo for _categoria, codigos in CODIGOS_REPRODUCTIVOS for codigo, _nombre in codigos
)
