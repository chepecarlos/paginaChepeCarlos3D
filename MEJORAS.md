# Mejoras pendientes

Ideas y tareas de mejora identificadas para trabajar en futuras sesiones.

---

## Páginas de contenido pendientes

- [ ] **Política de privacidad** — Requerida si se usan formularios, WhatsApp o Google Analytics. Página estática simple.

- [ ] **Política de devoluciones** — Qué cubre, qué no, plazos. Reduce fricción en la decisión de compra.

- [ ] **Logo o foto de cuenta en `/links/`** — Hoy `links.html` (`.links-avatar`) muestra solo la inicial de `SITENAME`. Reemplazar por un `<img>` con el logo o foto de perfil (ej. `theme/static/images/avatar.webp`).

---

## Google Search Console

- [ ] **Verificar el sitio en Google Search Console**
  La infraestructura ya está lista: variable `GOOGLE_SITE_VERIFICATION` en `pelicanconf.py` y meta tag condicional en `base.html` línea 24.
  Pasos pendientes:
  1. Entrar a [search.google.com/search-console](https://search.google.com/search-console)
  2. Agregar la propiedad con la URL del sitio (método "Prefijo de URL")
  3. Elegir verificación por "Etiqueta HTML" y copiar el valor del atributo `content`
  4. Pegarlo en `pelicanconf.py`: `GOOGLE_SITE_VERIFICATION = "abc123XYZ..."`
  5. Desplegar el sitio y hacer clic en "Verificar" en Search Console

---

## Meta Pixel (Facebook Ads)

Pixel `958042070611307` integrado en `base.html` (`FACEBOOK_PIXEL_ID` en `pelicanconf.py`). Eventos activos: `PageView`, `ViewContent` (páginas de producto, en `article.html`), `Contact` (clic en cualquier botón/link de WhatsApp, listener delegado en `base.html`). Confirmado en Events Manager que `PageView` y `ViewContent` llegan por "Navegador".

- [ ] **Confirmar que llega el evento `Contact`** — no apareció en el primer test porque no se hizo clic en WhatsApp durante la prueba. Repetir el test haciendo clic en el botón flotante o el de la página de producto y verificar en Events Manager.

- [ ] **Confirmar que la API de Conversiones (gateway gratuito de Meta) está activa** — se eligió la opción "Realiza la configuración con Meta" (gratis, solo eventos web) en vez de Stape. En el primer test, `PageView` y `Ver contenido` solo mostraban integración "Navegador", sin fila "Servidor". Revisar la configuración del pixel (¿quedó "API de conversiones: Conectada"?) y repetir el test tras desplegar a producción.

- [ ] **Marcar `Contact` como evento prioritario** en Events Manager (máx. 8 eventos prioritarios) — es la conversión real del negocio al no haber checkout online.

- [ ] **Verificar el dominio** en Meta Business Settings → Marca de la empresa → Dominios, para mejorar atribución cuando el navegador bloquea cookies de terceros.

---

## SEO y descubribilidad

- [ ] **Verificar el sitio en Google Search Console**
  (ver sección más arriba — pendiente ya documentado, se deja aquí como referencia cruzada de SEO)

## Analítica

- [ ] **Conectar Google Analytics (u otra herramienta)**
  `GOOGLE_ANALYTICS` está comentado en `publishconf.py` línea 22 y no hay ningún script de analítica en el theme.
  Sin esto no hay forma de saber qué productos generan más clics al botón de WhatsApp ni de dónde viene el tráfico.

## Calidad de código

- [ ] **Tests automatizados y CI**
  `playwright` ya está como dependencia de dev pero no hay archivos de test ni `.github/workflows`.
  La lógica de precios/variaciones en `plugins/auto_gallery.py` (grupos combinables, precios relativos) es compleja y no tiene cobertura — un cambio ahí podría romper precios sin detectarse hasta producción.

---

## Limpieza de código (auditoría ponytail, actualizada 2026-10-13)

Hallazgos de sobre-ingeniería ordenados por impacto (mayor recorte primero). Ninguno afecta funcionalidad actual. Total posible: ~790 líneas y 3 dependencias menos.

- [ ] **Eliminar `tasks.py` y las deps `invoke` y `livereload`** (~-215 líneas) — Duplica el Makefile. El task `publish` crashea en runtime (no define `ssh_port`/`ssh_user`). Deploy real es Dokploy/Docker. Nadie usa `inv`. Al borrarlo, quitar `invoke` y `livereload` de `pyproject.toml` y regenerar `uv.lock`.

- [ ] **Instagram: dejar solo el modo `manual_urls`** (~-200 líneas) — `content/instagram-source/feed.json` solo usa `manual_urls`. Los modos `profile_latest` y `local_files` están muertos: borrar `fetch_profile_latest_items`, `fetch_json`, `INSTAGRAM_APP_ID`, `normalize_items`, `copy_images`, `discover_source_images`, las ramas lista/dict de `load_manifest`, los args `--mode`/`--username` y los targets `instagram-feed-urls`/`instagram-feed-latest` del Makefile. (`scripts/sync_instagram_feed.py`)

- [ ] **Reemplazar `report_image_savings.py` por `du`** (~-140 líneas) — El target `optimize-images-report` puede ser solo `du -sh content/images/productos content/images_opt/productos`. El script actual además no cuenta las `.thumb.webp`. Esto también elimina las funciones duplicadas con `optimize_images.py` (`normalize_relpath`, `parse_formats`, `iter_source_images`, `source_to_target`), así que ya no hace falta crear `scripts/image_utils.py`.

- [ ] **Quitar el archivo de estado `.optimize_state.json`** (~-40 líneas) — En `scripts/optimize_images.py`, `load_state`/`save_state`/`source_signature` y el manejo de `state` en `cleanup_orphaned_webp` se reemplazan comparando fechas: `target.stat().st_mtime >= source.stat().st_mtime` (como hace make). Si cambia la calidad o el tamaño, para eso está `--force`.

- [ ] **Limpiar boilerplate de Pelican en el Makefile** (~-35 líneas) — Borrar el target `github` y las vars `GITHUB_PAGES_*` (`ghp-import` no está en deps; deploy es Dokploy), además de `serve-global`, `devserver-global`, `regenerate`, `install-frozen`, `instagram-feed-build`, las opciones `RELATIVE`/`DEBUG` y sus líneas del `help`.

- [ ] **Borrar el formato plano de variaciones** (~-30 líneas) — Ningún producto usa `variacion: Grande:$28, Pequeño:$12`; todos usan el YAML anidado. Borrar `_parse_variation_options_flat`, la rama `else` en `normalize_bilingual_metadata` y el alias `variation_name`/`variacion_nombre`. (`plugins/auto_gallery.py`)

- [ ] **Desactivar templates Pelican sin uso** (~-40 líneas) — Borrar `archives.html`, `authors.html` y `period_archives.html`, y agregar en `pelicanconf.py`:
  ```python
  ARCHIVES_SAVE_AS = ""
  AUTHORS_SAVE_AS = ""
  ```
  **Ojo:** `author.html` ya NO es código muerto — `article.html:233` enlaza a `article.author.url`. No poner `AUTHOR_SAVE_AS = ""`.

- [ ] **Simplificar helpers de `auto_gallery.py`** (~-25 líneas)
  - Fusionar `_normalize` y `normalize_media_path` (hacen lo mismo).
  - `_resolve_gallery_dir` repite la lógica de rutas cortas de `resolve_optimized_image_path`; dejar una sola.
  - Quitar el `try/except ImportError` de `markdown`: es dependencia fija vía `pelican[markdown]`.
  - Meter `_attach_helpers_to_env` dentro de `_register_template_helpers` (tiene un solo caller).
  - Borrar los filtros Jinja sin uso `optimized_image`, `optimized_gallery` y el global `resolve_gallery`; las plantillas solo usan `resolve_image`, `resolve_thumb` y `price_value`.
  - Quitar `"gallery_dir"` de `_meta_value(article, "gallerydir", "gallery_dir")`: el alias ya se normaliza antes.

- [ ] **Quitar settings `IMAGE_OPTIMIZATION_*` de `pelicanconf.py`** (~-15 líneas) — `QUALITY`, `PRODUCTS_SUBDIR` y `FORMATS` solo las leía `tasks.py`. `ENABLED`, `SOURCE_DIR` y `DEST_DIR` las lee el plugin, pero nunca cambian y el Makefile igual tiene `images`/`images_opt` escritos a mano. Pasarlas a constantes en el plugin.

- [ ] **Quitar argumentos sin uso de `optimize_images.py`** (~-25 líneas) — `--content-path`, `--source-dir`, `--dest-dir`, `--formats` y `parse_formats`: el Makefile siempre pasa los valores por defecto. Pasarlos a constantes; los targets quedan como `"$(PY)" scripts/optimize_images.py [--force]`.

- [ ] **Quitar feeds Atom de `publishconf.py`** (~-6 líneas) — `FEED_ALL_ATOM` y `CATEGORY_FEED_ATOM` generan feeds que ninguna plantilla enlaza. Borrar también los comentarios de DISQUS/GOOGLE_ANALYTICS.

- [ ] **Quitar `playwright` de deps de desarrollo** — No existe ningún test Playwright. Si se hace la tarea de "Tests automatizados y CI", decidir ahí si vuelve. (`pyproject.toml` `[dependency-groups] dev`)

- [ ] **Importar del plugin en lugar de copiar** (~-20 líneas) — `ALIASES` en `scripts/audit_products.py` duplica `METADATA_ALIASES`, y `_price_to_float` en `scripts/check_dolibarr_prices.py` duplica el del plugin. Importar ambos desde `plugins/auto_gallery.py`.

- [ ] **Simplificar `_catalog_url` en `plugins/sitemap.py`** (-4 líneas) — El bucle sobre `TEMPLATE_PAGES` se reemplaza por `(settings.get("TEMPLATE_PAGES") or {}).get("catalog.html")`.

- [ ] **Verificar doble resolución de aliases** (~-20 líneas, posible) — `normalize_bilingual_metadata` vuelve a resolver los aliases que `BilingualReader` ya resolvió al leer. Si se confirma que sobra, dejar solo la normalización de mayúsculas y el parseo de variaciones. Hacer `make html` antes y después y comparar `output/` (`diff -r`).

---

## Contenido de productos (revisión 2026-10-08)

Detectado al corregir la ortografía; son datos, no ortografía, así que no se cambiaron sin confirmar.

### Resúmenes copiados de otro producto

- [ ] **Alcancía Pokébola Grande** (`productos/alcancia/pokemon/01-alcancia-pokebola-grande.md`) — el `resumen` dice "estilo de TNT".
- [ ] **Alcancía Pokébola Pequeña** (`productos/alcancia/pokemon/01-alcancia-pokebola.md`) — el `resumen` dice "estilo de TNT".
- [ ] **Dragón Esquelético Articulable** (`productos/medieval/01-dragon-esqueletico-articulable.md`) — el `resumen` habla de una alcancía Masterbola de Pokémon.
- [ ] **Copa Mundial Tamaño Real** (`productos/mundial-futbol/01-copa-grande.md`) — el `resumen` habla de Goku y Dragon Ball.
- [ ] **Base de QR** (`productos/emprendimiento/01-base-qr.md`) — el `resumen` habla de una flor de lirio.

### Precio de personalización contradictorio

- [ ] **Definir si la personalización cuesta $1.00 o $1.50** — el texto de "Características" dice $1.50 pero la variación cobra `+$1.00` en: Batman, Goku, Pikachu, Mewtwo, Luffy, Zoro, Chopper, Kuromi, Deadpool grande, Copa Mundial, Muñeco de nieve y Lámpara de Lirio.

### Contenido incompleto

- [ ] **Base para llaveros** (`productos/emprendimiento/03-base-llavero.md`) — `precio: ???`.
- [ ] **Cruz imagen Jesús** (`productos/religiosas/cruz-jesus.md`) — sin descripción.
- [ ] **Lámpara de Lirio** (`productos/iluminaria/lampara-lirio.md`) — la descripción es solo "...".

---

## Diseño y accesibilidad (auditoría impeccable 2026-10-08)

- [ ] **Crear `DESIGN.md`** (`/impeccable document`) — documentar paleta, tipografía y componentes actuales; hoy hay ~127 colores escritos directo en `style.css` en vez de usar variables (`#334155`, `#0c2132`, `#113a56`, varios `rgba(...)`).
- [ ] **Íconos de la barra de ventajas** — `index.html` usa emojis (📦 ✨ 📍 💬) mientras el resto del sitio usa íconos SVG. Reemplazarlos por SVG del mismo estilo.
- [ ] **Zona de testimonios** — reservada en `PRODUCT.md`; llenar con reseñas reales cuando se consigan (no usar testimonios inventados).
