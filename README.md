# ChepeCarlos3D

Sitio estatico con Pelican para catalogo y contenido de ChepeCarlos3D.

## Guia rapida de productos

Para crear productos con atributos en espanol o ingles, revisa:

- [GUIA_PRODUCTOS.md](GUIA_PRODUCTOS.md)

## Docker para Dokploy

Este repositorio incluye una dockerizacion multi-stage:

- `Dockerfile`: genera el sitio con Pelican y lo sirve con Nginx.
- `docker-compose.yml`: flujo local equivalente al despliegue.
- `.dockerignore`: reduce el contexto de build.

### Variables de build

- `SITEURL`: URL publica final (ejemplo: `https://tu-dominio.com`).
- `INSTAGRAM_SYNC`: `1` para sincronizar feed de Instagram durante build, `0` para omitirlo.

Recomendado en Dokploy:

- `SITEURL=https://tu-dominio.com`
- `INSTAGRAM_SYNC=0`

Si activas `INSTAGRAM_SYNC=1`, el build dependera de acceso de red a Instagram y puede fallar por limites temporales (HTTP 429).

## Deploy en Dokploy

1. Crea un proyecto tipo Dockerfile (o Compose) apuntando a este repositorio.
2. Si usas Dockerfile, establece:
	- Dockerfile path: `Dockerfile`
	- Port: `80`
	- Build args: `SITEURL` y `INSTAGRAM_SYNC`
3. Configura dominio y HTTPS en Dokploy.
4. Despliega.

El contenedor final sirve archivos estaticos desde Nginx en el puerto `80`.

## Prueba local con Docker Compose

```bash
SITEURL=http://localhost:8000 INSTAGRAM_SYNC=0 docker compose up --build
```

Luego abre `http://localhost:8000`.

## Pipeline de imagenes optimizadas

El sitio conserva los originales en `content/images/` y genera versiones WebP en `content/images_opt/`.

- Calidad por defecto: `72` (rango sugerido 70-75).
- Modo incremental por defecto: solo reprocesa imagenes nuevas o modificadas.
- Modo completo: usa `--force` para reprocesar todo.

### Comandos utiles

```bash
# Optimizar solo cambios (incremental)
make optimize-images

# Reprocesar todo
make optimize-images-force

# Ver reporte de ahorro total (original vs WebP)
make optimize-images-report
```

Tambien se ejecuta automaticamente en `make html` y en tareas Invoke (`build`, `rebuild`, `regenerate`, `preview`, `publish`).

### Configuracion

En `pelicanconf.py`:

- `IMAGE_OPTIMIZATION_ENABLED`
- `IMAGE_OPTIMIZATION_QUALITY`
- `IMAGE_OPTIMIZATION_SOURCE_DIR`
- `IMAGE_OPTIMIZATION_DEST_DIR`
- `IMAGE_OPTIMIZATION_PRODUCTS_SUBDIR`
- `IMAGE_OPTIMIZATION_FORMATS`

### Fallback automatico

Las plantillas intentan usar `images_opt/*.webp` cuando existe archivo optimizado. Si no existe, usan la imagen original sin romper rutas.

### Troubleshooting

- Si no se genera WebP, verifica que `Pillow` este instalado.
- Si una imagen no tiene version optimizada, el sitio mostrara automaticamente la original.
- El pipeline no borra ni muta archivos originales en `content/images/`.
