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
