# Manual de uso — Ojo Avizor

> Guía para las personas que usan la plataforma: observadores, revisores y administradores. Para documentación técnica de instalación ver [`README.md`](../README.md).

---

## Para cualquier persona, sin necesidad de cuenta

En la página principal (`/`) puedes:

- **Ver el catálogo** de especies de aves registradas en Pijao.
- **Buscar** una especie escribiendo su nombre científico o cualquiera de sus nombres comunes (por ejemplo, "toche" o "mirla") en el cuadro de búsqueda.
- **Abrir la ficha** de una especie para ver su descripción, tamaño, historia natural, un dato curioso y los avistamientos aprobados en el municipio (lugar y fecha, sin coordenadas exactas ni datos personales de quien lo aportó — solo su seudónimo).
- **Ver el inventario consolidado** (enlace "Ver inventario consolidado") con el total de especies, avistamientos y observadores participantes.

No necesitas iniciar sesión para nada de esto.

---

## Crear una cuenta

Para aportar avistamientos necesitas una cuenta:

1. Toca **"Crear cuenta"** en la parte superior.
2. Completa usuario, correo, tu nombre real, un **seudónimo** (así te van a ver los demás, tu nombre real nunca se muestra en público) y una contraseña.
3. Al registrarte quedas automáticamente con sesión iniciada y con rol **Observador**.

Los roles Revisor y Administrador no se auto-asignan: los otorga un Administrador desde el panel de gestión.

---

## Como Observador

### Registrar un avistamiento

1. Toca **"Mis avistamientos"** y luego **"Registrar avistamiento"** (o ve directo a esa opción desde el menú).
2. Completa el lugar y la fecha (obligatorios; la fecha no puede ser futura). Si sabes qué especie es, selecciónala; si no, marca **"Pido ayuda para identificarla"**.
3. Puedes agregar comportamiento, sustrato, información adicional y fotografías (opcional). Las fotos se comprimen automáticamente al guardarlas.
4. Al enviar, tu registro queda en estado **Pendiente** hasta que un Revisor lo revise.

**Sin conexión:** si estás en el campo sin señal, puedes llenar el formulario igual (sin fotos) y enviarlo — quedará guardado en tu propio celular y se enviará solo cuando recuperes conexión. Verás cuántos registros tienes pendientes de enviar en la parte superior de la página.

### Revisar el estado de tus avistamientos

En **"Mis avistamientos"** ves todos los que has aportado y su estado:

- **Pendiente**: está esperando revisión.
- **Aprobado**: ya es público y aparece en la ficha de la especie.
- **Devuelto**: el revisor pidió más información o una corrección. Toca **"Corregir"** para ver el motivo, ajustar tu registro y reenviarlo — vuelve a quedar en Pendiente.

---

## Como Revisor

Además de todo lo anterior, un Revisor puede:

### Gestionar fichas de especie

En **"Fichas de especie"**:

- **"Nueva ficha"** crea una especie con nombre científico, familia, orden, distribución, tamaño, historia natural, dato curioso, foto de referencia y sus nombres comunes (puedes agregar varios, marcando cuáles son propios del municipio).
- **"Editar"** en cualquier ficha existente para actualizar su información o agregar más nombres comunes.

### Revisar avistamientos

En **"Bandeja de revisión"** aparecen todos los registros pendientes, con las coordenadas exactas visibles (solo Revisor y Administrador las ven; nunca se publican).

- **"Aprobar"** publica el avistamiento de inmediato en la ficha de la especie.
- **"Devolver"** exige escribir un motivo — no se puede devolver sin explicar por qué. El autor verá ese motivo y podrá corregir y reenviar. El revisor **no modifica** el contenido del registro ajeno: solo aprueba o devuelve con explicación.

---

## Como Administrador

Además de todo lo anterior, un Administrador puede:

- **Retirar una ficha de especie** publicada (botón "Retirar" en "Fichas de especie"), que deja de aparecer en el catálogo.
- **Gestionar usuarios y roles** desde el panel de administración de Django (`/admin/`), incluyendo asignar el rol Revisor o Administrador a otras cuentas.

---

## Preguntas frecuentes

**¿Por qué no aparece mi avistamiento en el catálogo público apenas lo envío?**
Porque todo aporte pasa primero por revisión (nunca se publica sin que un Revisor lo apruebe).

**¿Se ve mi nombre real en algún lado?**
No. En todo el sitio público solo se muestra tu seudónimo. Tu nombre real y tu correo solo los pueden ver Revisores y Administradores.

**¿Se publica la ubicación exacta de un avistamiento?**
No. Públicamente solo se muestra el lugar en texto (por ejemplo, "Vereda La Playa"); las coordenadas se guardan pero nunca se publican, para no facilitar la localización de especies vulnerables.
