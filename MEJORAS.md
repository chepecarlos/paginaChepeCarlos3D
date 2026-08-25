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

## SEO y descubribilidad

### Alta prioridad

- [x] **Sitemap.xml y robots.txt**
  Implementado: `plugins/sitemap.py` (nuevo plugin local, mismo patrón de signals que `auto_gallery.py`) genera `sitemap.xml` con todos los artículos y páginas al finalizar el build.
  `robots.txt` se genera desde `theme/templates/robots.txt` vía `TEMPLATE_PAGES` (igual que `catalog.html`), para poder usar `SITEURL` dinámico y apuntar al sitemap.

- [x] **Datos estructurados JSON-LD (`schema.org/Product`)**
  Implementado en `article.html` (bloque `head_extra`): emite `Product` con nombre, descripción, imágenes, categoría y marca.
  Usa `Offer` cuando el producto tiene un precio único, o `AggregateOffer` (lowPrice/highPrice) cuando tiene variaciones con rango de precio.
  `availability` se deja fijo en `InStock` porque son piezas hechas por encargo, no hay control de stock real.

### Impacto medio

- [ ] **Verificar el sitio en Google Search Console**
  (ver sección más abajo — pendiente ya documentado, se deja aquí como referencia cruzada de SEO)

## Analítica

- [ ] **Conectar Google Analytics (u otra herramienta)**
  `GOOGLE_ANALYTICS` está comentado en `publishconf.py` línea 22 y no hay ningún script de analítica en el theme.
  Sin esto no hay forma de saber qué productos generan más clics al botón de WhatsApp ni de dónde viene el tráfico.

## Rendimiento (Core Web Vitals)

- [ ] **`width`/`height` explícitos en imágenes de producto**
  Ni `catalog.html` ni `article.html` los declaran, lo que causa layout shift (CLS) mientras cargan las imágenes.

- [ ] **`fetchpriority="high"` en la imagen principal del producto**
  La imagen candidata a LCP (`#product-main-image` en `article.html`) no tiene esta pista de prioridad de carga.

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
