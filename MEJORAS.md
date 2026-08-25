# Mejoras pendientes

Ideas y tareas de mejora identificadas para trabajar en futuras sesiones.

---

## Página de productos

### Alta prioridad

- [x] **Filtros por categoría y precio en el catálogo**
  Botones de categoría (Todos + una por categoría) y rangos de precio (Todos, Hasta $10, $10–$20, Más de $20).
  JS puro filtrando tarjetas visibles sin recargar la página. Implementado en `catalog.html` y `style.css`.

- [x] **Imagen de galería en tarjetas del catálogo**
  En `catalog.html` línea 16-18 solo se usa `product.image`.
  Si el producto no tiene `imagen:` pero sí tiene `galeria:`, la tarjeta sale sin foto.
  Agregar fallback a `auto_gallery[0]` igual que ya hace `article.html` líneas 6-8.

- [x] **Resumen visible en la tarjeta del catálogo**
  Las tarjetas no muestran el campo `resumen:` del producto.
  Agregar una línea de descripción breve en `catalog.html` para dar contexto antes del clic.

### Impacto medio

- [x] **Breadcrumb en la página de producto**
  El botón "Volver" usa `javascript:history.back()` — no funciona si el usuario llega de Google.
  Reemplazar con breadcrumb: `Inicio › [Categoría] › [Nombre del producto]`.
  Archivo: `article.html` línea 134.

- [x] **Productos relacionados al final del producto**
  Al terminar de ver un producto no hay dónde seguir navegando.
  Mostrar 3-4 productos de la misma categoría al final de `article.html`.

## Páginas de contenido pendientes

- [ ] **Historia / Nosotros** — Página que cuente quién es ChepeCarlos, cómo empezó, qué hace. Da confianza al comprador antes de cotizar.

- [ ] **Blog** — Sección de artículos (proceso de impresión, materiales, casos de uso). Ayuda con SEO y posiciona como experto.

- [ ] **Política de privacidad** — Requerida si se usan formularios, WhatsApp o Google Analytics. Página estática simple.

- [ ] **Política de devoluciones** — Qué cubre, qué no, plazos. Reduce fricción en la decisión de compra.

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

### Alta prioridad

- [x] **Sitemap.xml y robots.txt**
  Implementado: `plugins/sitemap.py` (nuevo plugin local, mismo patrón de signals que `auto_gallery.py`) genera `sitemap.xml` con todos los artículos y páginas al finalizar el build.
  `robots.txt` se genera desde `theme/templates/robots.txt` vía `TEMPLATE_PAGES` (igual que `catalog.html`), para poder usar `SITEURL` dinámico y apuntar al sitemap.

- [x] **Datos estructurados JSON-LD (`schema.org/Product`)**
  Implementado en `article.html` (bloque `head_extra`): emite `Product` con nombre, descripción, imágenes, categoría y marca.
  Usa `Offer` cuando el producto tiene un precio único, o `AggregateOffer` (lowPrice/highPrice/offerCount) cuando tiene variaciones con rango de precio. `offerCount` es el total real de combinaciones (producto de las opciones de cada grupo de variación).
  `availability` se deja fijo en `InStock` porque son piezas hechas por encargo, no hay control de stock real.
  Confirmado con Google Rich Results Test: "Se ha detectado 1 elemento válido". Quedan pendientes opcionales `review`/`aggregateRating` — no se agregan porque requerirían reseñas reales, que el sitio no tiene todavía.

### Impacto medio

- [ ] **Verificar el sitio en Google Search Console**
  (ver sección más abajo — pendiente ya documentado, se deja aquí como referencia cruzada de SEO)

## Analítica

- [ ] **Conectar Google Analytics (u otra herramienta)**
  `GOOGLE_ANALYTICS` está comentado en `publishconf.py` línea 22 y no hay ningún script de analítica en el theme.
  Sin esto no hay forma de saber qué productos generan más clics al botón de WhatsApp ni de dónde viene el tráfico.

## Rendimiento (Core Web Vitals)

- [x] ~~`width`/`height` explícitos en imágenes de producto~~ — **no hacía falta**
  Revisado: todas las imágenes del sitio (catálogo, producto, relacionados, blog, Instagram) ya están dentro de contenedores con `aspect-ratio: 1/1` fijo en `style.css` (`.product-img-wrap`, `.product-main-media`, `.product-detail-img`, `.product-thumb`, `.post-card-thumb`, `.social-mosaic-item`). El CSS ya reserva el espacio antes de que cargue la imagen, igual que harían `width`/`height`, así que no hay CLS real que corregir aquí.

- [x] **`fetchpriority="high"` en la imagen principal del producto**
  Implementado: `#product-main-image` en `article.html` ahora tiene `fetchpriority="high"` para que el navegador la priorice como candidata a LCP.

## Calidad de código

- [ ] **Tests automatizados y CI**
  `playwright` ya está como dependencia de dev pero no hay archivos de test ni `.github/workflows`.
  La lógica de precios/variaciones en `plugins/auto_gallery.py` (grupos combinables, precios relativos) es compleja y no tiene cobertura — un cambio ahí podría romper precios sin detectarse hasta producción.

---

### Pulido de UX

- [x] **Indicador de posición en la galería**
  El carousel no indica cuántas fotos hay ni en cuál se está (ej: `2 / 5`).
  Agregar puntos o contador en el JS del `article.html`.

- [x] **Swipe en móvil para la galería**
  La galería no responde a gestos táctiles.
  Agregar soporte de swipe con unos pocos eventos de touch en el JS del `article.html`.

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
