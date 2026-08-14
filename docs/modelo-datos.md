# Modelo de datos

> **Paquete de contexto v1.1** · 9 de agosto de 2026

Seis entidades. Las dos primeras forman la **Capa 1** (curada); Registro y Fotografia forman la **Capa 2** (comunitaria).

---

## Usuario

Extiende `AbstractUser` de Django. Se declara en `AUTH_USER_MODEL` **antes de la primera migración**.

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | bigint | PK |
| `nombre_real` | varchar(150) | Obligatorio. **Nunca visible en el catálogo público.** |
| `correo` | email | Obligatorio, único. Sirve de identificador de acceso. |
| `seudonimo` | varchar(50) | Obligatorio, único. **Es lo único que se muestra públicamente.** |
| `rol` | varchar(20) | `ADMINISTRADOR`, `REVISOR`, `OBSERVADOR` |
| `password` | varchar | Gestionado por Django, siempre cifrado |
| `estado` | varchar(20) | `ACTIVO`, `SUSPENDIDO` |
| `fecha_registro` | datetime | Automático |

El rol **Visitante** no es un registro en base de datos: es el usuario no autenticado.

Jerarquía de permisos: Administrador ⊃ Revisor ⊃ Observador ⊃ Visitante. Quien tiene un rol dispone también de lo que puede hacer el rol inferior.

---

## Especie — Capa 1

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | bigint | PK |
| `nombre_cientifico` | varchar(150) | Obligatorio, único |
| `familia` | varchar(100) | Opcional |
| `orden` | varchar(100) | Opcional |
| `distribucion` | text | Opcional |
| `tamano_cm` | numeric(5,1) | Opcional |
| `historia_natural` | text | Opcional |
| `dato_curioso` | text | Opcional. Pensado para el uso didáctico posterior. |
| `foto_referencia` | ImageField | Opcional |
| `creado_por` | FK → Usuario | Campo en base de datos: `creado_por_id_usuario` |
| `fecha_creacion` | datetime | Automático |

Solo Revisor y Administrador crean o editan fichas.

---

## NombreComun — Capa 1

Una especie tiene **varios** nombres comunes. Es información que ninguna plataforma global recoge y constituye parte del valor del proyecto: una misma ave recibe nombres distintos según la región.

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | bigint | PK |
| `especie` | FK → Especie | `related_name='nombres_comunes'` |
| `nombre` | varchar(100) | Obligatorio |
| `region` | varchar(100) | Opcional. Ej.: «Quindío», «Pijao» |
| `es_local` | boolean | Marca las denominaciones propias del municipio |
| `estado` | varchar(20) | `APROBADO`, `PROPUESTO` |

Restricción de unicidad: (`especie`, `nombre`).

---

## Registro — Capa 2

Un avistamiento. Es la entidad central del sistema.

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | bigint | PK |
| `especie` | FK → Especie, **null=True** | Nulo cuando se envía sin identificar |
| `usuario` | FK → Usuario | Autor del registro |
| `lugar` | varchar(200) | **Obligatorio** |
| `latitud` | numeric(9,6) | Opcional. **Reservada: solo Revisor y Administrador** (RN-06) |
| `longitud` | numeric(9,6) | Opcional. **Reservada: solo Revisor y Administrador** (RN-06) |
| `fecha_avistamiento` | date | **Obligatorio.** No puede ser futura. |
| `fecha_envio` | datetime | Automático |
| `estado` | varchar(20) | `BORRADOR`, `PENDIENTE`, `APROBADO`, `DEVUELTO` |
| `comportamiento` | text | Opcional. Ej.: nidificando, llevando alimento |
| `sustrato` | varchar(150) | Opcional. Árbol o sustrato donde se observó |
| `info_adicional` | text | Opcional |
| `sin_identificar` | boolean | `True` cuando el autor pide ayuda para identificar |

**Solo los registros en estado `APROBADO` aparecen en el catálogo público.**

### Transiciones de estado

```
BORRADOR  ──enviar──▶  PENDIENTE
PENDIENTE ──aprobar──▶ APROBADO
PENDIENTE ──devolver─▶ DEVUELTO   (exige motivo)
DEVUELTO  ──corregir─▶ PENDIENTE
```

Cualquier otra transición es inválida y el servicio debe rechazarla. **El campo `estado` nunca se asigna directamente desde una vista.**

---

## Fotografia — Capa 2

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | bigint | PK |
| `registro` | FK → Registro | `related_name='fotografias'` |
| `archivo` | ImageField | Comprimido y redimensionado al guardar |
| `fecha_subida` | datetime | Automático |

La compresión ocurre en un servicio, no en el modelo. Objetivo: que la imagen conserve calidad suficiente para identificar la especie y pese lo mínimo posible.

---

## Revision

Registra cada decisión de curaduría. **No se borra nunca**: es la trazabilidad del proceso.

| Campo | Tipo | Notas |
| --- | --- | --- |
| `id` | bigint | PK |
| `registro` | FK → Registro | `related_name='revisiones'` |
| `revisor` | FK → Usuario | Quien decidió |
| `decision` | varchar(20) | `APROBADO`, `DEVUELTO` |
| `motivo` | text | **Obligatorio si la decisión es `DEVUELTO`** |
| `fecha` | datetime | Automático |

---

## Resumen de relaciones

| Origen | Cardinalidad | Destino |
| --- | --- | --- |
| Especie | 1 — N | NombreComun |
| Especie | 0..1 — N | Registro |
| Usuario | 1 — N | Registro (como autor) |
| Registro | 1 — N | Fotografia |
| Registro | 1 — N | Revision |
| Usuario | 1 — N | Revision (como revisor) |

---

## Índices recomendados

- `registro.estado` — se filtra en cada consulta del catálogo y de la bandeja de revisión.
- `registro.especie` — para contar avistamientos por especie.
- `especie.nombre_cientifico` — búsqueda.
- `nombre_comun.nombre` — búsqueda por nombre común, que es como busca la comunidad.
