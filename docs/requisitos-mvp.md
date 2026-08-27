# Requisitos del producto mínimo viable

> **Paquete de contexto v1.1** · 9 de agosto de 2026
> 20 requisitos funcionales. Si algo no está aquí, no se construye en esta entrega.

---

## Estado actual — 22 de agosto de 2026

**Los 20 requisitos funcionales y los 11 no funcionales de este documento
están implementados y probados.** Detalle día a día en `docs/bitacora.md`.

Además, varias funciones que este documento marca como fuera de alcance se
construyeron por pedido explícito del usuario, con la excepción anotada en
cada RF correspondiente más abajo: historial de aportes propios (roza
RF-12, ver «Mi cuenta»), panel de estadísticas (roza RF-25, ver panel de
administrador), ubicación sobre mapa (RF-22, ver la excepción explícita),
ayuda de la comunidad para identificar un avistamiento (RF-19 y RF-29, ver
la excepción explícita), interfaz en inglés (RNF-13, ver la excepción
explícita), nombres comunes propuestos desde el registro (RF-18, ver la
excepción explícita) y aviso resumido al revisor (RF-24, ver la excepción
explícita). El resto de la lista de «Fuera del alcance» sigue exactamente
fuera: no se empezó ninguno.

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

**Excepción sobre RF-19 y RF-29:** se construyeron por pedido explícito del 22/08/2026. Cualquier aportante (Observador, Revisor o Administrador) puede comentar en un registro `sin_identificar` para ayudar a determinar la especie — "Ayudar a identificar" en el menú. Cada comentario admite voto de Me gusta / No me gusta, pero **solo de Revisor o Administrador** (un voto por persona y comentario, cambiable): es la señal de credibilidad que el revisor usa antes de decidir la especie, no una votación abierta. La vista nunca expone coordenadas, nombre real ni correo del autor del registro (RN-02, RN-06), igual que el resto del catálogo. **Regla añadida el 23/08/2026** tras un aporte real sin ningún dato aprovechable: pedir ayuda (`sin_identificar=True`) exige como mínimo una descripción de lo visto (comportamiento, sustrato o info adicional) o una fotografía — o ambas. Se valida en `apps.registros.services._validar_pedido_de_ayuda`, así que aplica igual al formulario web, a la corrección de un registro devuelto y a la app móvil.

**Excepción sobre RF-02:** el 25/08/2026 se reportó una foto repetida dos veces en la galería de una especie. `apps.registros.services.agregar_fotografia` ahora calcula un hash SHA-256 del archivo tal como se subió (antes de comprimirlo) y descarta la foto si ya existe una igual en el mismo registro — cubre tanto subir el mismo archivo dos veces en un solo envío como volver a adjuntarlo al corregir un registro devuelto. Campo nuevo `Fotografia.hash_contenido`.

**Excepción sobre RNF-13:** la interfaz en inglés se construyó por pedido explícito del 21/08/2026, pese a quedar fuera del MVP original. Se apoya en la estructura de `gettext` que sí se dejó preparada desde el inicio (ver la excepción documentada abajo).

**Excepción sobre RF-21:** se construyó por pedido explícito del 22/08/2026. La ficha pública de cada especie muestra una galería con las fotos de todos sus avistamientos aprobados — la Capa 2 alimentando a la Capa 1 (CLAUDE.md, apartado 2). Solo fotos de registros `APROBADO`; se oculta por completo si la especie aún no tiene ninguna.

**Excepción sobre RF-18:** se construyó por pedido explícito del 22/08/2026. Al registrar un avistamiento, el observador puede sugerir un nombre local para la especie (campo `nombre_comun_propuesto` en `Registro`). No se agrega solo a la ficha: el Revisor lo ve al curar ese registro y decide si lo agrega con un botón dedicado — nunca automático, respeta RN-03 (el revisor no corrige contenido, pero esta es una acción explícita suya, no una corrección).

**Excepción sobre RF-24:** se construyó por pedido explícito del 22/08/2026. Un aviso resumido, no uno por cada registro nuevo: `python manage.py enviar_resumen_revisores` manda un correo con el total de pendientes a cada Revisor y Administrador con las notificaciones activadas. Sin cola de tareas (Celery ni similares, por RNF-08): el comando se programa externamente (cron), ver README.md.

---

## Funcionalidad añadida después del MVP, sin requisito original

Ninguna de estas roza un RF de este documento — no estaban contempladas de ninguna forma. Se construyeron por pedido explícito del usuario el 22/08/2026, tras la entrega.

**Racha de días seguidos registrando.** Cuenta cualquier registro, sin importar su estado — lo que mide es el hábito de registrar, no si el revisor ya lo aprobó. Visible en "Mi cuenta" y en el ranking de observadores, con un ícono de llama que se ve apagado en cero y encendido (con pulso) cuando hay racha activa.

**Insignias por hitos.** Ocho insignias (primer aporte, primera especie, 10 y 25 avistamientos aprobados, 5 y 10 especies distintas, racha de 7 y de 30 días) en "Mi cuenta". No se guardan en la base de datos: se recalculan en cada visita a partir de cifras que ya existen (`apps/cuentas/services.py: evaluar_hitos`), así que nunca quedan desincronizadas de la realidad.

**Exportar el inventario en CSV.** Botón "Descargar CSV" en la lista pública de avistamientos y en el inventario consolidado — para que la Fundación o el semillero usen los datos en informes fuera de la plataforma. Mismas columnas que ya son públicas (especie, nombre común, lugar, fecha, seudónimo del observador); nunca coordenadas, nombre real ni correo (RN-02, RN-06). Sin cuenta: no hay ahí nada que no esté ya público.

**Actividad por departamento y municipio.** `Registro` suma dos campos: `departamento` (lista cerrada de los 33 departamentos de Colombia, ver `apps/registros/colombia.py`) y `municipio` (texto libre — Colombia tiene más de mil municipios, una lista incompleta sería peor que no tenerla). El formulario los preselecciona en Quindío/Pijao, así que un observador de Pijao no tiene que tocarlos. El inventario consolidado (`catalogo:inventario`) muestra "Dónde se concentra la actividad" agrupado por esos dos campos, solo con avistamientos aprobados.

Se descartó a propósito un mapa de veredas de Pijao: no hay datos confiables de esos límites y el campo `lugar` es texto libre, así que un mapa así habría sido una aproximación inventada del territorio real. El desglose por departamento/municipio usa división administrativa oficial y estable — hoy casi todo cae en "Quindío · Pijao" porque el proyecto es de un solo municipio, pero queda listo si algún día se suman observadores de otros lugares. Un mapa coloreado de Colombia (como el de distribución de especies, pero a nivel de país) queda pendiente como posible siguiente paso: requeriría conseguir un SVG de los departamentos, que este proyecto no tiene.

**Búsqueda avanzada, ficha enriquecida, perfil de observador y panel de estadísticas.** Se construyeron por pedido explícito del 25/08/2026, tras confirmar con el usuario qué funcionalidades concretas quería (no se inventó ninguna sin preguntar antes, según manda CLAUDE.md).

- *Filtros combinables* en el catálogo público (`catalogo:publico_listado`): familia, orden taxonómico, rango de tamaño y orden de los resultados, además de la búsqueda de texto que ya existía (RF-05). Todo vía HTMX, sin recargar la página.
- *Ficha de especie enriquecida*: foto de cabecera más grande (estilo editorial), y una sección "Especies similares" con otras fichas de la misma familia (`apps.catalogo.repositories.listar_especies_similares` — sin familia registrada, no se muestra nada, porque no hay forma confiable de emparentarlas).
- *Perfil público de observador* (`registros:observador_perfil`, enlazado desde el ranking): seudónimo, avistamientos aprobados, especies distintas, racha e insignias conseguidas, más la lista de sus avistamientos ya publicados. Solo existe para quien ya tiene al menos un aporte aprobado (si no, 404) — nunca nombre real, correo ni coordenadas (RN-02, RN-06), verificado con pruebas.
- *Panel de estadísticas* en el inventario consolidado: gráfica de avistamientos aprobados por mes, los últimos 6 meses, con barras CSS (sin librería de gráficas, por RNF-01/RNF-08).
