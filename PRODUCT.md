# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Mezcla sin perfil dominante, todos en El Salvador:

- **Fan que busca regalo**: anime, Pokémon, Marvel, cultura pop; llega desde Instagram/TikTok/Facebook, casi siempre en el celular, y cotiza por WhatsApp.
- **Coleccionista o fan para sí mismo**: piezas para colección o decoración.
- **Emprendedor o negocio**: piezas personalizadas o por volumen (llaveros, bases, souvenirs).

El trabajo común: encontrar una pieza (o describir una que no existe), ver precio y variaciones, y escribir por WhatsApp para cotizar.

## Product Purpose

Catálogo de productos de ChepeCarlos3D, impresión 3D y fabricación digital en San Miguel, El Salvador. El sitio no vende en línea: muestra piezas, precios y variaciones, y lleva la conversación a WhatsApp. Éxito = una cotización iniciada por WhatsApp.

## Positioning

- **Diseños a la medida**: productos que no existen se crean especialmente para el cliente.
- **Personalización**: nombres, colores y variaciones por pedido (con precio extra declarado por variación).
- **Textura crochet**: piezas impresas que imitan tejido/amigurumi.
- **Trato directo**: atención personal por WhatsApp, producción por pedido, entrega local y envíos según zona.

## Operating Context

- Contacto principal: WhatsApp (`WHATSAPP_NUMBER` en `pelicanconf.py`); también correo y teléfono en el pie.
- Redes: Instagram, TikTok, Facebook (`SOCIAL_LINKS`); feed de Instagram opcional en build.
- Para cotizar se pide: producto, cantidad, ciudad/zona, fecha requerida. Piezas personalizadas pueden requerir anticipo.
- Disponibilidad se confirma antes de cada pedido; tiempos varían por pieza.
- Meta Pixel activo en producción para anuncios.

## Capabilities and Constraints

- Sitio estático Pelican + Jinja2, servido por Nginx en Docker (Dokploy). Sin backend, sin carrito, sin pagos en línea.
- Contenido en Markdown en español; metadatos con alias ES/EN.
- Páginas: inicio, catálogo con filtros por categoría y precio, búsqueda, producto con galería/variaciones/relacionados/breadcrumb, blog, links, nosotros, contacto.
- Variaciones por producto con precio relativo; rango de precio calculado para el catálogo.
- Imágenes de producto optimizadas a WebP con fallback al original.
- Precios en USD.
- Crédito al diseñador original del modelo (`autor`) cuando aplica.

## Brand Commitments

- Nombre: **ChepeCarlos3D**. Voz cercana, en español, tuteando al cliente.
- Ubicación declarada: San Miguel, El Salvador.

## Evidence on Hand

- Fotos reales de producto: `content/images/productos/` (~37 productos, 14 categorías).
- Feed de Instagram: `content/instagram-source/`.
- Blog: `content/blog/` (materiales PLA/PETG).
- **Testimonios: aún no existen.** Reservar una zona para testimonios que se llenará después con reseñas reales; nunca inventarlos ni usar marcadores falsos como si fueran reales.
- No hay prensa, cifras de ventas ni clientes nombrados; no fabricarlos.

## Product Principles

1. Todo camino termina en WhatsApp: cada pieza debe facilitar iniciar la cotización.
2. Mostrar lo que es posible, no solo lo que hay: el catálogo es punto de partida para diseños a la medida.
3. Precio honesto y visible, incluido el costo de cada personalización.
4. Mobile primero: el visitante llega desde redes en el celular.
5. Dar crédito al diseñador original cuando el modelo no es propio.

## Accessibility & Inclusion

Público general en El Salvador navegando en celular, posiblemente con datos móviles limitados: imágenes ligeras y páginas rápidas.
