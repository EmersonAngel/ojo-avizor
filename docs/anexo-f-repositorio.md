# Anexo F — Repositorio y control de versiones

Este anexo describe el repositorio en el que se ha desarrollado Ojo Avizor, las convenciones que rigen su historial y la forma en que ese historial refleja el avance del proyecto a lo largo de las tres semanas de trabajo. La información aquí presentada se obtuvo directamente del propio repositorio (`git log`, listado de ramas y de archivos versionados), no de un resumen aparte, de modo que sea verificable por cualquier persona con acceso a él.

## Datos del repositorio

El código fuente está alojado en GitHub, en `https://github.com/EmersonAngel/ojo-avizor`. Una consulta no autenticada a la API de GitHub sobre ese repositorio devuelve un código de respuesta 404 — la señal habitual de un repositorio privado, ya que GitHub responde así tanto para repositorios inexistentes como para privados sin permiso de lectura, precisamente para no revelar cuáles existen. **Esto queda pendiente de confirmación directa por parte del autor**: verificar en la configuración del repositorio que la visibilidad esté efectivamente en «privado», y documentar aquí el procedimiento real para solicitar acceso (por ejemplo, si se otorga agregando al solicitante como colaborador desde la configuración de GitHub, o por algún otro medio institucional).

## Convenciones adoptadas

Todos los mensajes de confirmación (*commits*) del proyecto están escritos en español y en modo imperativo — la forma que Git recomienda por convención (`Añade`, no `Añadido` ni `Se añadió`), y que aquí se aplicó además en español en vez de en inglés, coherente con el resto del código y la documentación del proyecto. Tres ejemplos reales, tomados directamente del historial:

- `crea proyecto Django con estructura por capas y modelo de datos inicial`
- `añade insignias por hitos y exportar el inventario en CSV`
- `corrige la barra: nunca estuvo pegada arriba de la pantalla`

Estos tres ejemplos ilustran también el patrón de verbos que se mantuvo a lo largo de todo el historial: *crea*/*añade* para funcionalidad nueva, *corrige* para resolver un defecto, *mejora*/*ajusta* para refinar algo ya construido — de forma que el propósito de un cambio se entiende leyendo solo la primera línea del mensaje, sin necesidad de abrir el diferencial.

En cuanto a ramas: el desarrollo ocurrió mayoritariamente sobre una única rama principal, `master`, con confirmaciones directas y frecuentes — una estrategia adecuada al tamaño del equipo (un desarrollador) y al ritmo de la entrega, que no justificaba la sobrecarga de un flujo de ramas por funcionalidad. La única excepción fue una rama secundaria, `identidad-visual`, abierta y fusionada de vuelta a `master` el 15 de agosto, usada para aislar el trabajo del sistema de diseño (paleta, tipografía y modo oscuro) mientras se definía, antes de integrarlo al resto del código.

## Estadísticas del historial

A la fecha de este anexo, el repositorio registra:

- **110 confirmaciones** en total.
- Primera confirmación: **9 de agosto de 2026**, a las 12:29 (`crea proyecto Django con estructura por capas y modelo de datos inicial`).
- Última confirmación: **27 de agosto de 2026**, a las 23:39 (`rediseña la portada como landing page profesional`).
- **251 archivos** bajo control de versiones.

## Evolución por jornadas

La tabla siguiente cubre cada día con actividad registrada en el historial, desde el inicio del proyecto hasta la fecha de este anexo. Los días sin fila no tuvieron confirmaciones — no representan una interrupción del trabajo en todos los casos, sino que en algunos tramos el avance de una jornada se integró al repositorio como parte de la confirmación del día siguiente.

| Fecha | Confirmaciones | Qué se construyó |
| --- | --- | --- |
| 9 de agosto | 1 | Arranque del proyecto: estructura Django en capas y modelo de datos inicial de las cuatro entidades del dominio. |
| 14 de agosto | 6 | Cierre funcional del MVP — lógica de negocio de registro, curaduría y catálogo — junto con el sistema visual completo, modo oscuro, accesibilidad, configuración de URLs raíz, service worker, datos de ejemplo y la documentación técnica y de identidad visual. |
| 15 de agosto | 30 | Jornada más extensa del proyecto: rediseño de las cinco áreas de la aplicación sobre el sistema de diseño nuevo, tres extensiones fuera del MVP original por pedido explícito (historial de aportes propios, panel de administrador, portada tipo abrebocas), selector de idioma español/inglés, mapa de distribución interactivo hecho a mano, y dockerización del proyecto. |
| 16 de agosto | 20 | Primera versión de la app móvil nativa (Expo), con su propia API mínima en el backend, y ajustes al mapa de distribución para que funcione con conexión intermitente. |
| 20 de agosto | 3 | Preparación de la app móvil para generar un instalable real (EAS Build) y migración de Tailwind CSS de un CDN en vivo a un build compilado, más estable para el usuario final. |
| 21 de agosto | 2 | Identidad visual propia para tarjetas de especie, portada y autenticación. |
| 22 de agosto | 18 | Jornada más grande en funcionalidad: portada reformulada, lista pública de avistamientos y ranking de observadores, traducción completa al inglés, y los últimos requisitos funcionales pendientes del MVP original (ayuda de la comunidad para identificar avistamientos, álbum de fotos por especie, nombre común propuesto desde el registro), además de racha de aportes, insignias, exportación a CSV y estadísticas del inventario por región. |
| 23 de agosto | 6 | Pulido de la navegación y de la app móvil: reorganización de menús, corrección del mapa y del selector de especies en el cliente móvil. |
| 26 de agosto | 4 | Corrección de dos hallazgos de seguridad (validación de fotos subidas y una clave de aplicación insegura que podía llegar a producción), búsqueda avanzada del catálogo, perfil público de observador y almacenamiento seguro de las credenciales de acceso de la app móvil. |
| 27 de agosto | 20 | Última jornada registrada: configuración del inicio de sesión con Google, rediseño de la portada como landing page (fondo fotográfico fijo, animación de marca, layout distribuido en columnas) y una serie extensa de correcciones a la barra de navegación superior hasta resolver su causa raíz. |

## Correspondencia entre versiones del software y del documento

El repositorio **no usa etiquetas de versión** (`git tag`) — las 110 confirmaciones forman una única línea de tiempo continua sin puntos de referencia nombrados, lo cual dificulta correlacionar una versión concreta del software con una versión concreta del documento académico. Se propone, de cara a las entregas restantes, adoptar un esquema simple de etiquetas `entregaN` (por ejemplo `entrega-18-08-2026` para la versión presentada el 18 de agosto) colocadas sobre la confirmación exacta que se entregó, de forma que este anexo — y cualquier futura revisión — pueda apuntar a una versión inmutable y verificable del código en lugar de a una fecha aproximada.

## Estructura del proyecto

El árbol de directorios, hasta dos niveles:

```
07_Codigo_Fuente/
├── apps/                  # las cuatro (más una) aplicaciones Django del dominio
│   ├── cuentas/           # Usuario, roles y autenticación
│   ├── catalogo/          # Especie y NombreComun — la Capa 1 (ficha curada)
│   ├── registros/         # Registro y Fotografia — la Capa 2 (avistamientos)
│   ├── curaduria/         # Revision y el flujo de aprobación
│   └── api_movil/         # API mínima de solo lectura/escritura para la app móvil
├── config/                # configuración de Django: settings por entorno, URLs raíz
├── templates/             # plantillas HTML, organizadas por aplicación
│   ├── catalogo/
│   ├── cuentas/
│   ├── curaduria/
│   └── registros/
├── static/                # CSS compilado, JavaScript, imágenes de marca
├── locale/                # traducciones español / inglés
├── docs/                  # el paquete de documentación del proyecto (este anexo incluido)
├── app_movil/             # la app móvil nativa (Expo/React Native), proyecto aparte
├── datos_ejemplo/         # fixtures para poblar una base de datos de prueba
├── respaldos/             # copias de resguardo de la base de datos
├── Dockerfile / docker-compose.yml / entrypoint.sh   # empaquetado para despliegue
└── manage.py              # punto de entrada de Django
```

Cada aplicación bajo `apps/` corresponde a una parte concreta del modelo de dos capas del proyecto (`CLAUDE.md`, apartado 2): `cuentas` resuelve quién puede aportar y con qué rol; `catalogo` sostiene la ficha curada de cada especie; `registros` recibe los avistamientos individuales de la comunidad; `curaduria` es el filtro por el que un avistamiento pasa antes de publicarse; y `api_movil`, añadida después del MVP original, expone ese mismo backend a la app móvil sin duplicar su lógica de negocio.
