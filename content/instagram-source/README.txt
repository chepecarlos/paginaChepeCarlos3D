Feed para "Trabajos recientes" (home)

Ejecuta `make instagram-feed` (también corre en cada `make html`), revisa el home,
y haz commit de content/images/instagram/, content/images_opt/instagram/ y
theme/templates/partials/instagram_feed_items.html para que Dokploy lo despliegue.

== Modo API (automático: trae los últimos 6 posts) ==

Si existe INSTAGRAM_TOKEN en `.env` (o como variable de entorno), el script usa la
API oficial de Instagram: toma los últimos posts, usa el texto del post como `alt`
y, en Reels, la portada. feed.json se ignora.

Conseguir el token (una sola vez; la cuenta debe ser Empresa o Creador):
1. https://developers.facebook.com/apps → Crear app → caso de uso
   "Administrar mensajes y contenido en Instagram".
2. En la app: Instagram → "Configuración de la API con inicio de sesión de Instagram"
   → "Generar tokens de acceso" → Agregar cuenta → inicia sesión con @chepecarlos3d.
3. Copia el token y pégalo en `.env` (copia `.env.example`): INSTAGRAM_TOKEN=IGAA...

El token dura 60 días y el script lo renueva y guarda en `.env` en cada corrida
(Instagram solo lo renueva si tiene más de 24 h). Basta con correr
`make instagram-feed` al menos una vez cada ~50 días; si vence, repite el paso 2.

== Modo manual (sin token) ==

1. En `feed.json`, agrega un item por post con su `post_url` (máx. 6).
   - `title` / `alt` (opcional pero recomendado): describe la pieza; si falta queda "Trabajo destacado N".
   - `image_url` (opcional): fuerza una imagen si falla la descarga automática.

El script descarga desde `post_url/media/?size=l` y, si falla, intenta con el og:image del post.
Si alguna descarga falla, las fotos actuales no se tocan.
Con `items` vacío, el home muestra fotos de productos.

Ejemplo:

{
  "max_items": 6,
  "items": [
    {
      "title": "Luffy amigurumi grande",
      "alt": "Luffy tejido a mano en crochet",
      "post_url": "https://www.instagram.com/p/XXXXXXXXXXX/"
    }
  ]
}
