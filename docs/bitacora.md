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

## 15–16 de agosto (noche) — dockerización

`Dockerfile` (Python 3.12-slim, gunicorn + WhiteNoise para servir estáticos
sin depender de nginx), `docker-compose.yml` para desarrollo local (Postgres
+ la app con el código montado y recarga automática) y `entrypoint.sh` que
espera a que la base de datos acepte conexiones antes de migrar. Ver la
sección «Ejecutar con Docker» del `README.md` para los comandos.

Verificado de punta a punta con `docker compose up`: migraciones aplicadas
automáticamente, servidor respondiendo, estáticos (incluido el mapa mundial
del apartado anterior) servidos correctamente, y la suite de pruebas
completa en verde corriendo dentro del contenedor. Docker Desktop tardó
casi una hora en levantar el daemon en este entorno — una vez arriba, todo
funcionó a la primera sin ajustes.

---

## 16 de agosto — primera versión de la app móvil nativa

App aparte del sitio web (`app_movil/`, Expo/React Native), pedida por el
usuario para que el observador registre avistamientos en campo sin depender
del navegador — mismo principio que el guardado sin conexión de RF-23, pero
como app instalable. Backend nuevo y 100% aditivo (`apps/api_movil/`): login
por token, catálogo de especies, crear registro con fotos, listar los
propios. Sin Django REST Framework — se evaluó de nuevo y se descartó,
cuatro vistas planas con `JsonResponse` bastan, coherente con la regla ya
establecida del proyecto de no añadirlo sin justificación real. Se agrega
mapa, fecha, descarga de catálogo, marca e íconos propios a la app; se baja
de versión de Expo SDK por incompatibilidad; Leaflet se sirve localmente
(no CDN) para que el mapa funcione con conexión intermitente en campo.

## 20 de agosto — Tailwind compilado y preparación del APK

El CDN de Tailwind se rompía en el navegador del usuario final ("Expected an
opening parenthesis"), sin generar ninguna clase de utilidad — layout e
íconos quedaban sin tamaño ni posición. Se reemplaza por un build compilado
(`npm run build:css`, commiteado, ver README.md), que no depende de que ese
motor corra en cada visita. Se unifica el sistema de color y se corrige
contraste siguiendo `docs/identidad-visual.md`. Se prepara `eas.json`/
`app.json` (paquete Android, project ID) para generar un APK instalable de
verdad con EAS Build, no solo la app de desarrollo Expo Go.

## 21–22 de agosto — rediseño grande y los últimos RF pendientes del MVP

Bloque de trabajo más grande del proyecto hasta ahora:

- Identidad propia para tarjetas de especie, portada y autenticación;
  unificación del sistema de profundidad (sombras) y limpieza del CSS
  muerto que quedó de la migración del CDN.
- Portada reformulada con hero asimétrico, ficha real de especie y
  explicación del proyecto (versión previa a la de foto fija del 27 de
  agosto — ver más abajo).
- Lista pública de avistamientos y ranking de observadores; traducción
  completa al inglés de todo lo nuevo.
- Tipografía Lora autoalojada (no CDN) y animaciones de aparición al hacer
  scroll (`data-reveal` + `IntersectionObserver`, con salvedad si el
  navegador no la soporta y respeto a `prefers-reduced-motion`).
- **RF-19/RF-29** (ayuda de la comunidad para identificar avistamientos),
  **RF-21** (álbum de fotos por especie) y **RF-18** (nombre común propuesto
  desde el formulario de registro, con aviso resumido para el revisor):
  quedaban marcados como fuera de alcance de esta entrega en
  `docs/requisitos-mvp.md` — se implementan aquí, ya no están pendientes.
- Racha de días seguidos registrando, iterada varias veces en el mismo
  bloque hasta la versión actual (llama que se muestra siempre, apagada en
  gris en cero, con pulso cuando está viva). Insignias por hitos y
  exportación del inventario en CSV.
- Corrección de países sin colorear en el mapa de distribución (RF-22).
  Actividad por departamento y municipio de Colombia añadida al inventario
  consolidado. El menú había quedado sin ningún enlace a "Inventario" — se
  corrige. Racha y nombre común propuesto se replican en la app móvil.

## 23 de agosto — pulido de navegación y de la app móvil

Reorganización de la barra de navegación y corrección del selector de
especies en móvil; ajuste del punto de quiebre responsive de la barra
superior para que no se rompiera. Regla nueva: pedir ayuda a identificar un
avistamiento exige descripción o foto, no se puede pedir sin nada.
Corrección del mapa de la app móvil, que no se podía arrastrar; de un
mensaje que le echaba la culpa a "sin conexión" cuando el catálogo fallaba
por otra razón; y de una migración faltante de `especies_cache` en la app
móvil.

## 26 de agosto — seguridad y funcionalidad avanzada del catálogo

**Dos hallazgos de seguridad corregidos por pedido explícito del usuario**:
fotos subidas sin validar tamaño ni formato (ahora valida un máximo de
10 MB y atrapa imágenes corruptas o bombas de descompresión), y
`SECRET_KEY` de producción que podía quedar silenciosamente en el valor
inseguro de desarrollo (`config/settings/produccion.py` ahora falla fuerte
si detecta ese valor por defecto en vez de arrancar igual).

Búsqueda avanzada del catálogo (filtros combinables de familia, orden,
tamaño y texto), ficha de especie enriquecida (especies similares, sidebar
de datos rápidos), perfil público de observador — con privacidad por
defecto: si no tiene ningún avistamiento aprobado, la página no existe
públicamente, para no exponer un perfil vacío — y panel de estadísticas del
inventario (tendencia mensual de avistamientos).

Los tokens de acceso de la app móvil se guardaban en texto plano en la base
de datos, deuda técnica deliberada ya anotada en su momento — se corrige
guardándolos como hash SHA-256, con una migración de datos que convierte
los tokens existentes sin romper ninguna sesión activa. Fotos duplicadas en
la galería de una especie (mismo archivo subido dos veces) se deduplican
por hash de contenido, no por nombre de archivo. El filtro de tamaño del
catálogo quedaba con un valor inválido para el campo numérico al recargar
la página — Django renderizaba el número con coma decimal de configuración
regional española (`"15,0"`), que el HTML rechaza; se separa el valor de
texto para mostrar del valor numérico para la consulta.

## 27 de agosto — portada con foto propia, Google OAuth y la barra superior

La portada (hero asimétrico del 21-22) se reemplaza por una foto fija: un
paisaje de nevado de los Andes, foto propia del usuario (no de internet),
comprimida siguiendo el mismo patrón de compresión ya usado en el proyecto.
Se restauran los degradados y blobs decorativos del `.hero` que se habían
quitado por violar la sección "qué evitar" de `docs/identidad-visual.md` —
el usuario pidió explícitamente conservarlos, así que queda documentado
como excepción permanente dentro de esa misma guía para que no se
"corrija" de nuevo por error en una sesión futura. Ficha de especie e
inventario pasan de una columna apilada a un layout en dos columnas desde
`lg`. Animación de intro de marca en la portada (isotipo que aparece y se
retira antes de mostrar la página), inspirada en la animación de bienvenida
de iconicoterraza.co, ajustada para reproducirse en cada carga y respetando
`prefers-reduced-motion`.

**Login con Google (django-allauth) terminado de configurar**: faltaba la
dependencia `PyJWT`, necesaria para que el proveedor OIDC de Google
verifique el `id_token` (no viene como dependencia obligada de la versión
de allauth usada). Credenciales de Google Cloud Console en `.env`, nunca
commiteadas — configurar esto es gratis, con la limitación de "modo de
prueba" hasta publicar la app. Confirmado funcionando en vivo; solo prueba
con `localhost`, no con `127.0.0.1` (son orígenes distintos para el
redirect de OAuth — limitación de cómo se prueba en desarrollo, no un bug).

**Saga de depuración de la barra superior** (se esconde al bajar el scroll,
reaparece al subir o al acercar el cursor): pasó por seis rondas de
corrección antes de dar con la causa real, vale la pena registrarla
completa porque fue un proceso de diagnóstico real, no una sola corrección.
1. Primer intento con `requestAnimationFrame` dentro del `x-init` de
   Alpine — se reemplaza porque un navegador puede dejar de invocarlo si la
   pestaña no está pintando activamente, dejando la barra congelada.
2. Se quedaba pegada sin reaccionar cerca del final de la página: el punto
   de referencia de comparación se reescribía en cada evento de scroll en
   vez de solo cuando la barra cambiaba de estado, así que una serie de
   pasos de scroll chiquitos (típico al frenar el impulso) nunca acumulaba
   lo suficiente para cruzar el margen de tolerancia.
3. Por pedido explícito del usuario se quita un caso especial que dejaba la
   barra siempre visible cerca del extremo superior del scroll — esa
   excepción era justo la que hacía que acercar el cursor "no hiciera nada"
   ahí, porque ya estaba forzada visible.
4. El usuario reportó que seguía sin funcionar. Se diagnosticó en vivo,
   pidiéndole que corriera fragmentos de JavaScript en la consola de su
   propio navegador y reportara los resultados — el estado reactivo de
   Alpine (`barraOculta`) cambiaba perfecto en cada prueba, sin fallar una
   sola vez, tanto con scroll como con el cursor.
5. Como la única parte de la cadena sin confirmar era si la clase CSS de
   escondido realmente se aplicaba y ganaba en el navegador del usuario, se
   cambia de clase CSS compilada a estilo en línea vía Alpine (`:style`) —
   un estilo en línea gana siempre sobre cualquier regla de hoja de
   estilos, sin depender de en qué capa cae la clase ni de si el CSS
   compilado está al día en quien prueba.
6. Seguía sin funcionar. **Causa real**: `.barra-superior` tenía
   `position: relative` declarado en el `<style>` de `base.html` (agregado
   para posicionar los pseudo-elementos decorativos `::before`/`::after`),
   con la misma especificidad que la utilidad `sticky` de Tailwind ya
   puesta en el HTML del header — y como esa regla aparecía después en la
   cascada, ganaba y pisaba a `sticky` sin que nada lo avisara. La barra
   nunca estuvo pegada arriba de la pantalla: al hacer scroll se iba con el
   resto de la página como cualquier elemento normal, así que no importaba
   qué tan bien funcionara el estado de Alpine — no había nada que revelar.
   Se quita `position: relative` (sticky ya sirve de referencia para los
   pseudo-elementos) y queda confirmado con medición directa de posición:
   antes, "revelada" quedaba a cientos de píxeles fuera de la pantalla;
   ahora queda exactamente en el borde superior, visible.

La lección de fondo: un bug de posicionamiento CSS puede hacer que una
lógica de estado 100% correcta sea completamente invisible — diagnosticarlo
tomó pedirle al usuario que ejecutara pruebas paso a paso en su propia
consola, porque las herramientas de navegador automatizadas disponibles no
podían confirmar el resultado visual final por sí solas.

## 31 de agosto — buscador de especie tipo eBird, cantidad de individuos y códigos reproductivos

Tres extensiones nuevas al formulario de registro, todas fuera del MVP original, pedidas explícitamente por el usuario:

- **Buscador de especie con autocompletar** (reemplaza el desplegable de lista completa): HTMX pide sugerencias a medida que se escribe, filtrando por nombre científico y por nombres comunes — coherente con el modelo de dos capas del proyecto, donde la gente reconoce el ave por como le dicen en la vereda, no por su nombre en latín. Cada sugerencia muestra ambos nombres.
- **Cantidad de individuos** (`Registro.cantidad_individuos`), obligatoria en el formulario web al estilo eBird.
- **Código reproductivo**: al principio se dejó marcar varios a la vez (`JSONField`, lista, con chips tipo casilla). El 1 de septiembre se corrigió: la guía oficial de eBird es explícita — *"choose the highest-ranking code that you observed for that species on this checklist"* (verificado contra su Help Center) — nunca se combinan códigos, siempre se reporta uno solo, el de mayor jerarquía. El campo pasa a `CharField` de un solo valor y los chips a un grupo de radios (selección única, se auto-excluyen).

En el camino se encontraron y corrigieron varios bugs reales de Alpine.js e HTMX, vale la pena dejarlos anotados porque no fueron obvios:

- Un método definido dentro de `x-data` necesita `this.` para tocar sus propias propiedades (`this.consulta`, no `consulta` a secas) — sin el prefijo, el cambio nunca se reflejaba en pantalla, aunque `$refs` sí funcionaba sin `this.` (es "mágico", se inyecta distinto). El id oculto de la especie elegida quedaba bien puesto, pero el texto visible del buscador se quedaba pegado en lo que se había escrito.
- Dos disparadores de HTMX en el mismo campo (`input` y `focus`) rompían el `delay:300ms` del debounce: cada tecla mandaba su propia petición al toque, más una petición vacía de más — confirmado revisando la red real, no adivinando. Se resolvió a un solo disparador.
- El panel de sugerencias no se cerraba al perder el foco de otra forma que no fuera un clic afuera (con Tab, por ejemplo, se quedaba abierto) — se agrega cierre por `@blur`.
- Tocar una sugerencia en pantallas táctiles (el público real del proyecto) le quitaba el foco al campo *antes* de que el clic terminara de procesarse, perdiendo la selección casi siempre — se corrige con `@mousedown.prevent` en vez de competir contra un `setTimeout`.
- El panel debía aparecer también con la primera tecla, no solo al enfocar el campo: Alpine carga con `defer`, y en un celular lento el campo puede ya aceptar toques antes de que Alpine termine de engancharse — si el toque cae justo ahí, el evento de foco no lo escucha nadie.

Causa raíz aparte, encontrada revisando por qué varios cambios de CSS/JS "no se veían" pese a estar bien hechos: `runserver` no manda ninguna instrucción de caché al servir estáticos, así que el navegador podía reusar una copia vieja de `tailwind.css` incluso en una recarga normal. Se probó arreglarlo con un middleware, pero el manejo automático de estáticos de `runserver` intercepta la petición antes de que llegue a cualquier middleware — no funciona. La solución real: un tag de plantilla propio (`{% estatico_v %}`, `apps/catalogo/templatetags/estaticos.py`) le agrega la fecha de modificación del archivo a la URL, así que un cambio de contenido siempre es una URL nueva y fuerza a pedirlo de nuevo.

## 1 de septiembre — investigación de despliegue y preparación para AWS

Con el MVP y las extensiones ya construidas, tocaba decidir dónde publicar la plataforma. Se investigaron seis rutas (Render, un VPS auto-administrado, Railway, Fly.io, PythonAnywhere, y separar la base de datos en un servicio administrado aparte), comparando costo, cuánto mantenimiento humano exige cada una después de que termine la práctica, y qué tan predecible es la factura para pedirle un número concreto a la Fundación. Se recomendó Render como opción principal (sin servidor que mantener) y un VPS propio como alternativa más barata — documentado en un artefacto aparte para presentarle a la Fundación, con presupuesto anual estimado (~US$220 con Render, ~US$92 con VPS) y una nota sobre Google for Nonprofits como recurso adicional a tramitar (Colombia y las fundaciones califican; el crédito específico de Google Cloud para hosting no se pudo confirmar fuera de EE. UU., así que no se dio por hecho).

Ese mismo día cambió el panorama: aparecieron créditos de AWS de la cuenta institucional del usuario, vigentes hasta el **13 de septiembre**. Se preparó el despliegue en consecuencia — mismo principio de "todo en un servidor" ya evaluado (nada de escalado ni base de datos administrada aparte, no hace falta con 10 usuarios simultáneos), pero sobre **AWS Lightsail** en vez de DigitalOcean, aprovechando que ya existía un `Dockerfile` construido y verificado de punta a punta desde el 15-16 de agosto: nada de instalar Gunicorn/Nginx/PostgreSQL a mano, la misma imagen que ya corre en desarrollo.

Se agregan `docker-compose.prod.yml` (Postgres + la imagen existente + Caddy) y `Caddyfile`. La decisión no trivial fue Caddy en vez de Nginx + certbot: consigue y renueva el certificado HTTPS de Let's Encrypt solo, sin una tarea programada que alguien tenga que acordarse de mantener — importante porque después de la práctica no va a quedar nadie de guardia. `docker compose config` valida la sintaxis correctamente; el build completo de la imagen no se pudo confirmar en esta máquina porque el daemon de Docker Desktop no estaba corriendo (arrancarlo tarda cerca de una hora acá, según quedó anotado en la entrada del 15-16 de agosto) — no se justificaba la espera dado el plazo, y el `Dockerfile` no cambió desde la última vez que sí se verificó completo. Se documenta el paso a paso completo en `README.md`, sección "Despliegue en producción (AWS Lightsail)": crear la instancia, IP estática, apuntar el dominio, variables de entorno de producción (incluida la advertencia de agregar el dominio nuevo a las credenciales de Google OAuth, o el login con Google funciona en desarrollo pero falla en producción), y cron en el servidor para los comandos de respaldo y aviso a revisores que ya existían pero nunca se habían programado fuera de desarrollo.

**Queda pendiente, no se puede hacer desde acá**: ningún paso de la consola de AWS (crear la instancia, la IP estática, elegir/registrar el dominio) se puede ejecutar sin las credenciales de la cuenta — eso lo tiene que hacer el usuario siguiendo la guía. Tampoco está confirmado si el registro de dominio en Route 53 queda cubierto por los créditos de cómputo o es un cargo aparte, ni qué pasa con el servidor si los créditos vencen el 13 de septiembre sin haberse renovado — ambas cosas quedaron anotadas en el README para confirmar antes de esa fecha.

---

## Dónde queda el proyecto

El MVP completo (20 RF + 11 RNF) está construido y probado. Las extensiones
por pedido explícito (mapa de distribución, historial de aportes, panel de
administración, selector de idioma, app móvil nativa, búsqueda avanzada,
perfil de observador, estadísticas del inventario, login con Google)
también. De la lista que este documento marcaba como **fuera de alcance de
la entrega original**, RF-19/RF-29, RF-21 y RF-18 ya se construyeron (ver
21-22 de agosto); sigue sin tocarse, deliberadamente, el resto: RF-20,
RF-24, RNF-12.

Al 27 de agosto no había evidencia en el repositorio de un despliegue en un
lugar público y accesible. Eso cambió el 1 de septiembre: preparación
completa para desplegar en AWS Lightsail con créditos institucionales
(`docker-compose.prod.yml`, `Caddyfile`, guía paso a paso en `README.md`) —
ver la entrada de esa fecha para el detalle y lo que sigue pendiente
(ejecutar los pasos en la consola de AWS, algo que solo puede hacer quien
tiene las credenciales de la cuenta).
