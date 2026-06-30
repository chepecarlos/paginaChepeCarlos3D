# Mini guia de productos (ES/EN)

Esta guia te permite crear o editar productos usando atributos en espanol o ingles.

## Donde crear productos

Guarda tus archivos Markdown dentro de:

- content/productos/

Ejemplo de rutas:

- content/productos/pokemon/pikachu.md
- content/productos/religiosas/cruzJesus.md

## Plantilla lista para copiar

Usa esta base y solo cambia los valores:

- [PLANTILLA_PRODUCTO.md](PLANTILLA_PRODUCTO.md)

## Campos compatibles (espanol e ingles)

Puedes usar cualquiera de estas dos columnas:

| Canonico (EN) | Alias (ES)  |
| ------------- | ----------- |
| title         | titulo      |
| category      | categoria   |
| tags          | etiquetas   |
| summary       | resumen     |
| description   | descripcion |
| image         | imagen      |
| price         | precio      |
| product       | producto    |
| gallerydir    | galeria     |
| date          | fecha       |
| modified      | modificado  |
| author        | autor       |
| lang          | idioma      |

Nota: tambien se acepta gallery_dir y directorio_galeria como variantes de gallerydir.
Nota: Pelican requiere Date para procesar el articulo. Puedes usar fecha y Date con el mismo valor para mantener consistencia en espanol.

## Ejemplo 1: Front matter en ingles

```md
Title: Pikachu Estilo Crochet
Date: 2026-04-24
Category: Pokemon
Tags: crochet, amigurumi, anime
Product: true
Slug: pikachu-crochet
Price: $15.00
Image: pikachu-crochet/01_Pikachu.png
GalleryDir: pikachu-crochet/
Summary: Amigurumi tejido a mano, ideal para regalo o coleccion.
```

## Ejemplo 2: Front matter en espanol

```md
titulo: Cruz imagen Jesus
fecha: 2026-04-24
Date: 2026-04-24
categoria: religiosas
etiquetas: jesus, colgar
producto: true
slug: cruz-jesus
precio: $5.00
imagen: religiosas/cruz-jesus/01_Cruz.png
galeria: religiosas/cruz-jesus/
resumen: Cruz decorativa impresa en 3D para colgar.
```

## Variaciones de producto (talla, color, modelo, etc.)

Cuando un producto tiene varias opciones con **precio y/o fotos distintas** (ej. tamano Grande/Pequeno), el formato plano de arriba no alcanza porque no soporta listas anidadas. Para esto, encabeza el archivo con un bloque YAML delimitado por `---`.

### Estructura basica

```md
---
titulo: Luffy Estilo Crochet
fecha: 2026-01-15
Date: 2026-01-15
categoria: onepiece
etiquetas: crochet, amigurumi, anime
producto: true
slug: luffy-crochet
resumen: Figura impresa 3D con estilo Luffy, disponible en dos tamanos.
variacion:
  nombre: Tamano
  lista:
    - titulo: Pequeno
      precio: $12.00
      imagen: onepiece/luffy-crochet/pequeno/01_Luffy.png
      galeria: onepiece/luffy-crochet/pequeno
    - titulo: Grande
      precio: $28.00
      imagen: onepiece/luffy-crochet/grande/04_Luffy.png
      galeria: onepiece/luffy-crochet/grande
---

## Descripcion

Texto del producto...
```

Ejemplo real en el repo: `content/productos/textura-crochet/onepeice/01-luffy-crochet.md`.

### Campos por variacion

| Campo     | Obligatorio | Para que sirve                                                             |
| --------- | ----------- | --------------------------------------------------------------------------- |
| `titulo`  | Si          | Texto del boton de seleccion (ej. "Grande").                                |
| `precio`  | Si          | Precio mostrado; tambien se usa en el filtro y el orden del catalogo.       |
| `imagen`  | No          | Imagen principal de esa variacion.                                          |
| `galeria` | No          | Carpeta de fotos propia de esa variacion (mismo formato que `galeria` general). |

No hace falta repetir `precio:`, `imagen:` ni `galeria:` a nivel general del producto — el sitio los toma automaticamente de la **primera** variacion de la lista.

### Varios grupos de variacion combinables (ej. Tamano + Personalizacion)

Cuando un producto necesita dos decisiones independientes (ej. elegir tamano Y elegir si se personaliza), `variacion:` puede ser una **lista de grupos** en vez de un solo grupo:

```yaml
variacion:
  - nombre: Tamaño
    lista:
      - titulo: Pequeño
        precio: $12.00
        imagen: onepiece/luffy-crochet/pequeño/01_Luffy.png
        galeria: onepiece/luffy-crochet/pequeño
      - titulo: Grande
        precio: $28.00
        imagen: onepiece/luffy-crochet/grande/04_Luffy.png
        galeria: onepiece/luffy-crochet/grande
  - nombre: Personalización
    lista:
      - titulo: Normal
      - titulo: Personalizado
        precio: +$1.00
```

- El **primer grupo de la lista** es el principal: sus precios son absolutos (igual que el caso de un solo grupo) y son los que definen imagen/galeria por defecto.
- Los **grupos siguientes** son aditivos: su `precio` (ej. `+$1.00` o `-$2.00`) se suma o resta sobre el total acumulado de los grupos anteriores. Si una opcion no define `precio` (ej. "Normal"), no agrega nada.
- El precio grande de arriba y el rango del catalogo se recalculan combinando todos los grupos (ej. Pequeño sin personalizar = $12.00, Grande + Personalizado = $29.00 → catalogo muestra "$12.00 - $29.00").
- En la pagina del producto aparece un selector por cada grupo; el cliente puede elegir una opcion de cada uno de forma independiente.

### Que hace el sitio automaticamente

- La **primera variacion de la lista** es la que se ve seleccionada al cargar la pagina (su precio, imagen y galeria son los que aparecen por defecto). El orden de `lista` define cual es esa.
- En el **catalogo**, la tarjeta del producto muestra el **rango de precio** (ej. "$12.00 - $28.00") cuando las variaciones tienen precios distintos.
- El **filtro de precio** y el **orden** (menor a mayor / mayor a menor) del catalogo consideran todos los precios de las variaciones, no solo el de la primera.

### Atributos extra que cambian segun la variacion (ej. altura, estilo, modelo)

Puedes agregar cualquier otro campo a una variacion ademas de los de la tabla de arriba, y mostrarlo en el cuerpo del producto para que cambie solo al elegir la variacion:

1. Agrega el campo en cada item de `lista`:

```yaml
    - titulo: Pequeño
      precio: $12.00
      altura: 10 cm
    - titulo: Grande
      precio: $28.00
      altura: 17 cm
```

2. En el cuerpo del Markdown, donde quieras mostrar ese valor, envuelvelo en un `<span>` con id `product-<nombre-del-campo>`, usando como valor inicial el de la **primera** variacion:

```md
- **Altura:** <span id="product-altura">10 cm</span>.
```

El sitio detecta el campo solo — no hace falta tocar plantillas ni JavaScript. Funciona con cualquier nombre de campo (`estilo`, `modelo`, `color`, `material`...), distinto en cada producto si lo necesitas.

## Ocultar productos en desarrollo (producto: false)

Agrega `producto: false` para que el producto no aparezca en el sitio ni en los listados, pero el archivo siga siendo auditado por `make audit-info`:

```md
titulo: Producto nuevo
fecha: 2026-06-28
Date: 2026-06-28
categoria: categoria-principal
producto: false
slug: nombre-del-producto
precio: $0.00
```

Tambien puedes ocultar solo una variacion especifica (ej. todavia no tiene fotos):

```yaml
variacion:
  nombre: Tamano
  lista:
    - titulo: Pequeno
      precio: $12.00
      galeria: categoria/producto/pequeno
    - titulo: Grande
      precio: $20.00
      galeria: categoria/producto/grande
      producto: false   # esta opcion no aparece como boton
```

## Auditoria de productos

El comando `make audit` revisa todos los productos activos y reporta:

- Campos requeridos faltantes (titulo, precio).
- Imagenes o galerias que no existen en disco.
- Imagenes que no son cuadradas (relacion 1:1 recomendada para fotos de producto).
- Nombre de archivo con espacios o caracteres no-ASCII.

```bash
make audit        # errores y avisos de productos activos (producto: true)
make audit-info   # igual + productos en desarrollo (producto: false) + campos opcionales
```

Los productos con `producto: false` solo aparecen en `make audit-info`, con todos sus avisos marcados como INFO para distinguirlos.

## Imagenes: formato recomendado

Usa siempre fotos **cuadradas (1:1)**, por ejemplo 1000×1000 px o 1200×1200 px. Esto garantiza que las tarjetas del catalogo y la galeria del producto se vean correctas sin recortes ni espacios en blanco.

Si una imagen no cumple la relacion 1:1, `make audit` muestra un aviso con las dimensiones exactas para que sea facil identificarla y recortarla.

Formatos soportados: JPG, PNG, WebP, AVIF. El sitio genera versiones WebP automaticamente con `make optimize-images`.

## Recomendaciones rapidas

- Usa `producto: true` para que aparezca en el catalogo; `producto: false` para productos en desarrollo.
- Mantiene una sola forma por archivo (todo EN o todo ES) para mayor orden, aunque mezclar tambien funciona.
- Si no defines `imagen` y existe `galeria` con imagenes, el sistema toma la primera automaticamente (en catalogo, inicio y pagina de producto).
- Las fotos deben ser cuadradas (1:1); usa `make audit` para verificarlo.

## Comando para regenerar

```bash
source .venv/bin/activate && make html
```
