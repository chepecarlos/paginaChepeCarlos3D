# Plantilla de producto

```md
titulo: Nombre del producto
fecha: 2026-04-24
Date: 2026-04-24
categoria: categoria-principal
etiquetas: etiqueta1, etiqueta2, etiqueta3
producto: true
slug: nombre-del-producto
precio: $0.00
imagen: categoria/nombre-del-producto/01_principal.png
galeria: categoria/nombre-del-producto/
resumen: Descripcion corta para tarjetas de catalogo y buscador.

## Descripcion

Escribe aqui la descripcion completa del producto.

## Caracteristicas

- **Material:**
- **Tamano:**
- **Color:**
- **Tiempo de produccion:**

## Recomendaciones

- Recomendacion 1.
- Recomendacion 2.
```

> **Formato de imagen recomendado:** usa fotos cuadradas (relacion 1:1, ej. 1000×1000 px). El audit avisa si alguna imagen no cumple este formato.

## Plantilla con variaciones (talla, color, modelo...)

Usa esta version si el producto tiene varias opciones con precio y/o fotos distintas (ver detalle completo en [GUIA_PRODUCTOS.md](GUIA_PRODUCTOS.md#variaciones-de-producto-talla-color-modelo-etc)):

```md
---
titulo: Nombre del producto
fecha: 2026-04-24
Date: 2026-04-24
categoria: categoria-principal
etiquetas: etiqueta1, etiqueta2, etiqueta3
producto: true
slug: nombre-del-producto
resumen: Descripcion corta para tarjetas de catalogo y buscador.
variacion:
  nombre: Tamano
  lista:
    - titulo: Pequeno
      precio: $0.00
      imagen: categoria/nombre-del-producto/pequeno/01_principal.png
      galeria: categoria/nombre-del-producto/pequeno
    - titulo: Grande
      precio: $0.00
      imagen: categoria/nombre-del-producto/grande/01_principal.png
      galeria: categoria/nombre-del-producto/grande
---

## Descripcion

Escribe aqui la descripcion completa del producto.

## Caracteristicas

- **Material:**
- **Tamano:**
- **Color:**
- **Tiempo de produccion:**

## Recomendaciones

- Recomendacion 1.
- Recomendacion 2.
```

La primera variacion de `lista` es la que se muestra por defecto al cargar la pagina (precio, imagen y galeria).

## Producto en desarrollo (oculto del catalogo)

Agrega `producto: false` para que el producto no aparezca en el sitio pero si en `make audit-info`:

```md
titulo: Producto nuevo
fecha: 2026-04-24
Date: 2026-04-24
categoria: categoria-principal
producto: false
slug: nombre-del-producto
precio: $0.00
```

Para ocultar solo una variacion especifica (ej. aun no tiene fotos):

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
      producto: false   # oculta solo esta opcion
```

## Flujo sugerido

1. Copia una opcion completa.
2. Guarda el archivo en content/productos/<categoria>/<slug>.md.
3. Coloca las imagenes en content/images/productos/<categoria>/<slug>/ (cuadradas, 1:1).
4. Audita el producto para detectar campos faltantes o imagenes incorrectas:

```bash
make audit-info   # muestra todo, incluido productos con producto: false
make audit        # solo errores y avisos de productos activos
```

5. Previsualiza el sitio:

```bash
source .venv/bin/activate && make devserver
```
