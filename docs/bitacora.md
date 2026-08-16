# Bitácora técnica

> Registro interno de avances. Complementa a `docs/requisitos-mvp.md` (qué había
> que construir) contando **qué se construyó, en qué orden y por qué** —
> pensado para el equipo, no para una entrega formal. Cada entrada resume una
> sesión o un bloque de trabajo, no cada commit; el historial completo con
> mensajes en español está en `git log`.

---

## 9 de agosto — arranque del proyecto

Estructura del proyecto Django en capas (`config/` + cuatro apps: `cuentas`,
`catalogo`, `registros`, `curaduria`), modelo de datos inicial de las cuatro
entidades del dominio (Usuario, Especie/NombreComun, Registro/Fotografia,
Revision) y primeras migraciones. Se fija desde el inicio la convención que
gobierna todo el código: modelos solo definen estructura, la lógica de negocio
vive en `services.py`, las consultas complejas en `repositories.py` — nunca en
vistas ni modelos.

## 9–14 de agosto — el MVP funcional

Sprint 1 y 2 completos: autenticación y roles (RF-09, RF-10, RF-27), CRUD de
fichas de especie restringido a Revisor/Administrador (RF-13, RF-14, RF-16,
RF-17), registro de avistamientos con compresión de fotos (RF-01, RF-02,
RF-11, RF-15), flujo de curaduría completo con motivo obligatorio al devolver
(RF-06, RF-07, RF-08), catálogo público con búsqueda por nombre científico y
común, ficha detallada e inventario consolidado (RF-03, RF-04, RF-05, RF-26,
RF-28), importador de especies desde CSV (RF-14) y guardado local con envío
diferido para registrar avistamientos sin conexión (RF-23). Se escriben las
pruebas mínimas no negociables (transiciones de estado, que nada no aprobado
se publique, que las vistas públicas no filtren datos personales ni
coordenadas) y la documentación técnica (`docs/arquitectura.md`,
`docs/modelo-datos.md`, `docs/reglas-negocio.md`, `docs/manual-uso.md`).

**Con esto, los 20 requisitos funcionales y los 11 no funcionales del MVP
(`docs/requisitos-mvp.md`) quedan implementados.** El resto del tiempo se
invierte en identidad visual, pulido y extensiones pedidas explícitamente
fuera de ese alcance.

## 14 de agosto — identidad de marca

Guía de identidad visual completa (`docs/identidad-visual.md`): paleta de
marca con variables CSS para tema claro y oscuro, tipografía, componentes
clave (barra, tarjetas, botones, estados). Cambio de nombre del proyecto de
«Avisté» a **Ojo Avizor**, con el símbolo del ojo con pupila en forma de ave
reemplazando el logo anterior (bird-on-ellipse). Condiciones de uso (RN-07).

## 15 de agosto — rediseño, modo oscuro y funciones nuevas

Día más largo de trabajo continuo. En orden aproximado:

- **Modo oscuro obligatorio** montado sobre `base.html`: paletas por
  `data-tema`, script anti-parpadeo en el `<head>`, barra e íconos propios
  (se retiran los emoji del sitio completo).
- **Rediseño de las cinco áreas de la aplicación** (cuentas, catálogo público,
  gestión de fichas, registros, curaduría) sobre el sistema de diseño nuevo,
  con HTMX para la búsqueda en vivo y micro-interacciones (skeleton loaders,
  animaciones de entrada, botón «volver arriba»).
- **Estados de marca**: páginas 404/500 propias, estados vacíos con mensaje
  cálido, meta tags Open Graph, pantalla de confirmación al registrar un
  avistamiento.
- **Tres extensiones fuera del MVP original, construidas por pedido explícito
  del usuario** pese a estar en la lista de exclusiones de
  `docs/requisitos-mvp.md`:
  - Página **«Mi cuenta»** con estadísticas de aportes propios (roza RF-12).
  - **Panel de administrador** con gestión de usuarios y cifras de uso (roza
    RF-25).
  - **Portada tipo abrebocas** (inspirada en eBird), separada del catálogo,
    con estadísticas, familias y actividad reciente.
- **Selector de idioma ES/EN** junto al de tema, con traducción completa de
  cadenas de plantilla, formularios y `TextChoices` de los modelos (un mismo
  texto en español puede vivir en tres lugares distintos — plantilla,
  `forms.py`, `models.py` — y hay que envolver los tres en `gettext`, o la
  traducción queda incompleta a medias sin que sea obvio).
- **Mapa de distribución interactivo** (RF-22, también fuera del MVP
  original): reemplaza el campo de texto libre por un mapa mundial que
  colorea los países de distribución de cada especie, con zoom y arrastre
  hechos a mano (sin librería de mapas ni tiles, para no romper RNF-01/02).
  Decisión de diseño no trivial: el SVG base (dominio público, Wikimedia
  Commons) pesaba 1 MB; se optimizó a ~480 KB redondeando coordenadas y
  quitando metadatos de editor, y se limitó la lista de países seleccionables
  a América y el Caribe (el alcance geográfico real de las aves que registra
  la plataforma) en vez de las 195 naciones ISO completas.
- **Logos institucionales** (Universidad Alexander von Humboldt, Fundación
  Smurfit Westrock Colombia) en el pie de página, sustituyendo el texto
  placeholder.
- **Profundidad visual de la barra superior**: subrayado cian en la pestaña
  activa (ya estaba especificado en la guía de identidad visual, nunca se
  había construido), sombra que crece al hacer scroll, brillo sutil —
  siempre dentro de las restricciones propias de la guía (sin degradados
  marcados, sombras fuertes ni animaciones llamativas).

## 15 de agosto (noche) — dockerización

`Dockerfile` (Python 3.12-slim, gunicorn + WhiteNoise para servir estáticos
sin depender de nginx), `docker-compose.yml` para desarrollo local (Postgres
+ la app con el código montado y recarga automática) y `entrypoint.sh` que
espera a que la base de datos acepte conexiones antes de migrar. Ver la
sección «Ejecutar con Docker» del `README.md` para los comandos.

---

## Dónde queda el proyecto

El MVP completo (20 RF + 11 RNF) está construido y probado. Las extensiones
por pedido explícito (mapa de distribución, historial de aportes, panel de
administración, selector de idioma) también. Lo que sigue pendiente, mirando
`docs/requisitos-mvp.md`, es exactamente lo que ese documento marca como
**fuera de alcance de esta entrega** y no se ha tocado: RF-18, RF-19/RF-29,
RF-20, RF-21, RF-24, RNF-12. No están a medias — deliberadamente no se
empezaron.
