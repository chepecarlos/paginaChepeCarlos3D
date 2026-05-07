# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto

Sitio estático con [Pelican](https://getpelican.com/) para el catálogo de productos de ChepeCarlos3D — impresión 3D en El Salvador. El contenido se escribe en Markdown, el motor genera HTML estático, y el contenedor Docker sirve el resultado con Nginx.

## Comandos frecuentes

```bash
# Instalar dependencias (usa uv)
make install

# Servidor local con recarga automática
make devserver

# Generar sitio estático (incluye optimización de imágenes)
make html

# Optimizar imágenes de productos (incremental)
make optimize-images

# Reprocesar todas las imágenes
make optimize-images-force

# Reporte de ahorro de espacio original vs WebP
make optimize-images-report

# Generar para producción
make publish
```

Prueba local con Docker:
```bash
SITEURL=http://localhost:8000 INSTAGRAM_SYNC=0 docker compose up --build
```

## Arquitectura

```
content/productos/<categoria>/<slug>.md   ← artículos de productos
content/images/productos/<categoria>/     ← imágenes originales
content/images_opt/productos/<categoria>/ ← WebP generados por optimize_images.py
theme/templates/                          ← plantillas Jinja2 personalizadas
plugins/auto_gallery.py                   ← plugin local (galería + aliases bilingues)
scripts/                                  ← optimize_images, report_image_savings, sync_instagram_feed
pelicanconf.py                            ← configuración de desarrollo
publishconf.py                            ← configuración de producción (extiende pelicanconf.py)
```

**Plugin `auto_gallery`**: hace tres cosas a la vez —
1. Registra aliases en español para los metadatos (ver tabla en `GUIA_PRODUCTOS.md`).
2. Descubre automáticamente las imágenes del directorio `gallerydir` y las expone como `article.auto_gallery`.
3. Expone los filtros Jinja2 `optimized_image` y `optimized_gallery` para servir WebP cuando existen, o la imagen original como fallback.

**Rutas cortas**: en el front matter se puede escribir `galeria: onepiece/luffy/` en lugar de `images/productos/onepiece/luffy/`; el plugin resuelve la ruta completa automáticamente.

**Páginas de catálogo y búsqueda**: se generan desde `TEMPLATE_PAGES` (`catalog.html` → `/catalogo/index.html`, `search.html` → `/buscar/index.html`), no como artículos normales de Pelican.

## Crear o editar un producto

1. Copia la plantilla de `PLANTILLA_PRODUCTO.md`.
2. Guarda el archivo en `content/productos/<categoria>/<slug>.md`.
3. Coloca las imágenes en `content/images/productos/<categoria>/<slug>/`.
4. Ejecuta `make devserver` para previsualizar.

Los campos del front matter pueden estar en español o inglés (ver `GUIA_PRODUCTOS.md`). **Siempre incluye `Date:` además de `fecha:`** porque Pelican lo requiere internamente para procesar el artículo.

## Despliegue

El build de producción se realiza con Dokploy apuntando al `Dockerfile` de este repositorio. Variables de entorno relevantes:
- `SITEURL` — URL pública final (obligatoria en producción).
- `INSTAGRAM_SYNC` — `0` por defecto; `1` sincroniza el feed durante el build (puede fallar por rate-limiting de Instagram).
