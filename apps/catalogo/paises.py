"""Lista curada de países para el mapa de distribución de una especie.

No es la lista completa ISO 3166-1 (195 países): se limita a América y el
Caribe, que es donde se distribuyen las aves que puede registrar Ojo Avizor,
incluyendo las especies migratorias que pasan el invierno boreal en Pijao.
Los códigos son ISO 3166-1 alfa-2 en minúscula y coinciden con los id de
static/catalogo/mapa_mundo.svg.
"""
from django.utils.translation import gettext_lazy as _

PAISES_DISTRIBUCION = [
    ('ca', _('Canadá')),
    ('us', _('Estados Unidos')),
    ('mx', _('México')),
    ('bz', _('Belice')),
    ('gt', _('Guatemala')),
    ('hn', _('Honduras')),
    ('sv', _('El Salvador')),
    ('ni', _('Nicaragua')),
    ('cr', _('Costa Rica')),
    ('pa', _('Panamá')),
    ('cu', _('Cuba')),
    ('jm', _('Jamaica')),
    ('ht', _('Haití')),
    ('do', _('República Dominicana')),
    ('bs', _('Bahamas')),
    ('pr', _('Puerto Rico')),
    ('tt', _('Trinidad y Tobago')),
    ('bb', _('Barbados')),
    ('gd', _('Granada')),
    ('lc', _('Santa Lucía')),
    ('vc', _('San Vicente y las Granadinas')),
    ('ag', _('Antigua y Barbuda')),
    ('dm', _('Dominica')),
    ('kn', _('San Cristóbal y Nieves')),
    ('co', _('Colombia')),
    ('ve', _('Venezuela')),
    ('gy', _('Guyana')),
    ('sr', _('Surinam')),
    ('gf', _('Guayana Francesa')),
    ('ec', _('Ecuador')),
    ('pe', _('Perú')),
    ('br', _('Brasil')),
    ('bo', _('Bolivia')),
    ('py', _('Paraguay')),
    ('cl', _('Chile')),
    ('ar', _('Argentina')),
    ('uy', _('Uruguay')),
]

CODIGOS_VALIDOS = frozenset(codigo for codigo, _nombre in PAISES_DISTRIBUCION)
