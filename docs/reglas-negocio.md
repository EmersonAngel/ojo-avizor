# Reglas de negocio

> **Paquete de contexto v1.0** · 9 de agosto de 2026

Estas ocho reglas son políticas del proyecto, no detalles de implementación. **Ninguna se puede omitir ni relajar por conveniencia técnica.** Si una decisión de código las contradice, la decisión está mal.

---

## RN-01 · Todo aporte pasa por revisión antes de publicarse

Ningún registro aportado por la comunidad se publica sin haber sido revisado y aprobado.

**En el código:** todo Registro nace en `PENDIENTE`. Las consultas del catálogo público filtran siempre por `estado='APROBADO'`. Conviene un *manager* específico —por ejemplo `Registro.publicados`— para que no se pueda olvidar el filtro.

**Por qué:** la credibilidad del inventario ante los observadores del municipio es su activo más frágil.

---

## RN-02 · Ningún dato identificable de menores es público

No se publica nada que permita identificar o localizar a un menor de edad. La autoría se muestra mediante **seudónimo**; el nombre real y el correo quedan accesibles solo a Administrador y Revisor.

**En el código:** ninguna plantilla pública puede acceder a `usuario.nombre_real` ni a `usuario.correo`. Al mostrar autoría, siempre `usuario.seudonimo`.

**Por qué:** obligación legal y ética. Es la regla que no admite excepción.

---

## RN-03 · El revisor no corrige: devuelve con explicación

El revisor acepta el registro o lo devuelve con un motivo para que su autor lo corrija o lo sustente. **No modifica el contenido ajeno.**

**En el código:** el servicio de revisión solo cambia el estado y crea una Revision. No toca los campos del Registro.

**Por qué:** un registro aparentemente improbable puede ser cierto. Hay casos documentados de especies observadas fuera de su distribución habitual o tras décadas sin registros en la región. Corregir de oficio podría borrar un hallazgo legítimo.

---

## RN-04 · Solo se publica material con autorización verificada

Únicamente material con licencia abierta o autorización de su autor.

**En el código:** no uses imágenes de internet ni siquiera para datos de prueba. Emplea marcadores de posición generados.

---

## RN-05 · Consultar es abierto; aportar requiere cuenta

La consulta del inventario no requiere identificación. Aportar contenido exige una cuenta con rol Observador o superior.

**En el código:** las vistas de catálogo, ficha, búsqueda e inventario consolidado son públicas. Las de registro y curaduría exigen autenticación y rol.

---

## RN-06 · La ubicación de especies sensibles no se publica con precisión exacta

Cuando la ubicación pueda facilitar la localización de especies vulnerables, se publica con precisión reducida.

**En el código:** el modelo distingue entre la ubicación almacenada y la mostrada. **Pendiente de definir** qué especies se consideran sensibles y con cuánta reducción. Por ahora: almacena las coordenadas completas y **no las muestres en el catálogo público**; solo el campo `lugar` en texto.

**Por qué:** la propia comunidad identificó la caza ilegal de fauna silvestre como causa del problema ambiental del municipio. Sería contradictorio que la plataforma la facilitara.

---

## RN-07 · La autoría del contenido es de la comunidad y de quien registra

La autoría pertenece únicamente a la comunidad y a cada usuario que realiza el registro. La Fundación, la Universidad y el practicante pueden **usar** estos datos para los fines del proyecto, pero en ningún caso adquieren su autoría.

**En el código:** el campo de autoría es permanente y no se reasigna ni se anonimiza al internamente. Las condiciones de uso deben expresar la distinción entre autoría y uso.

---

## RN-08 · Un rechazo se explica y se conserva

Un registro devuelto no se elimina: queda archivado con su motivo.

**En el código:** `DEVUELTO` es un estado más, no un borrado. Las revisiones nunca se eliminan.

**Por qué:** un rechazo bien explicado es una oportunidad de aprendizaje, que es parte del propósito de la plataforma.

---

## Verificación rápida

Antes de dar por terminada una funcionalidad, comprueba:

- [ ] ¿Puede algún dato personal de un menor llegar a una vista pública? (RN-02)
- [ ] ¿Puede publicarse un registro sin haber sido aprobado? (RN-01)
- [ ] ¿Alguna vista modifica el estado sin pasar por un servicio? (RN-03)
- [ ] ¿Se puede devolver un registro sin motivo? (RN-08)
- [ ] ¿Alguna vista pública exige autenticación sin necesidad? (RN-05)
