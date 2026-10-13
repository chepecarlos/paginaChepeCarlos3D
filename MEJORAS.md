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

## Limpieza de código (auditoría ponytail)

Hallazgos de sobre-ingeniería ordenados por impacto. Ninguno afecta funcionalidad actual.

- [ ] **Eliminar `tasks.py`** — 216 líneas que duplican el Makefile. El task `publish` crashea en runtime (no define `ssh_port`/`ssh_user`). Deploy real es Dokploy/Docker. Nadie usa `inv`.

- [ ] **Quitar deps `invoke` y `livereload`** — Solo las usa `tasks.py`. Al borrarlo quedan huérfanas. Actualizar `pyproject.toml` y regenerar `uv.lock`.

- [ ] **Quitar `playwright` de deps de desarrollo** — No existe ningún test Playwright en el repo. (`pyproject.toml` `[dependency-groups] dev`)

- [ ] **Borrar filtros Jinja muertos en `auto_gallery.py`** — `optimized_image`, `optimized_gallery` y el global `resolve_gallery` (líneas 332–335) nunca se usan en plantillas. Las templates solo llaman `resolve_image`.

- [ ] **Borrar 3 settings muertos en `pelicanconf.py`** — `IMAGE_OPTIMIZATION_QUALITY`, `IMAGE_OPTIMIZATION_PRODUCTS_SUBDIR` e `IMAGE_OPTIMIZATION_FORMATS` (líneas 24–26) solo las leía `tasks.py`.

- [ ] **Eliminar target `github` del Makefile** — `ghp-import` no está en las deps; deploy es Dokploy. Borrar vars `GITHUB_PAGES_*` (líneas 14–15) y el target `github` (líneas 145–147).

- [ ] **Consolidar funciones duplicadas entre scripts de imágenes** — `normalize_relpath`, `parse_formats`, `iter_source_images` y `source_to_target` están copiadas palabra por palabra en `optimize_images.py` y `report_image_savings.py` (~45 líneas). Extraer a `scripts/image_utils.py`.

- [ ] **Importar `ALIASES` desde el plugin en `audit_products.py`** — `ALIASES` (líneas 38–51) duplica `METADATA_ALIASES` de `auto_gallery.py` y se mantiene en sync a mano. Importar directamente o mover a módulo compartido.

- [ ] **Desactivar templates Pelican sin uso** — `archives.html`, `authors.html`, `author.html` y `period_archives.html` generan rutas muertas. Agregar en `pelicanconf.py`:
  ```python
  ARCHIVES_SAVE_AS = ""
  AUTHORS_SAVE_AS = ""
  AUTHOR_SAVE_AS = ""
  ```

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
