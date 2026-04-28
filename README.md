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
