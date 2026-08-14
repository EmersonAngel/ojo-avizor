# Arquitectura y decisiones técnicas

> **Paquete de contexto v1.1** · 9 de agosto de 2026

---

## Arquitectura en capas con servicios de dominio

Cuatro capas, con una regla que las gobierna: **cada capa solo conoce la que tiene debajo**.

```
┌─────────────────────────────────────────┐
│  PRESENTACIÓN                           │
│  views.py · forms.py · templates        │
│  Recibe, valida formato, responde.      │
├─────────────────────────────────────────┤
│  SERVICIOS DE DOMINIO                   │
│  services.py                            │
│  Reglas de negocio, transiciones,       │
│  orquestación. El corazón del sistema.  │
├─────────────────────────────────────────┤
│  REPOSITORIOS                           │
│  repositories.py                        │
│  Consultas. Aísla el ORM del dominio.   │
├─────────────────────────────────────────┤
│  MODELO                                 │
│  models.py                              │
│  Estructura y validación de campo.      │
└─────────────────────────────────────────┘
```

### Por qué esta arquitectura y no otra

Se consideraron tres opciones.

**Arquitectura limpia canónica** —entidades, casos de uso, puertos y adaptadores con inversión de dependencias— es la más rigurosa, pero multiplica archivos e interfaces. Para un solo desarrollador con un plazo corto, el costo supera al beneficio.

**MVC clásico** de Django es lo más rápido, pero deja la lógica de negocio repartida entre vistas y modelos. En este proyecto hay lógica que merece protección: el flujo de curaduría, las transiciones de estado y las reglas de publicación.

**Capas con servicios de dominio** conserva la separación donde importa sin la ceremonia completa. Y tiene una ventaja de cara a la Fase 2: cuando otra persona añada el módulo educativo, encontrará la lógica de negocio en un lugar identificable.

### Ejemplo de la regla en la práctica

```python
# ❌ MAL — lógica de negocio en la vista
def aprobar(request, registro_id):
    registro = Registro.objects.get(id=registro_id)
    registro.estado = 'APROBADO'      # transición directa
    registro.save()
    return redirect('bandeja')

# ✅ BIEN — la vista delega en el servicio
def aprobar(request, registro_id):
    try:
        servicios.aprobar_registro(registro_id, revisor=request.user)
    except TransicionInvalida as e:
        messages.error(request, str(e))
    return redirect('bandeja')
```

El servicio valida la transición, comprueba el rol, crea la Revision y cambia el estado, todo en una transacción.

---

## Decisiones técnicas

| Decisión | Alternativa descartada | Justificación |
| --- | --- | --- |
| **Django** | Spring Boot | Trae de fábrica autenticación, roles y panel de administración. Resuelve RF-09, RF-10, RF-13, RF-14 y RF-25 con muy poco código, lo que es determinante con el plazo disponible. |
| **HTMX + Alpine** | Angular como aplicación separada | Un solo proyecto y un solo despliegue. Envía fragmentos de HTML en vez de JSON, lo que reduce el JavaScript en ejecución y los datos en tránsito: cumple RNF-01 y RNF-03 por diseño. |
| **PostgreSQL** | MySQL | Mejor manejo de campos JSON y de texto, y soporte geoespacial disponible si más adelante entra el mapa (RF-22). |
| **Tailwind CSS** | Bootstrap | Diseño adaptable sin arrastrar componentes que no se usan. Cumple RNF-02 con menos peso. |
| **Pillow** | Servicio externo de imágenes | Compresión en el propio servidor, sin costo adicional. Cumple RNF-04 y RNF-08. |
| **Sin Django REST Framework** | API REST + cliente | No hay cliente externo que consumir. Añadiría una capa sin beneficio en este alcance. |

---

## Metodología

**Scrum adaptado a un solo desarrollador**, con sprints de una semana.

- **Product backlog:** los 29 requisitos priorizados; 20 en el MVP.
- **Sprint backlog:** lo comprometido para la semana.
- **Incremento:** al cierre de cada sprint debe haber algo ejecutable.
- **Revisión:** con la tutora empresarial al final de cada sprint.
- **Retrospectiva:** documentada por el propio desarrollador; alimenta el capítulo de recomendaciones del informe.

---

## Cómo se resuelve el registro sin conexión (RF-23)

Alcance acotado, no sincronización bidireccional:

1. Un *service worker* cachea la página del formulario de registro.
2. Al enviar sin conexión, los datos se guardan en almacenamiento local del navegador con estado «en cola».
3. Al detectarse conexión, la cola se envía al servidor en orden.
4. El usuario ve en todo momento cuántos registros tiene pendientes de enviar.

Es el único punto del proyecto donde se escribe JavaScript propio de cierta extensión. No intentes resolverlo con HTMX: no es su caso de uso.

---

## Convenciones de nombres

| Elemento | Convención | Ejemplo |
| --- | --- | --- |
| Modelos | Español, singular, PascalCase | `NombreComun` |
| Tablas | Español, snake_case | `nombre_comun` |
| Campos | Español, snake_case | `fecha_avistamiento` |
| Servicios | Verbo en infinitivo | `aprobar_registro()` |
| Repositorios | `obtener_`, `listar_`, `contar_` | `listar_pendientes()` |
| Plantillas | `<app>/<recurso>_<accion>.html` | `catalogo/especie_detalle.html` |
| Rutas con nombre | `<app>:<accion>` | `registros:crear` |
| Excepciones propias | Sufijo descriptivo en español | `TransicionInvalida` |

Los términos del framework se conservan en inglés: `models.py`, `views.py`, `save()`, `get_queryset()`.

---

## Pruebas mínimas exigidas

No hace falta cobertura completa, pero estas no son negociables:

- Transiciones de estado válidas e inválidas del Registro.
- Que un registro no aprobado **nunca** aparezca en el catálogo público.
- Que una vista pública no exponga nombre real, correo ni coordenadas.
- Que devolver sin motivo falle.
- Que la búsqueda encuentre especies por nombre común además de por nombre científico.
