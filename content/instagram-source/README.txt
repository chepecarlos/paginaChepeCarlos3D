Feed local para "Nuestros trabajos"

Modos soportados:

1. manual_urls (recomendado):
  - En `feed.json`, agrega `post_url` (o `instagram_url`) por item.
  - El script intenta descargar desde `post_url/media/?size=l` automaticamente.
  - Opcional: `image_url` para forzar imagen manual si falla la extraccion automatica.
  - Ejecuta `make instagram-feed-urls`.

2. profile_latest (experimental pero util):
  - En `feed.json`, define `mode: profile_latest` y agrega `username` con el usuario publico.
  - Tambien puedes ejecutarlo directo con `make instagram-feed-latest USERNAME=chepecarlos3d`.
  - El script consulta el endpoint web publico del perfil, reconstruye los `post_url` recientes y descarga sus imagenes.

3. local_files (compatibilidad):
  - En `feed.json`, define `mode: local_files` y usa `image` con archivos locales.
  - Ejecuta `make instagram-feed`.

Luego genera el sitio con `make html` o `make publish`.

Ejemplo mode manual_urls:

{
  "mode": "manual_urls",
  "max_items": 6,
  "items": [
    {
      "title": "Luffy amigurumi grande",
      "alt": "Luffy tejido a mano en crochet",
      "post_url": "https://www.instagram.com/p/XXXXXXXXXXX/"
    }
  ]
}

Ejemplo mode profile_latest:

{
  "mode": "profile_latest",
  "username": "chepecarlos3d",
  "max_items": 6,
  "items": []
}