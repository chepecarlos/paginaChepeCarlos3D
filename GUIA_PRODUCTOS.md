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
Image: images/productos/pikachu-crochet/01_Pikachu.png
GalleryDir: images/productos/pikachu-crochet/
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
imagen: images/productos/religiosas/cruz-jesus/01_Cruz.png
galeria: images/productos/religiosas/cruz-jesus/
resumen: Cruz decorativa impresa en 3D para colgar.
```

## Recomendaciones rapidas

- Usa product o producto en true para que aparezca en el catalogo.
- Mantiene una sola forma por archivo (todo EN o todo ES) para mayor orden, aunque mezclar tambien funciona.
- Si no defines image o imagen y existe gallerydir o galeria con imagenes, el sistema toma la primera automaticamente.

## Comando para regenerar

```bash
source .venv/bin/activate && make html
```
