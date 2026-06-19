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

## Recomendaciones rapidas

- Usa product o producto en true para que aparezca en el catalogo.
- Mantiene una sola forma por archivo (todo EN o todo ES) para mayor orden, aunque mezclar tambien funciona.
- Si no defines image o imagen y existe gallerydir o galeria con imagenes, el sistema toma la primera automaticamente.

## Comando para regenerar

```bash
source .venv/bin/activate && make html
```
