# Ojo Avizor

Plataforma web que consolida el inventario de avifauna del municipio de Pijao, Quindío, mediante el registro participativo de la comunidad. Proyecto de práctica empresarial de Ingeniería de Software, desarrollado con la Fundación Smurfit Westrock Colombia para el semillero de observación de aves *Semillas de La Cordillera*.

El contexto completo del proyecto (modelo de datos, reglas de negocio, requisitos del MVP y decisiones de arquitectura) está en [`CLAUDE.md`](CLAUDE.md) y en [`docs/`](docs/). Este archivo es la guía técnica para instalar, ejecutar y entender el código.

---

## Pila técnica

Python 3.12 · Django 5.2 · PostgreSQL · HTMX + Alpine.js · Tailwind CSS (vía CDN) · Pillow

## Estructura del proyecto

```
config/              # settings por entorno, urls raíz, wsgi/asgi
apps/
  cuentas/            # Usuario, roles, autenticación
  catalogo/           # Especie, NombreComun — ficha curada (Capa 1)
  registros/          # Registro, Fotografia — avistamientos (Capa 2)
  curaduria/          # Revision y flujo de revisión
templates/            # base.html + una carpeta por app
static/               # CSS/JS propios (js/registro-offline.js, sw.js)
locale/                # traducciones es / en
datos_ejemplo/         # CSV de muestra para el importador de especies
docs/                  # paquete de contexto del proyecto + manual de uso
```

Cada app sigue la misma arquitectura en capas: `models.py` (estructura y validación de campo) → `repositories.py` (consultas) → `services.py` (reglas de negocio y transiciones de estado) → `views.py`/`forms.py` (presentación). Los detalles están en [`docs/arquitectura.md`](docs/arquitectura.md).

---

## Instalación local

### 1. Requisitos previos

- Python 3.12
- PostgreSQL corriendo localmente (o accesible por red)

### 2. Entorno virtual y dependencias

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con los datos de tu base de datos PostgreSQL (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) y una `DJANGO_SECRET_KEY` propia. La base de datos y el usuario de PostgreSQL deben existir de antemano (créalos con `createdb` / `createuser`, o con pgAdmin).

### 4. Migraciones y superusuario

```bash
python manage.py migrate
python manage.py createsuperuser
```

El primer usuario que se cree con `createsuperuser` queda con rol `OBSERVADOR` por defecto (el campo `rol` no forma parte del flujo de `createsuperuser`). Para convertirlo en Administrador, entra a `/admin/` con esa cuenta y cambia su rol, o hazlo desde `manage.py shell`:

```python
from apps.cuentas.models import Usuario
u = Usuario.objects.get(correo='tu_correo@ejemplo.com')
u.rol = Usuario.Rol.ADMINISTRADOR
u.save()
```

### 5. Levantar el servidor

```bash
python manage.py runserver
```

La plataforma queda disponible en `http://localhost:8000/`. El catálogo público (`/`) no requiere sesión; para gestionar fichas o revisar registros necesitas una cuenta con rol Revisor o Administrador.

---

## Estilos (Tailwind CSS)

El CSS se compila con Tailwind CLI a `static/css/tailwind.css` — **no** desde el CDN en tiempo de ejecución (`cdn.tailwindcss.com`), que se descartó a propósito: su compilador JIT en el navegador podía romperse en runtime (ver commit "unifica el sistema de color…") y dejaba toda la interfaz sin ninguna clase de utilidad aplicada. `static/css/tailwind.css` se commitea al repositorio: el despliegue (Docker/`collectstatic`) no corre ningún paso de Node, solo sirve lo que ya está generado.

Si editas `static/css/entrada.css`, `tailwind.config.js`, o agregas clases nuevas en las plantillas, hay que recompilar:

```bash
npm install     # una sola vez
npm run build:css
```

Para no tener que recompilar a mano en cada cambio mientras desarrollas:

```bash
npm run watch:css
```

---

## Ejecutar con Docker

Alternativa a la instalación local: no necesitas Python ni PostgreSQL instalados en la máquina, solo Docker.

```bash
cp .env.example .env
# edita .env: pon una DJANGO_SECRET_KEY propia y un DB_PASSWORD
docker compose up --build
```

Esto levanta dos servicios: `db` (PostgreSQL 16, con los datos en un volumen que persiste entre reinicios) y `web` (la aplicación, con el código montado desde el host — los cambios se recargan solos, igual que con `runserver` local). La plataforma queda en `http://localhost:8000/`.

En otra terminal, con los contenedores corriendo:

```bash
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py importar_especies datos_ejemplo/especies_ejemplo.csv --usuario correo_de_un_revisor@ejemplo.com
```

Cualquier comando de `manage.py` de este README funciona igual, anteponiendo `docker compose exec web`.

**Sobre la imagen:** el `Dockerfile` está pensado también para producción — usa el mismo mecanismo con `gunicorn` y WhiteNoise (sirve los estáticos compilados sin depender de un nginx aparte) cuando se ejecuta sin el `command:` de desarrollo que trae `docker-compose.yml`. `DJANGO_SETTINGS_MODULE=config.settings.produccion` es el valor por defecto de la imagen; `docker-compose.yml` lo cambia a `desarrollo` explícitamente.

---

## Despliegue en producción (AWS Lightsail)

> **En pausa** (4 de septiembre): los créditos institucionales de AWS con los que se pensó este camino finalmente no quedaron disponibles. Se deja documentado igual — reutiliza el mismo `docker-compose.prod.yml`/`Caddyfile` que ya están en el repositorio, así que sirve tal cual el día que haya presupuesto o créditos de nuevo. Mientras tanto, el despliegue activo es el de la sección siguiente, "Despliegue gratuito".

Un solo servidor con `docker-compose.prod.yml` (la misma imagen de arriba + PostgreSQL + [Caddy](https://caddyserver.com/) como proxy — Caddy consigue y renueva el certificado HTTPS de Let's Encrypt solo, sin `certbot` ni tareas programadas que alguien tenga que recordar). Es la misma arquitectura de "todo en una máquina" que ya corre en desarrollo con Docker, apta para el tráfico de este proyecto (RNF-01: 10 usuarios simultáneos) sin necesitar balanceador de carga ni base de datos administrada aparte — ver `docs/bitacora.md`, entrada del 1 de septiembre, para la comparación completa de alternativas de hosting y por qué se descartaron.

Esta guía asume créditos de AWS ya activos en la cuenta y **nada más de infraestructura previa** — se crea todo desde cero. Ningún paso de acá se puede automatizar desde este repositorio: cada uno se hace a mano, una sola vez, en la consola de AWS o por SSH en el servidor.

### 1. Elegir el dominio primero

Let's Encrypt (y por lo tanto Caddy) necesita un dominio real apuntando al servidor — no funciona solo con la IP. Hacer esto de primero importa porque la propagación de DNS puede tardar minutos u horas.

- Si ya hay un dominio (o subdominio) disponible, se puede usar directo.
- Si no, se registra uno — un `.co` cuesta entre US$15 y US$30 al año (ver `docs/bitacora.md`, misma entrada del 1 de septiembre). Esto es un gasto real y aparte de los créditos de cómputo de AWS: **Route 53** (el registrador de dominios de AWS) sí cobra a la tarjeta/facturación de la cuenta — hay que confirmar con quien administra los créditos si ese cargo puntual también queda cubierto, antes de asumir que sí.

### 2. Crear el servidor en Lightsail

1. Consola de AWS → buscar **Lightsail** → **Create instance**.
2. Plataforma: **Linux/Unix** → **OS Only** → **Ubuntu 24.04 LTS**.
3. Plan: el de **2 GB de RAM** (unos US$10/mes) — corre Django, PostgreSQL y Caddy a la vez con margen; el plan más chico de 512 MB–1 GB queda muy justo con los tres contenedores arriba al mismo tiempo, sobre todo mientras se construye la imagen.
4. Nombre de la instancia (ej. `ojo-avizor-produccion`) → **Create instance**.
5. Con la instancia ya `Running`: pestaña **Networking** → **Create static IP** → asociarla a esta instancia. Sin esto, la IP cambia si el servidor se reinicia y el DNS del paso 1 se rompe.

### 3. Apuntar el dominio a la IP

En el proveedor donde está el dominio (Route 53 u otro registrador), crear un registro **A** que apunte al **static IP** del paso anterior. Confirmar que ya resuelve antes de seguir:

```bash
nslookup tu-dominio.com
```

### 4. Conectar al servidor y preparar Docker

Desde la consola de Lightsail, botón **Connect using SSH** (abre una terminal en el navegador, sin manejar llaves a mano):

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
sudo apt-get install -y git
# cerrar y volver a abrir la terminal SSH para que el grupo "docker" tome efecto
```

### 5. Traer el código

```bash
git clone https://github.com/EmersonAngel/ojo-avizor.git
cd ojo-avizor/07_Codigo_Fuente
```

### 6. Variables de entorno de producción

```bash
cp .env.example .env
nano .env
```

Adaptar `.env.example` (ver también sus comentarios) con valores reales de producción, no los de desarrollo:

```bash
DJANGO_SETTINGS_MODULE=config.settings.produccion
DJANGO_SECRET_KEY=  # generar una nueva, nunca la de desarrollo del repo — ver abajo
DJANGO_ALLOWED_HOSTS=tu-dominio.com
DB_PASSWORD=  # una contraseña fuerte y nueva, no la de desarrollo local

# Lo que ya use el proyecto en desarrollo — reutilizar los mismos valores:
DJANGO_EMAIL_HOST_USER=...
DJANGO_EMAIL_HOST_PASSWORD=...
DJANGO_DEFAULT_FROM_EMAIL=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Nueva, la usa Caddyfile — no existe en .env.example porque es propia de este despliegue:
DOMINIO=tu-dominio.com
```

Generar una `DJANGO_SECRET_KEY` nueva y exclusiva para este despliegue (el arranque falla a propósito si detecta la de desarrollo — ver `config/settings/produccion.py`):

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

**Antes de seguir**, agregar el dominio de producción a las credenciales de Google OAuth ya existentes (ver más arriba, sección "Inicio de sesión con Google"): en Google Cloud Console, sumar `https://tu-dominio.com` a los orígenes autorizados y `https://tu-dominio.com/accounts/google/login/callback/` a los URI de redirección — sin esto, "Continuar con Google" funciona en desarrollo pero falla en producción.

### 7. Levantar todo

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml logs -f caddy   # confirmar que consigue el certificado; Ctrl+C para salir del log
```

Con los contenedores corriendo:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
docker compose -f docker-compose.prod.yml exec web python manage.py importar_especies datos_ejemplo/especies_ejemplo.csv --usuario correo-del-superusuario
```

Visitar `https://tu-dominio.com` — debería cargar con el candado de HTTPS puesto.

### 8. Tareas programadas (cron, en el servidor — no dentro del contenedor)

```bash
crontab -e
```

```cron
0 7 * * * cd ~/ojo-avizor/07_Codigo_Fuente && docker compose -f docker-compose.prod.yml exec -T web python manage.py enviar_resumen_revisores
0 3 * * * cd ~/ojo-avizor/07_Codigo_Fuente && docker compose -f docker-compose.prod.yml exec -T web python manage.py respaldar_datos --destino /app/respaldos
```

Los respaldos (RNF-11) quedan en el volumen `respaldos_data` — sobreviven a un `docker compose up --build`, pero siguen viviendo solo en este servidor. Bajarlos de vez en cuando a otro lugar (la propia máquina, o donde se prefiera guardarlos):

```bash
docker compose -f docker-compose.prod.yml cp web:/app/respaldos ./respaldos-descargados
```

### 9. Actualizar el código más adelante

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

Las migraciones corren solas al arrancar (`entrypoint.sh`); no hace falta ningún paso manual aparte para eso.

### Antes de que venzan los créditos

Revisar **Billing → Cost Explorer** en la consola de AWS para ver cuánto crédito institucional queda, y confirmar con quien lo administre qué pasa el 13 de septiembre si vence sin renovarse — si no se renueva ni se migra a otra cuenta/plan de pago antes de esa fecha, el servidor puede quedar suspendido o empezar a facturar a una tarjeta real. Vale la pena dejarlo anotado con tiempo, no descubrirlo el mismo día.

---

## Despliegue gratuito (Render + Neon + Backblaze B2)

Sin tarjeta ni gasto real — pero, a diferencia del despliegue de arriba, ningún proveedor gratis da "todo en un solo lugar" de forma confiable, así que son **tres cuentas separadas**, una por cada pieza:

| Pieza | Para qué | La salvedad de usarla gratis |
| --- | --- | --- |
| [Render](https://render.com) | corre Django | El servicio "duerme" a los 15 minutos sin visitas; la primera persona que entra después espera ~30-60 segundos mientras arranca de nuevo. |
| [Neon](https://neon.tech) | PostgreSQL | Los datos **no** se borran ni caducan (a diferencia del Postgres gratis del propio Render, que sí se borra a los 30 días) — solo el cómputo se pausa solo tras 5 minutos sin consultas, y se reactiva solo en la siguiente. |
| [Backblaze B2](https://www.backblaze.com/cloud-storage) | fotos de avistamientos | 10 GB gratis al mes, sin pedir tarjeta en ningún momento (a diferencia de Cloudflare R2, que sí la pide para activarse — por eso se eligió esta). Compatible con la misma API de S3 que usan Render/AWS, así que el resto del código no cambia. |

Sin disco propio persistente (a diferencia del despliegue con Docker/VPS de arriba), las fotos subidas por la gente **tienen que** vivir en un lugar aparte — de ahí la tercera pieza. `config/settings/produccion.py` ya está preparado: si detecta credenciales de Backblaze B2 en el entorno, las usa; si no, sigue guardando en disco local (el otro despliegue no necesita tocar nada de esto).

### 1. Backblaze B2 (fotos)

1. Crear cuenta en [backblaze.com/sign-up/cloud-storage](https://www.backblaze.com/sign-up/cloud-storage) — no pide tarjeta.
2. **B2 Cloud Storage** → **Create a Bucket** → nombre único (por ejemplo `ojo-avizor-fotos-tunombre`, tiene que ser único entre todos los usuarios de Backblaze, no solo los propios) → **Files in Bucket are**: elegir **Public** (si queda en Private, las fotos no se van a poder ver desde el sitio).
3. En la lista de buckets, el propio bucket recién creado muestra su **Endpoint** — algo como `s3.us-west-004.backblazeb2.com`. De ahí salen dos valores:
   ```bash
   B2_ENDPOINT_URL=https://s3.us-west-004.backblazeb2.com
   B2_REGION=us-west-004
   ```
4. **Account** → **App Keys** → **Add a New Application Key** → **Allow access to Bucket(s)**: elegir el bucket recién creado (no "All") → permisos de lectura y escritura → **Create New Key**. Copiar el **keyID** (`B2_ACCESS_KEY_ID`) y la **applicationKey** (`B2_SECRET_ACCESS_KEY`) que muestra — una sola vez, si se pierden hay que crear otra.
5. La URL pública del bucket es `B2_PUBLIC_DOMAIN=<nombre-del-bucket>.s3.<region>.backblazeb2.com` (mismos datos del paso 3 y el nombre del paso 2, sin `https://` acá).

### 2. Neon (base de datos)

1. Crear cuenta en [neon.tech](https://neon.tech) (con GitHub o correo, sin tarjeta).
2. **Create a project** → nombre, región (la más cercana disponible).
3. Neon muestra una cadena de conexión con esta forma:
   ```
   postgresql://usuario:contraseña@ep-algo-12345.region.aws.neon.tech/nombrebasededatos?sslmode=require
   ```
   Repartirla en las variables de siempre (`DATABASES` en `config/settings/base.py` las espera separadas, no como una sola cadena):
   ```bash
   DB_NAME=nombrebasededatos
   DB_USER=usuario
   DB_PASSWORD=contraseña
   DB_HOST=ep-algo-12345.region.aws.neon.tech
   DB_PORT=5432
   DB_SSLMODE=require
   ```

### 3. Render (la app)

1. Crear cuenta en [render.com](https://render.com) (con GitHub, sin tarjeta).
2. **New +** → **Web Service** → conectar el repositorio `ojo-avizor` de GitHub.
3. Render detecta el `Dockerfile` solo y ofrece **Docker** como entorno — dejarlo así (no hace falta indicar build/start command a mano). En **Name**, poner algo memorable como `ojo-avizor`: ese nombre define de una vez la URL final (`ojo-avizor.onrender.com`), así no hay que volver después a corregir nada.
4. Plan: **Free**.
5. En **Environment** → **Environment Variables**, agregar todas las de `.env.example` con valores reales, más las de Backblaze B2 y Neon de los pasos anteriores, más:
   ```bash
   DJANGO_SETTINGS_MODULE=config.settings.produccion
   DJANGO_SECRET_KEY=  # generar una nueva — ver la sección de AWS de arriba para el comando
   DJANGO_ALLOWED_HOSTS=ojo-avizor.onrender.com  # el nombre elegido en el paso 3
   # Para que se cree solo un superusuario al arrancar — Render (plan gratis)
   # no siempre da una terminal para correr createsuperuser a mano:
   DJANGO_SUPERUSER_CORREO=tu-correo@ejemplo.com
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_NOMBRE_REAL=Tu Nombre
   DJANGO_SUPERUSER_SEUDONIMO=admin
   DJANGO_SUPERUSER_PASSWORD=  # una contraseña fuerte y nueva
   ```
6. **Create Web Service** → Render construye la imagen y la despliega — tarda varios minutos la primera vez. Cuando termine, el sitio queda en `https://ojo-avizor.onrender.com` (o el nombre que se haya puesto), con HTTPS automático y sin dominio propio necesario.

Si se va a usar el inicio de sesión con Google en este despliegue, agregar `https://ojo-avizor.onrender.com/accounts/google/login/callback/` a los URI de redirección en Google Cloud Console (ver la sección "Inicio de sesión con Google" más abajo) **antes** del primer intento de usarlo — si no, ese botón en particular falla, el resto del sitio funciona igual.

### 4. Verificar

Visitar la URL de Render. Puede tardar hasta un minuto en la primera carga (el servicio recién está despertando). Iniciar sesión con el correo/contraseña de `DJANGO_SUPERUSER_*` para entrar como administrador.

### 5. Actualizar el código más adelante

Cada `git push` a la rama conectada dispara un despliegue solo en Render — no hace falta ningún paso manual.

---

## Inicio de sesión con Google

Es opcional: sin configurarlo, el botón "Continuar con Google" aparece en las pantallas de inicio de sesión y registro pero falla al usarse — el resto del sitio (correo/contraseña, recuperar contraseña) funciona exactamente igual. Usa [django-allauth](https://docs.allauth.org/).

### 1. Crear el proyecto y la pantalla de consentimiento

1. Entra a [console.cloud.google.com](https://console.cloud.google.com/) y crea un proyecto nuevo (o usa uno existente).
2. Ve a **APIs y servicios → Pantalla de consentimiento de OAuth**.
   - Tipo de usuario: **Externo** (a menos que tengas Google Workspace).
   - Completa nombre de la app ("Ojo Avizor"), correo de soporte y los datos obligatorios.
   - Mientras la app esté en modo **Prueba**, solo los correos que agregues como "usuarios de prueba" van a poder iniciar sesión — para abrirlo a cualquiera hay que publicarla.

### 2. Crear las credenciales OAuth

1. Ve a **APIs y servicios → Credenciales → Crear credenciales → ID de cliente de OAuth**.
2. Tipo de aplicación: **Aplicación web**.
3. **Orígenes de JavaScript autorizados**: `http://localhost:8000` (agrega el dominio real cuando despliegues).
4. **URI de redirección autorizados** (tiene que ser exacto, con esta forma — la define django-allauth, no se puede cambiar):
   ```
   http://localhost:8000/accounts/google/login/callback/
   ```
   En producción, agrega también `https://tu-dominio.com/accounts/google/login/callback/`.
5. Guarda: te da un **Client ID** (termina en `.apps.googleusercontent.com`) y un **Client Secret** (empieza con `GOCSPX-`).

### 3. Configurar el proyecto

Pon los dos valores en tu `.env`:

```bash
GOOGLE_CLIENT_ID=tu-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-tu-secreto
```

Reinicia el servidor. Los campos propios de la cuenta que Google no manda (seudónimo, rol) se completan solos la primera vez que alguien entra así — ver `apps/cuentas/adapters.py`.

---

## Correo saliente en producción

Recuperar contraseña y las notificaciones por correo (aprobación/devolución de un avistamiento, respuesta a una solicitud de revisor — ver `apps/cuentas/services.py:notificar_por_correo`) necesitan un proveedor SMTP real. En desarrollo no hace falta nada: el correo se imprime en la consola (`EMAIL_BACKEND` en `config/settings/desarrollo.py`).

Con una cuenta de Gmail (gratis, suficiente para el volumen de esta plataforma):

1. Activa la verificación en dos pasos en la cuenta que va a enviar los correos.
2. Genera una **contraseña de aplicación** en [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) — Gmail no acepta la contraseña normal de la cuenta para esto.
3. Completa en tu `.env`:
   ```bash
   DJANGO_EMAIL_HOST_USER=tu-cuenta@gmail.com
   DJANGO_EMAIL_HOST_PASSWORD=la-contraseña-de-aplicación-de-16-letras
   DJANGO_DEFAULT_FROM_EMAIL=Ojo Avizor <tu-cuenta@gmail.com>
   ```

`DJANGO_EMAIL_HOST`, `DJANGO_EMAIL_PORT` y `DJANGO_EMAIL_USE_TLS` ya traen el valor correcto para Gmail por defecto (ver `.env.example`); solo hace falta tocarlos si se usa otro proveedor. Sin esta configuración, el envío falla en silencio (`fail_silently=True`, a propósito: un correo roto no debe tumbar la aprobación de un registro) — la plataforma sigue funcionando igual, simplemente nadie recibe el aviso.

---

## Comandos de gestión propios

### Importar especies desde CSV (RF-14)

```bash
python manage.py importar_especies datos_ejemplo/especies_ejemplo.csv --usuario correo_de_un_revisor@ejemplo.com
```

Columnas esperadas en el CSV (cabecera obligatoria, separador coma):

| Columna | Obligatoria | Notas |
| --- | --- | --- |
| `nombre_cientifico` | Sí | Debe ser único; si ya existe una ficha con ese nombre, la fila se omite (nunca se sobrescribe una ficha curada) |
| `familia`, `orden`, `distribucion`, `historia_natural`, `dato_curioso` | No | Texto libre |
| `tamano_cm` | No | Numérico |
| `nombres_comunes` | No | Varios nombres separados por `;` |

El comando reporta cuántas fichas se crearon, cuáles se omitieron por ya existir y el detalle de cualquier fila con error de validación.

### Respaldar la información del inventario (RNF-11)

```bash
python manage.py respaldar_datos
```

Genera un volcado JSON con fecha y hora en el nombre (`respaldos/ojo_avizor_AAAAMMDD_HHMMSS.json`) con los datos de las cuatro apps del dominio — no incluye sesiones ni el log de administración de Django, que no son "información del inventario". Usa `--destino` para elegir otra carpeta. La carpeta `respaldos/` está en `.gitignore`: son datos, no código.

Para restaurar un respaldo:

```bash
python manage.py loaddata respaldos/ojo_avizor_AAAAMMDD_HHMMSS.json
```

### Aviso resumido a los revisores (RF-24)

Fuera del MVP original, construido por pedido explícito del 22/08/2026.

```bash
python manage.py enviar_resumen_revisores
```

Manda un solo correo con el total de registros pendientes a cada Revisor y Administrador con las notificaciones por correo activadas — no uno por cada registro nuevo. Si no hay nada pendiente, o nadie tiene el correo activado, no manda nada.

Este proyecto no usa Celery ni ninguna otra cola de tareas (RNF-08: costos sostenibles), así que el comando no se ejecuta solo: hay que programarlo, por ejemplo con `cron` una vez al día:

```cron
0 7 * * * cd /ruta/al/proyecto && venv/bin/python manage.py enviar_resumen_revisores
```

---

## Roles y permisos

| Rol | Puede |
| --- | --- |
| Visitante (sin cuenta) | Consultar el catálogo, buscar especies, ver el inventario consolidado |
| Observador | Todo lo anterior + registrar avistamientos, adjuntar fotos, corregir sus propios registros devueltos |
| Revisor | Todo lo anterior + crear/editar fichas de especie, aprobar o devolver avistamientos en la bandeja de revisión |
| Administrador | Todo lo anterior + retirar fichas de especie publicadas |

La jerarquía es acumulativa (Administrador ⊃ Revisor ⊃ Observador ⊃ Visitante) y se aplica con el decorador `apps.cuentas.services.requiere_rol()`.

## Registro sin conexión (RF-23)

El formulario de registrar avistamiento (`/registros/nuevo/`) funciona con conectividad intermitente:

- Si el dispositivo está sin conexión al enviar, los datos (sin fotos) se guardan en `localStorage` con estado «en cola» y se muestra cuántos registros hay pendientes en la barra de navegación.
- Al recuperar señal, la cola se envía automáticamente al servidor.
- Las fotografías no se incluyen en la cola offline (alcance acotado, ver [`docs/arquitectura.md`](docs/arquitectura.md)): si hay una foto adjunta y no hay conexión, se le pide al usuario esperar a tener señal antes de enviar.
- Un service worker (`static/sw.js`, servido en `/sw.js` para poder controlar todo el sitio) cachea las páginas visitadas para que sigan cargando sin conexión.

## Pruebas

```bash
python manage.py test
```

Las pruebas mínimas exigidas por el proyecto (transiciones de estado del Registro, que un registro no aprobado nunca aparezca en público, que las vistas públicas no expongan datos personales ni coordenadas, que la búsqueda encuentre por nombre común) están descritas en [`docs/arquitectura.md`](docs/arquitectura.md).

## Manual de uso

Ver [`docs/manual-uso.md`](docs/manual-uso.md) para una guía paso a paso dirigida a observadores, revisores y administradores.
