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

## 4 de septiembre — los créditos de AWS no quedaron disponibles: despliegue gratuito

Los créditos institucionales de AWS de la entrada anterior finalmente no se pudieron usar. Se preparó una ruta alternativa con **cero costo real**, pedida explícitamente así — sin tarjeta de por medio en la medida de lo posible.

Ningún proveedor gratis resuelve todo el stack (app + base de datos + almacenamiento de archivos) de forma confiable en un solo lugar, así que la solución queda repartida en tres servicios: **Render** (corre Django, plan gratis — se duerme a los 15 minutos sin visitas), **Neon** (PostgreSQL, plan gratis permanente — a diferencia del propio Postgres gratis de Render, que se borra a los 30 días) y almacenamiento de archivos aparte para las fotos de avistamientos. Esta última pieza fue la decisión menos obvia: el disco del contenedor de Render **no es persistente** — cualquier foto guardada ahí se perdería en el siguiente reinicio o despliegue. Se investigaron alternativas para la base de datos y el archivo antes de decidir (Supabase se descartó para la base de datos: su Postgres gratis se pausa a los 7 días sin uso y hay que reactivarlo a mano, peor que el de Neon, que se reactiva solo; Oracle Cloud "Always Free" también, porque desde este año pide tarjeta de crédito de verificación a casi todo el mundo, justo lo que se quería evitar).

Para el almacenamiento de fotos, la primera elección fue **Cloudflare R2** — pero resultó ser la única de las tres piezas que pide una tarjeta para activarse (no cobra dentro de los 10 GB gratis, pero la pide igual). Pedido explícito del usuario de evitarlo: se cambió a **Backblaze B2**, mismo tamaño gratis (10 GB) y compatible con la misma API de S3 — el cambio de código fue solo de credenciales y nombres de variables (`R2_*` → `B2_*`), no de mecanismo.

La investigación decía que B2 no pide tarjeta en ningún caso; probándolo de verdad, el usuario encontró que **sí la pide, igual que R2, en el momento de hacer un bucket Público** — no al crear la cuenta ni al usarlo privado. Corrección sobre la marcha: el bucket queda **Privado** (así nunca pide tarjeta), y en vez de un dominio público fijo para las fotos, Django arma una URL firmada distinta cada vez que arma la página (`querystring_auth=True`, vencimiento de 7 días — el máximo que permite el esquema de firma de S3, y de sobra: como la URL se genera de nuevo en cada visita, ese vencimiento nunca llega a notarse desde el sitio). Vale la pena la anotación: la documentación pública de un servicio no siempre coincide con el comportamiento real al usarlo, y esta vez lo confirmó quien lo estaba probando en su propia cuenta, no una búsqueda.

Cambios de código para que esto funcione, todos condicionales — el despliegue con Docker/VPS de la entrada anterior sigue funcionando exactamente igual, sin tocar nada:

- `config/settings/produccion.py`: si hay credenciales de Backblaze B2 en el entorno, las fotos se guardan ahí (`django-storages`, backend S3 — B2 es compatible con la API de S3); si no las hay, sigue siendo disco local como hasta ahora.
- `config/settings/base.py`: `DATABASES` acepta un `DB_SSLMODE` opcional — Neon exige TLS para conectarse, el Postgres de Docker no.
- `Dockerfile`: el `CMD` de gunicorn pasa de forma exec a forma shell para poder leer `${PORT:-8000}` en tiempo de arranque — Render le asigna el puerto real al contenedor por una variable de entorno que no siempre es 8000; sin este cambio, el despliegue en Render fallaría en silencio.
- `entrypoint.sh`: crea un superusuario solo al arrancar si están puestas las variables `DJANGO_SUPERUSER_*` — Render, en el plan gratis, puede no dar una terminal para correr `createsuperuser` a mano como sí se puede con `docker compose exec` en el despliegue con Docker/VPS.

Guía completa en `README.md`, sección "Despliegue gratuito (Render + Neon + Backblaze B2)" — misma estructura que la de AWS, que se deja documentada y en pausa (no se borra: sirve tal cual el día que haya presupuesto o créditos de nuevo, sección marcada como tal). `manage.py check` se corrió con y sin las variables de B2 puestas, para confirmar que las dos ramas del `STORAGES` condicional cargan bien.

## 4 de septiembre (continuación) — el despliegue gratuito queda en vivo

Misma jornada, segundo bloque: se ejecutó de punta a punta lo que la entrada
anterior dejó preparado. El sitio queda publicado en
`https://ojo-avizor.onrender.com`, verificado en vivo con navegador real, no
solo con `manage.py check`.

**Neon.** El usuario pegó la cadena de conexión real de su proyecto. Traía un
parámetro nuevo, `channel_binding=require`, junto al ya conocido
`sslmode=require`, que `config/settings/base.py` todavía no contemplaba —
`DATABASES` solo sabía leer `DB_SSLMODE`. Se agrega `DB_CHANNEL_BINDING` con
el mismo patrón condicional. Verificado no solo con `manage.py check`, sino
con una conexión real contra la base de Neon del usuario (`SELECT version()`)
antes de dar por buena la corrección — la única forma de confirmar que
psycopg2 realmente acepta ese parámetro de SCRAM channel binding sin error,
en vez de asumirlo.

**Decisión del usuario: el entorno local deja de ser local.** Pidió
explícitamente que su `.env` de desarrollo apuntara a los mismos servicios
reales del despliegue (Neon, Backblaze B2, Gmail) en vez de a un Postgres y
un disco local — "que quede todo desplegado, nada en local". Esto tiene un
efecto en cadena que no es obvio: el almacenamiento de fotos en Backblaze B2
solo se activa en `config/settings/produccion.py`, no en `desarrollo.py`, así
que tener las credenciales de B2 en el `.env` no alcanza — hubo que cambiar
también `DJANGO_SETTINGS_MODULE` a `produccion` en local. Eso arrastra
`SECURE_SSL_REDIRECT=True` por defecto, que en un `runserver` sin HTTPS deja
`http://localhost:8000` en loop de redirección; se fija
`DJANGO_SECURE_SSL_REDIRECT=False` solo en el `.env` local para evitarlo, sin
tocar el valor real que usa Render. También exige correr `collectstatic` a
mano en local (WhiteNoise necesita el manifiesto, y con `DEBUG=False` el
`runserver` ya no sirve estáticos solo). Verificado sirviendo el sitio local
con estas condiciones antes de seguir.

**Cuenta de administrador.** Se creó el superusuario en Neon
(`createsuperuser --noinput`, único modo viable porque Render en el plan
gratis no siempre da una terminal). El campo `rol` propio del proyecto
(distinto de `is_staff`/`is_superuser`, que sí pone Django) quedó en
`OBSERVADOR` por defecto — `createsuperuser` no lo toca. Existe un servicio,
`cambiar_rol` (`apps/cuentas/services.py`), pero bloquea a propósito que
alguien se cambie el rol a sí mismo (pensado para el panel, donde un admin
cambia el rol de otra persona) — como esta era la primera cuenta del sistema,
no había quién más lo autorizara. Se asignó `ADMINISTRADOR` por asignación
directa del campo, mismo tipo de bootstrapping inicial que ya hace
`createsuperuser` con sus propios campos, no una vía nueva para saltarse la
regla en el uso normal del panel.

**Backblaze B2 y Gmail, credenciales reales.** Bucket `Ojo-Avizor` creado
Privado (confirma lo ya aprendido el mismo día: Público pide tarjeta,
Privado no). Para el correo saliente, generar la contraseña de aplicación de
Gmail tomó tres intentos — las dos primeras, copiadas a mano en el chat,
fallaron con `BadCredentials` contra el servidor SMTP real; la tercera, con
más cuidado al copiarla, funcionó. Se verificó con una autenticación SMTP
directa (`smtplib`, sin mandar ningún correo) antes de dar por buena la
contraseña, en vez de confiar en que el formato de 16 caracteres alcanzara.

**El build de Docker en Render fallaba — dos bugs reales, no de
configuración del usuario.** `collectstatic` corre durante la construcción
de la imagen, antes de que Render inyecte las variables de entorno del
dashboard. Desde la revisión de seguridad del 25 de agosto,
`produccion.py` exige una `DJANGO_SECRET_KEY` real y falla fuerte si no la
encuentra — nadie había ajustado el paso de build para tenerlo en cuenta, así
que el build fallaba siempre, sin importar qué tan bien configurado
estuviera Render. Se agrega una clave de marcador solo para ese paso del
`Dockerfile`; la real, la de Render, la pisa en tiempo de ejecución. Al
corregir eso, apareció un segundo problema: `leaflet.css`/`leaflet.js`
(vendorizados en `static/vendor/leaflet/`) referencian `layers.png`,
`layers-2x.png` y `leaflet.js.map` que nunca se habían copiado al
vendorizar la librería originalmente — invisibles en desarrollo porque
`runserver` no valida que esas referencias resuelvan a un archivo real, pero
WhiteNoise (`CompressedManifestStaticFilesStorage`) sí lo exige en el build.
Se agregan los tres archivos oficiales de Leaflet 1.9.4 (misma versión ya
vendorizada). Sin Docker Desktop disponible en esta máquina para probar el
build completo, se verificó el paso exacto que fallaba —`collectstatic` con
las mismas condiciones del build de Render (sin `.env`, sin base de datos,
solo la clave de marcador)— hasta confirmarlo limpio.

**Login con Google en el dominio nuevo.** Mismo patrón ya anotado el 27 de
agosto (el redirect de OAuth es específico por origen): hubo que agregar
`https://ojo-avizor.onrender.com/accounts/google/login/callback/` a los URI
de redirección autorizados en Google Cloud Console. El usuario reemplazó por
error el de `localhost` en vez de agregar el nuevo al lado — Google permite
varios URI en el mismo cliente OAuth, así que se repuso el de desarrollo
junto al de producción. Confirmado en vivo: el flujo llega hasta la pantalla
real de Google ("Ir a ojo-avizor.onrender.com") sin `redirect_uri_mismatch`.

**Las 399 fichas de especie no se habían perdido — nunca se habían
migrado.** El usuario notó que el catálogo en Neon estaba vacío pese a tener
399 fichas ya curadas. Estaban intactas en el Postgres local (nunca se tocó
ni se borró esa base al cambiar el `.env`, solo se dejó de apuntar ahí):
`migrate` sobre Neon crea el esquema, no copia datos. Se migraron con
`dumpdata`/`loaddata` (399 `Especie` + 399 `NombreComun`, más la cuenta de
prueba `obs.prueba@example.com` que figuraba como autora de todas, para no
perder esa referencia). En el camino, un bug de codificación propio de
Windows: `dumpdata --output archivo.json` escribió el archivo en `cp1252`
por defecto en vez de UTF-8, y `loaddata` rompía con `UnicodeDecodeError` en
cualquier nombre con tilde — se resolvió forzando `PYTHONUTF8=1` al volcar
de nuevo. Después de cargar con PK explícito, se corrió
`sqlsequencereset` sobre `catalogo` y `cuentas` para que el próximo usuario o
especie creados en Neon no choquen de ID con los recién importados.
Efecto colateral de probar la suite de pruebas completa con el `.env` ya
apuntando a Neon: al cortarla a mitad de camino quedó una base de datos de
prueba huérfana (`test_ojo_avizor`) en el proyecto real — Django la crea y
la borra sola si la corrida termina completa, pero interrumpida a mitad no
llegó a limpiarla. Se borró con confirmación explícita del usuario (acción
destructiva sobre un recurso real, no se hizo por cuenta propia). Queda
anotado como algo a tener presente de ahora en más: con el entorno local
apuntando a la base real, correr `manage.py test` sin querer tiene ese
costo — antes no lo tenía.

Verificado en vivo con navegador real, no solo con comandos: portada carga
con las 399 especies visibles, login por correo/contraseña funciona con
cookies seguras sobre HTTPS real, el panel de administrador confirma que el
rol quedó bien asignado, y el flujo de Google OAuth llega limpio hasta la
pantalla de consentimiento de Google.

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
lugar público y accesible. El 1 de septiembre se preparó uno completo sobre
AWS Lightsail con créditos institucionales, pero esos créditos finalmente no
quedaron disponibles — esa ruta se deja documentada y en pausa, no se
descarta.

**El despliegue gratuito con Render + Neon + Backblaze B2 ya está en vivo**,
no solo preparado: `https://ojo-avizor.onrender.com`, con las 399 fichas de
especie ya curadas, cuenta de administrador funcionando, login con Google
verificado en el dominio real y correo saliente por Gmail configurado. El 4
de septiembre queda registrado en dos entradas porque fue justo la frontera
entre "listo para ejecutar" y "ejecutado y confirmado en vivo": la primera
prepara el código y la investigación, la segunda corre cada paso contra los
servicios reales y corrige lo que solo se ve al hacerlo de verdad (el build
de Docker, la migración de datos, el redirect de OAuth). Sigue pendiente,
por la misma razón de siempre: cualquier ajuste futuro de dashboard de
terceros (Render, Neon, Google Cloud Console) le corresponde al usuario, con
las credenciales de sus propias cuentas.
