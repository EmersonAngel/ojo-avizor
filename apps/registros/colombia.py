"""Departamentos de Colombia, para agrupar la actividad del inventario por
región (pedido explícito del 22/08/2026, fuera del MVP original).

Ojo Avizor es un inventario de un solo municipio (Pijao, Quindío), pero se
deja preparada la división administrativa completa del país por si en el
futuro se suman observadores de otros lugares — no tendría sentido acotar
la lista a Quindío y tener que ampliarla después.

No hay una lista curada de municipios: Colombia tiene más de mil y una
lista incompleta o desactualizada sería peor que no tenerla. El municipio
queda como texto libre (igual que ya es `lugar`); el departamento sí es
una lista cerrada porque son solo 33 y son estables en el tiempo.
"""
from django.utils.translation import gettext_lazy as _

DEPARTAMENTOS = [
    ('Amazonas', _('Amazonas')),
    ('Antioquia', _('Antioquia')),
    ('Arauca', _('Arauca')),
    ('Atlántico', _('Atlántico')),
    ('Bogotá D.C.', _('Bogotá D.C.')),
    ('Bolívar', _('Bolívar')),
    ('Boyacá', _('Boyacá')),
    ('Caldas', _('Caldas')),
    ('Caquetá', _('Caquetá')),
    ('Casanare', _('Casanare')),
    ('Cauca', _('Cauca')),
    ('Cesar', _('Cesar')),
    ('Chocó', _('Chocó')),
    ('Córdoba', _('Córdoba')),
    ('Cundinamarca', _('Cundinamarca')),
    ('Guainía', _('Guainía')),
    ('Guaviare', _('Guaviare')),
    ('Huila', _('Huila')),
    ('La Guajira', _('La Guajira')),
    ('Magdalena', _('Magdalena')),
    ('Meta', _('Meta')),
    ('Nariño', _('Nariño')),
    ('Norte de Santander', _('Norte de Santander')),
    ('Putumayo', _('Putumayo')),
    ('Quindío', _('Quindío')),
    ('Risaralda', _('Risaralda')),
    ('San Andrés y Providencia', _('San Andrés y Providencia')),
    ('Santander', _('Santander')),
    ('Sucre', _('Sucre')),
    ('Tolima', _('Tolima')),
    ('Valle del Cauca', _('Valle del Cauca')),
    ('Vaupés', _('Vaupés')),
    ('Vichada', _('Vichada')),
]

DEPARTAMENTO_POR_DEFECTO = 'Quindío'
MUNICIPIO_POR_DEFECTO = 'Pijao'
