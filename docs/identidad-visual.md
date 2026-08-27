# Identidad visual de Ojo Avizor

> **Paquete de contexto v1.5** · Complementa `CLAUDE.md` y `docs/arquitectura.md`.
> Los archivos de marca están en `static/marca/`.

---

## 1. Regla que gobierna todo

**El azul profundo estructura, el cian señala, el blanco respira.**

La interfaz la usan niños de 10 a 15 años y observadores adultos, en celulares de gama baja y con luz de campo. Prioriza el contraste y el espacio en blanco sobre la decoración.

---

## 2. Paleta

Declara estas variables y **no uses colores fuera de esta lista**. La aplicación tiene
**dos temas obligatorios**: claro y oscuro. Todos los componentes deben funcionar en ambos.

### Tema claro (por defecto)

```css
:root {
  /* Marca */
  --azul-profundo:  #1B2D55;  /* barras, títulos, texto destacado */
  --azul-medio:     #0173BC;  /* enlaces, botones, foco */
  --cian:           #00ACE8;  /* acentos, iconos, cifras grandes */

  /* Superficies */
  --blanco:         #FFFFFF;
  --superficie:     #F7FAFC;  /* fondo general de página */
  --superficie-alt: #EEF3F8;  /* tarjetas destacadas, bloques de datos */
  --borde:          #C9D6E2;

  /* Texto */
  --texto:          #2E3A45;  /* cuerpo */
  --texto-suave:    #6B7A88;  /* metadatos, ayudas */
  --texto-inverso:  #FFFFFF;

  /* Estados */
  --exito:          #0F7B5A;  /* aprobado */
  --alerta:         #A66A00;  /* pendiente, sin conexión */
  --error:          #BE1A21;  /* devuelto, campos obligatorios, coordenadas */
  --exito-fondo:    #EFF8F4;
  --alerta-fondo:   #FFF6E8;
  --error-fondo:    #FDF0F0;

  /* Sombras */
  --sombra-tarjeta: 0 1px 3px rgba(27,45,85,.08);
  --sombra-elevada: 0 4px 14px rgba(27,45,85,.12);
}
```

### Tema oscuro

Se activa con el atributo `data-tema="oscuro"` en `<html>`.

```css
[data-tema="oscuro"] {
  /* Marca — aclarada para conservar legibilidad sobre fondo profundo */
  --azul-profundo:  #16223A;  /* barras y superficies elevadas */
  --azul-medio:     #5FB3E8;  /* enlaces, botones, foco */
  --cian:           #4FC8F0;  /* acentos, cifras grandes */

  /* Superficies */
  --blanco:         #16223A;  /* lo que en claro era blanco */
  --superficie:     #0E1626;  /* fondo general de página */
  --superficie-alt: #1E2C48;  /* tarjetas destacadas, bloques de datos */
  --borde:          #2C3E5E;

  /* Texto */
  --texto:          #E6ECF5;
  --texto-suave:    #9DAEC4;
  --texto-inverso:  #0E1626;

  /* Estados */
  --exito:          #3FBF92;
  --alerta:         #E5A73C;
  --error:          #F0787E;
  --exito-fondo:    #16302A;
  --alerta-fondo:   #33270F;
  --error-fondo:    #33191C;

  /* Sombras: en oscuro se perciben como profundidad, no como elevación */
  --sombra-tarjeta: 0 1px 3px rgba(0,0,0,.40);
  --sombra-elevada: 0 4px 14px rgba(0,0,0,.55);
}
```

**Escribe todos los componentes usando únicamente estas variables.** Si lo haces así, el
modo oscuro no exige una sola regla adicional de estilo: basta con cambiar el atributo.

### Advertencia de accesibilidad — importante

Verifiqué el contraste de toda la paleta contra WCAG 2.1. Un resultado obliga a una regla:

| Combinación | Contraste | Veredicto |
| --- | --- | --- |
| Texto `--texto` sobre blanco | 11,6 : 1 | AAA |
| `--azul-profundo` sobre blanco | 13,5 : 1 | AAA |
| Blanco sobre `--azul-profundo` | 13,5 : 1 | AAA |
| `--azul-medio` sobre blanco | 5,0 : 1 | AA |
| Blanco sobre `--azul-medio` | 5,0 : 1 | AA |
| `--exito` sobre blanco | 5,3 : 1 | AA |
| `--error` sobre blanco | 6,3 : 1 | AA |
| **`--cian` sobre blanco** | **2,6 : 1** | **INSUFICIENTE** |
| **Blanco sobre `--cian`** | **2,6 : 1** | **INSUFICIENTE** |

**Regla derivada:** el cian **nunca** se usa para texto pequeño ni como fondo de botón con texto encima. Su lugar son los acentos no informativos: subrayado de la pestaña activa, iconos decorativos, cifras muy grandes (36 px o más), separadores y el iris del isotipo.

**Para botones y enlaces usa `--azul-medio`**, que sí cumple AA.

### Contraste del tema oscuro

Toda la paleta oscura fue verificada y supera el nivel AA; la mayoría alcanza AAA.

| Combinación | Contraste | Veredicto |
| --- | --- | --- |
| `--texto` sobre `--superficie` | 15,2 : 1 | AAA |
| `--texto` sobre `--blanco` (superficie elevada) | 13,4 : 1 | AAA |
| `--texto-suave` sobre `--superficie` | 8,0 : 1 | AAA |
| `--cian` sobre `--superficie` | 9,3 : 1 | AAA |
| `--azul-medio` sobre `--superficie` | 7,8 : 1 | AAA |
| `--exito` sobre `--superficie` | 7,8 : 1 | AAA |
| `--alerta` sobre `--superficie` | 8,5 : 1 | AAA |
| `--error` sobre `--superficie` | 6,6 : 1 | AA |

**Diferencia importante respecto del tema claro:** en oscuro el cian **sí** cumple contraste,
porque se aclaró a `#4FC8F0`. Puede usarse para texto y para fondo de botón con texto oscuro
encima. La restricción del apartado anterior aplica únicamente al tema claro.

---

## 3. Tipografía

El cuerpo y la interfaz usan fuentes del sistema, sin descargas externas: ahorran ancho de banda,
que es un requisito real de este proyecto.

```css
--fuente: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

Los títulos, las cifras destacadas y el nombre científico usan una serif de display —
**Lora**, autoalojada en `static/fonts/` (dos archivos variables, uno recto y uno cursivo,
~40 KB cada uno, subconjunto latino) — nunca desde un CDN en vivo, por la misma razón que
Leaflet se sirve local: en campo, con conectividad irregular, la tipografía no puede depender
de una red externa.

```css
--fuente-display: 'Lora', ui-serif, Georgia, serif;
```

| Uso | Tamaño | Peso | Color | Fuente |
| --- | --- | --- | --- | --- |
| Título de página | 28 px | 700 | `--azul-profundo` | `--fuente-display` |
| Título de sección | 20 px | 700 | `--azul-profundo` | `--fuente-display` |
| Subtítulo | 16 px | 600 | `--azul-profundo` | `--fuente` |
| Cuerpo | 16 px | 400 | `--texto` | `--fuente` |
| Metadato o ayuda | 14 px | 400 | `--texto-suave` | `--fuente` |
| Cifra destacada | 40 px | 700 | `--cian` | `--fuente-display` |
| Nombre científico | 15 px | 700 *cursiva* | `--texto-suave` | `--fuente-display`, itálica |

**Nunca bajes de 14 px.** La población objetivo incluye menores y adultos mayores leyendo al sol.

---

## 4. Espaciado, bordes y sombras

```css
--radio-chico: 6px;    /* campos, botones */
--radio:      10px;    /* tarjetas */
--radio-pill: 999px;   /* etiquetas de nombres comunes */

--sombra-tarjeta: 0 1px 3px rgba(27,45,85,.08);
--sombra-elevada: 0 4px 14px rgba(27,45,85,.12);
```

Escala de espaciado en múltiplos de 4 px: 4, 8, 12, 16, 24, 32, 48.
Ancho máximo de contenido: **1200 px**, centrado.

Sombras muy sutiles. Este es un producto de consulta, no una tienda.

---

## 5. Componentes clave

**Barra superior.** Fondo `--azul-profundo`, alto 80 px en móvil y 112 px desde `sm`. Logo apilado a la izquierda (versión de modo oscuro, blanca, siempre — la barra es oscura en los dos temas): 56 px de alto en móvil, 80 px desde `sm`, ancho proporcional. Navegación centrada o a la derecha; la pestaña activa lleva subrayado de 3 px en `--cian`.

**Botón principal.** Fondo `--azul-medio`, texto blanco, radio 6 px, alto 44 px mínimo (objetivo táctil). Al pasar el cursor, oscurece un 8 %.

**Botón secundario.** Fondo transparente, borde 1 px `--borde`, texto `--azul-profundo`.

**Tarjeta de especie.** Fondo blanco, borde 1 px `--borde`, radio 10 px, sombra de tarjeta. Imagen arriba con relación 3:2. Debajo: nombre común en 16 px semibold, nombre científico en cursiva `--texto-suave`, y el número de avistamientos en `--azul-medio`.

**Etiqueta de nombre común.** Fondo `--superficie-alt`, texto `--azul-profundo`, radio pill, 13 px, padding 4 px 12 px.

**Bloque del inventario consolidado.** Fondo `--superficie-alt`, radio 10 px. Las tres cifras en 40 px `--cian` con su rótulo debajo en 14 px `--texto-suave`. Es lo primero que ve el visitante: dale aire.

**Estados de un registro.** Etiqueta con fondo e texto del estado correspondiente:
`PENDIENTE` → `--alerta-fondo` / `--alerta` · `APROBADO` → `--exito-fondo` / `--exito` · `DEVUELTO` → `--error-fondo` / `--error`.

**Aviso de sin conexión.** Franja con fondo `--alerta-fondo`, borde izquierdo de 4 px en `--alerta`. Debe indicar cuántos registros hay en cola.

**Campo obligatorio.** Asterisco en `--error` junto a la etiqueta. El error se comunica con texto, nunca solo con color.

---

## 6. Archivos de marca y dónde va cada uno

Guárdalos en `static/marca/`.

| Archivo | Dónde se usa |
| --- | --- |
| `logo-horizontal-fondo-oscuro.png` | Sin uso actual en la interfaz (la barra superior pasó a usar el logo apilado). Queda disponible para piezas puntuales sobre fondo oscuro que necesiten el logotipo horizontal completo. |
| `logo-horizontal.png` | Documentos, correos y cualquier fondo claro. |
| `logo-apilado.png` | Pantalla de inicio de sesión y de registro de cuenta con el tema claro, centrado sobre el formulario. |
| `isotipo.png` | Cabecera en pantallas estrechas cuando el logo completo no cabe, y como imagen para compartir en redes. |
| `logo-horizontal-modo-oscuro.png` | Sin uso actual en la interfaz. Variante clara del logotipo horizontal completo, para piezas puntuales sobre fondo oscuro con el tema oscuro activo. |
| `isotipo-modo-oscuro.png` | Isotipo para pantallas estrechas con el tema oscuro activo. |
| `logo-apilado-modo-oscuro.png` | **Barra superior** de la aplicación, en los dos temas (la barra es oscura en ambos). También inicio de sesión y registro de cuenta con el tema oscuro activo. |
| `favicon.ico` | `<link rel="icon">` |
| `icono-192.png`, `icono-512.png` | Manifiesto de la aplicación web (necesarios para instalarla y para el funcionamiento sin conexión). |
| `apple-touch-icon.png` | `<link rel="apple-touch-icon">` |

### Reglas de uso del logo

- Conserva alrededor un margen libre igual a la mitad de la altura del símbolo.
- **No lo recolorees, deformes, rotes ni le añadas sombras.**
- Sobre fotografías, usa la versión de fondo oscuro sobre una capa semitransparente.
- **Intercambia el archivo según el tema.** Resuélvelo con `<picture>` y una consulta de medios,
  o alternando el atributo `src` desde el mismo script que aplica el tema.
- Tamaño mínimo del logo horizontal: 120 px de ancho. Por debajo, usa el isotipo.
- El símbolo lleva `alt="Ojo Avizor"`; si va junto al nombre escrito, `alt=""` y `aria-hidden="true"`.

---

## 7. Coexistencia con los logos institucionales

En el **pie de página** van los logos de la Corporación Universitaria Empresarial Alexander von Humboldt y de la Fundación Smurfit Westrock Colombia, en escala de grises o a color según el fondo, con el rótulo «Un proyecto de la comunidad de Pijao, con el acompañamiento de:».

**No los pongas en la barra superior.** Esa es de la plataforma. La barra dice de qué producto se trata; el pie dice quién lo respalda.

---

## 8. Qué evitar

- Degradados, sombras marcadas, animaciones llamativas. **Excepción confirmada el 27/08/2026:**
  la clase `.hero` (portada, inventario, iniciar sesión, crear cuenta) sí usa un degradado de
  azul-medio a azul-profundo, con dos óvalos difuminados de acento (`.hero-blobs`) — se probó
  a quitarlo por esta misma regla y el usuario pidió explícitamente conservarlo. No lo quites
  de nuevo sin que te lo pidan.
- Iconos de más de un estilo. Elige un solo conjunto de trazo lineal.
- Texto sobre imagen sin capa de contraste.
- Cian como color de texto o de fondo de botón (ver la advertencia del apartado 2).
- Emojis como iconos de interfaz.
- Colores literales en el código: impiden que el modo oscuro funcione.
- Tipografías servidas desde un CDN en vivo (Google Fonts y similares): dependen de una red
  externa que puede no estar disponible en campo. La única serif de display del proyecto
  (Lora) está autoalojada — ver apartado 3 — precisamente para evitar esto.

---

## 9. Modo oscuro

Es **obligatorio** y debe funcionar en todas las pantallas.

### Cómo se activa

Tres estados, en este orden de precedencia:

1. **Preferencia guardada** del usuario, en `localStorage` bajo la clave `tema`.
2. **Preferencia del sistema**, mediante `prefers-color-scheme`, si no hay nada guardado.
3. **Claro**, como valor por omisión.

```html
<html lang="es" data-tema="claro">
```

Aplica el tema **antes de pintar la página**, con un script mínimo en el `<head>`, para evitar
el destello blanco que se produce si se aplica después:

```html
<script>
  (function () {
    var t = localStorage.getItem('tema');
    if (!t) {
      t = matchMedia('(prefers-color-scheme: dark)').matches ? 'oscuro' : 'claro';
    }
    document.documentElement.setAttribute('data-tema', t);
  })();
</script>
```

### El control

Un botón en la barra superior, a la derecha, con icono de sol o luna según el estado actual.
Debe llevar `aria-label` descriptivo («Cambiar a modo oscuro» / «Cambiar a modo claro») y
guardar la elección en `localStorage`.

Alpine.js es suficiente para manejarlo; no requiere nada más.

### Reglas al construir componentes

- **Nunca escribas un color literal** en una hoja de estilos ni en una plantilla. Solo variables.
- **Nunca uses `#fff` como fondo de tarjeta**: usa `var(--blanco)`, que en oscuro vale `#16223A`.
- En oscuro, la jerarquía se construye con **superficies más claras**, no con sombras: el fondo
  general es el más oscuro y las tarjetas se elevan aclarándose.
- Las **fotografías de aves** no se alteran. Si alguna resulta deslumbrante sobre fondo oscuro,
  reduce su brillo un 8 % con un filtro, nunca más.
- El **logotipo cambia de archivo** según el tema (ver la tabla del apartado 6).

### Verificación antes de dar por terminada una pantalla

- [ ] ¿Se ve correctamente en ambos temas?
- [ ] ¿Algún color literal se coló en el CSS o en la plantilla?
- [ ] ¿El logotipo corresponde al tema activo?
- [ ] ¿Los estados de un registro se distinguen en oscuro?
- [ ] ¿Hay destello blanco al cargar la página en modo oscuro?
