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

## Flujo sugerido

1. Copia una opcion completa.
2. Guarda el archivo en content/productos/<categoria>/<slug>.md.
3. Ajusta imagen/galeria a la carpeta real.
4. Regenera el sitio con:

```bash
source .venv/bin/activate && make devserver
```
