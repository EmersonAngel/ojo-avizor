# Requisitos del producto mínimo viable

> **Paquete de contexto v1.1** · 9 de agosto de 2026
> 20 requisitos funcionales. Si algo no está aquí, no se construye en esta entrega.

---

## Estado actual — 15 de agosto de 2026

**Los 20 requisitos funcionales y los 11 no funcionales de este documento
están implementados y probados.** Detalle día a día en `docs/bitacora.md`.

Además, tres funciones que este documento marca como fuera de alcance se
construyeron por pedido explícito del usuario, con la excepción anotada en
cada RF correspondiente más abajo: historial de aportes propios (roza
RF-12, ver «Mi cuenta»), panel de estadísticas (roza RF-25, ver panel de
administrador) y ubicación sobre mapa (RF-22, ver la excepción explícita).
El resto de la lista de «Fuera del alcance» sigue exactamente fuera: no se
empezó ninguno.

---

## Cuentas y roles

### RF-09 · Autenticar a los usuarios que aportan
Permitir crear cuenta, iniciar sesión y cerrar sesión.
**Aceptación:** un usuario completa el registro, entra y sale de la plataforma.

### RF-10 · Gestionar roles y permisos
Cuatro roles con permisos distintos: Administrador, Revisor, Observador y Visitante.
**Aceptación:** cada usuario tiene un rol y el sistema impide las acciones que no le corresponden.

### RF-27 · Nombre real interno y seudónimo público
La cuenta exige nombre real y correo. Públicamente solo se muestra el seudónimo. Administrador y Revisor pueden ver la identidad real.
**Aceptación:** el catálogo público no expone en ningún punto el nombre real ni el correo.
**Crítico:** protege los datos de menores de edad. No es negociable.

---

## Catálogo — Capa 1

### RF-16 · Crear y editar la ficha de una especie
Con nombre científico, nombres comunes, foto de referencia, distribución, tamaño, historia natural y dato curioso.
**Aceptación:** un Revisor crea una ficha completa y la edita después.

### RF-17 · Múltiples nombres comunes por especie
Una especie admite varios nombres comunes, incluidas las denominaciones locales.
**Aceptación:** se añaden varios nombres a una especie, todos visibles en la ficha y utilizables en la búsqueda.

### RF-14 · Cargar el contenido inicial
Permitir incorporar un conjunto inicial de fichas antes de abrir la plataforma. Se recibirán en hoja de cálculo.
**Aceptación:** existe un comando de gestión que importa fichas desde CSV.

### RF-13 · Editar o retirar una ficha publicada
**Aceptación:** el Administrador retira una ficha y deja de aparecer en el catálogo.

---

## Registro de avistamientos — Capa 2

### RF-01 · Registrar el avistamiento de una especie
Obligatorios: lugar, fecha y autor. Opcionales: fotografía, comportamiento, sustrato e información adicional.
**Aceptación:** un Observador envía el formulario y el registro queda en estado `PENDIENTE`.

### RF-02 · Adjuntar fotografía al registro
**Aceptación:** la imagen queda asociada al registro y se almacena comprimida.

### RF-11 · Conservar la autoría del contenido
Cada registro y cada fotografía guardan de forma permanente quién los aportó.
**Aceptación:** la autoría se conserva aunque el registro cambie de estado.

### RF-15 · Separar ficha y registro
Una ficha de especie existe con independencia de los avistamientos; cada avistamiento se asocia a una ficha.
**Aceptación:** se crea una ficha sin registros, y varios registros de distintos usuarios apuntan a la misma ficha.

### RF-23 · Registrar sin conexión y enviar al recuperar señal
**Alcance acotado:** guardado local del formulario y envío diferido. **No es sincronización bidireccional.**
**Aceptación:** con la conexión interrumpida, el formulario se conserva en el dispositivo y se envía solo al recuperar señal.

---

## Curaduría

### RF-06 · Retener los registros hasta su revisión
Todo registro nuevo queda `PENDIENTE` y no se publica hasta ser aprobado.
**Aceptación:** un registro recién creado no aparece en el catálogo público.

### RF-07 · Revisar, aprobar o devolver un registro
El revisor ve los pendientes y decide. **No corrige el contenido.**
**Aceptación:** el revisor accede a la bandeja y aprueba o devuelve cada registro.

### RF-08 · Informar el motivo de una devolución
Devolver exige escribir un motivo, visible para el autor.
**Aceptación:** no se puede devolver sin motivo; el autor lo ve en su registro.

---

## Consulta pública

### RF-03 · Consultar el catálogo de especies
Sin necesidad de cuenta.
**Aceptación:** un visitante no autenticado accede al listado.

### RF-04 · Ver la ficha detallada de una especie
Con toda su información y sus avistamientos aprobados.
**Aceptación:** al seleccionar una especie se muestra la ficha completa.
**Atención:** los avistamientos muestran `lugar` en texto, nunca coordenadas (RN-06).

### RF-05 · Buscar especies por nombre
Por nombre científico **y por nombres comunes**.
**Aceptación:** buscar por una denominación local devuelve la especie correspondiente.

### RF-26 · Consultar el inventario consolidado del municipio
Total de especies, total de avistamientos y número de observadores participantes.
**Aceptación:** existe una vista con esas tres cifras.
**Importante:** es la carencia que justifica todo el proyecto. Debe verse bien.

### RF-28 · Atribuir públicamente el aporte mediante seudónimo
**Aceptación:** cada registro publicado muestra el seudónimo de su autor, sin datos personales.

---

## Requisitos no funcionales del MVP

| Código | Requisito |
| --- | --- |
| RNF-01 | Funcionar en celulares de gama media y baja |
| RNF-02 | Funcionar en celular y en computador (diseño adaptable) |
| RNF-03 | Tolerar conectividad intermitente sin perder datos ya ingresados |
| RNF-04 | Comprimir y redimensionar las imágenes al almacenarlas |
| RNF-05 | No exponer públicamente datos personales de menores |
| RNF-06 | Almacenar las credenciales cifradas |
| RNF-07 | Interfaz comprensible para usuarios de 10 a 15 años |
| RNF-08 | Operar con costos sostenibles tras la práctica |
| RNF-09 | Código bajo control de versiones con historial legible |
| RNF-10 | Entregar documentación técnica y manual de uso |
| RNF-11 | Respaldar la información del inventario |

---

## Fuera del alcance de esta entrega

**No implementar**, aunque parezca sencillo:

| Código | Qué es |
| --- | --- |
| RF-12 | Historial de aportes propios |
| RF-18 | Proponer nombres comunes desde el registro |
| RF-19 y RF-29 | Solicitar y proponer ayuda de identificación |
| RF-20 | Datos ecológicos ampliados |
| RF-21 | Álbum de fotografías por especie |
| RF-22 | Ubicación sobre mapa |
| RF-24 | Avisos al revisor |
| RF-25 | Panel de estadísticas de uso |
| RNF-12 | Metas de rendimiento medidas |
| RNF-13 | Interfaz en español e inglés |

**Excepción sobre RNF-13:** aunque la traducción al inglés queda fuera, **prepara la estructura de internacionalización desde el inicio** — envuelve las cadenas visibles con `gettext`. Añadir idiomas después obliga a rehacer todas las plantillas.

**Excepción sobre RF-22:** se construyó por pedido explícito del 15/08/2026, pese a estar fuera del MVP original. Implementación deliberadamente liviana para no romper RNF-01/RNF-02: mapa SVG estático (sin librería de mapas ni tiles), coloreado por país vía `paises_distribucion` (ver `docs/modelo-datos.md`). RF-12 y RF-25 se construyeron por la misma vía (ver "Mi cuenta" y el panel de administración).

**Sobre RF-19:** el campo `especie` del modelo Registro admite `NULL` y existe el campo `sin_identificar` precisamente para habilitarlo más adelante. Deja la estructura, no la funcionalidad.
