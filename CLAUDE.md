# Ojo Avizor — Plataforma de inventario de avifauna de Pijao

> **Paquete de contexto v1.2** · 14 de agosto de 2026
> Si modificas este archivo, sube la versión y anótalo en el registro del final.

Lee también, en `docs/`: `arquitectura.md`, `modelo-datos.md`, `requisitos-mvp.md` y `reglas-negocio.md`.

---

## 1. Qué es este proyecto

Una plataforma web que consolida el inventario de avifauna del municipio de Pijao, Quindío, mediante el registro participativo de la comunidad.

El problema que resuelve: **existe conocimiento sobre las aves del municipio, pero no está consolidado**. Las plataformas globales de biodiversidad no permiten consultar Pijao como unidad territorial, no recogen los nombres comunes locales y no ofrecen forma de pedir ayuda para identificar un ave.

Es un proyecto de práctica empresarial de Ingeniería de Software, desarrollado con la Fundación Smurfit Westrock Colombia para el semillero de observación de aves *Semillas de La Cordillera*.

**Fecha límite de esta entrega: 18–21 de agosto de 2026.** Quedan pocos días. Prioriza que funcione sobre que sea perfecto, pero sin romper las reglas de este documento.

## 2. El modelo de dos capas

Es la decisión estructural del proyecto. Todo depende de entenderla.

**Capa 1 — Ficha de especie.** Una entrada única por especie, creada y curada por usuarios con conocimiento (rol Revisor o Administrador). Contiene nombre científico, todos los nombres comunes locales, foto de referencia, distribución, tamaño e historia natural.

**Capa 2 — Registro de avistamiento.** Múltiples por especie, aportados por cualquier usuario con rol Observador. Contiene lugar, fecha y autor como obligatorios.

La Capa 2 alimenta a la Capa 1: las fotografías aportadas se acumulan por especie. **Ningún registro se publica sin pasar por revisión.**

## 3. Pila técnica

| Componente | Elección |
| --- | --- |
| Lenguaje | Python 3.12 |
| Framework | Django 5.x |
| Base de datos | PostgreSQL |
| Interactividad | HTMX + Alpine.js |
| Estilos | Tailwind CSS |
| Imágenes | Pillow para compresión y redimensionado |
| Idiomas | Django i18n — español (por defecto) e inglés |

**Todo en un solo proyecto Django.** No hay API separada ni aplicación de una sola página. Django renderiza HTML; HTMX intercambia fragmentos; Alpine cubre la interactividad puntual.

**No introduzcas Django REST Framework** salvo que se justifique explícitamente. Se descartó a propósito: añade una capa que este alcance no necesita.

## 4. Reglas de código

**Idioma.** El dominio se nombra en español: modelos, campos, tablas, servicios, variables y funciones propias. Los términos del framework se dejan en inglés (`models.py`, `views.py`, `save()`, `get_queryset()`). Docstrings y comentarios en español.

**Dónde va cada cosa.**
- La lógica de negocio va en `services.py` de cada app. **Nunca en las vistas ni en los modelos.**
- Las vistas reciben, validan formato, llaman a un servicio y responden. Nada más.
- Las consultas complejas van en `repositories.py`.
- Los modelos definen estructura y validaciones de campo, no procesos.

**Transiciones de estado.** El estado de un registro solo cambia a través de un servicio, nunca asignando el campo directamente desde una vista.

**Migraciones.** Cada cambio de modelo genera su migración en el mismo commit.

**Commits.** En español, en imperativo: `añade modelo Especie`, `corrige validación de fecha de avistamiento`.

## 5. Estructura del proyecto

```
ojo_avizor/
├── config/              # settings, urls raíz, wsgi
├── apps/
│   ├── cuentas/         # Usuario, roles, autenticación
│   ├── catalogo/        # Especie, NombreComun
│   ├── registros/       # Registro, Fotografia
│   └── curaduria/       # Revision y flujo de revisión
├── templates/
│   ├── base.html
│   └── <app>/
├── static/
├── locale/              # traducciones es / en
├── docs/                # este paquete de contexto
└── manage.py
```

Cada app contiene: `models.py`, `services.py`, `repositories.py`, `forms.py`, `views.py`, `urls.py`, `admin.py`, `tests/`.

## 6. Qué NO hacer

- **No inventes requisitos.** Si algo no está en `requisitos-mvp.md`, no se construye. Pregunta antes.
- **No implementes lo que está fuera del MVP** (lista al final de `requisitos-mvp.md`), aunque parezca fácil.
- **No pongas lógica de negocio en las vistas.**
- **No publiques datos personales de menores.** Ver `reglas-negocio.md`, regla RN-02. En el catálogo público solo aparece el seudónimo.
- **No expongas coordenadas en vistas públicas.** La latitud y la longitud son información reservada a Revisor y Administrador (RN-06). En público, solo el campo `lugar`.
- **No uses fotografías tomadas de internet** para datos de prueba. Usa imágenes de marcador de posición genéricas.
- **No cambies el modelo de dos capas** sin avisar: rompe todo el diseño.
- **No añadas dependencias pesadas** sin justificarlo. Los costos de operación deben ser sostenibles después de la práctica.

## 7. Orden de trabajo sugerido

**Sprint 1 (9–15 de agosto)**
1. Configuración del proyecto, `settings` por entorno, conexión a PostgreSQL.
2. App `cuentas`: modelo Usuario con roles, registro, inicio de sesión, seudónimo.
3. App `catalogo`: modelos Especie y NombreComun, servicios y CRUD para Revisor y Administrador.
4. Migraciones y datos de prueba.

**Sprint 2 (16–20 de agosto)**
5. App `registros`: modelo Registro y Fotografia, formulario de registro, compresión de imágenes.
6. App `curaduria`: modelo Revision, flujo de estados, bandeja del revisor.
7. Catálogo público: listado, ficha de especie, búsqueda, inventario consolidado.
8. Guardado local y envío diferido para registrar sin conexión.
9. Documentación técnica y manual de uso.

## 8. Contexto que conviene tener presente

Los usuarios finales son niños y jóvenes de 10 a 15 años, y observadores adultos del municipio. Usan **celulares de gama media y baja**, con conexión regular en la zona urbana y peor en el campo. Eso condiciona todo: páginas ligeras, poco JavaScript, imágenes comprimidas.

El grupo piloto son 8 estudiantes del Instituto Pijao. La plataforma se dimensiona para **10 usuarios simultáneos**, no para miles.

---

## Registro de cambios del paquete

| Versión | Fecha | Cambios |
| --- | --- | --- |
| 1.0 | 09/08/2026 | Versión inicial del paquete de contexto. |
| 1.1 | 09/08/2026 | **RN-06 confirmada.** Las coordenadas de un avistamiento pasan a ser información reservada: se almacenan completas, pero solo son visibles para Revisor y Administrador. En el catálogo público se muestra únicamente `lugar`. Afecta a `reglas-negocio.md`, `modelo-datos.md`, `requisitos-mvp.md` y `arquitectura.md`. |
| **1.2** | **14/08/2026** | **Cambio de nombre.** El proyecto pasa a llamarse **Ojo Avizor** (antes «Avisté»). Cambia la marca en toda la interfaz, el nombre de la base de datos (`ojo_avizor`), la documentación y los identificadores internos del código. No afecta el modelo de datos ni ninguna regla de negocio. |
