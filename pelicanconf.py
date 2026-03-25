import os

AUTHOR = "ChepeCarlos"
SITENAME = "ChepeCarlos3D"
SITEDESCRIPTION = "Productos de calidad para tu día a día"
SITEURL = os.getenv("SITEURL", "http://127.0.0.1:8000/").rstrip("/")

PATH = "content"

TIMEZONE = "America/Mexico_City"

DEFAULT_LANG = "es"

# Tema personalizado
THEME = "theme"

# Rutas de contenido
STATIC_PATHS = ["images"]

# Plugins locales
PLUGIN_PATHS = ["plugins"]
PLUGINS = ["auto_gallery"]

# Página de catálogo generada desde template
# → accesible en /catalogo/index.html
TEMPLATE_PAGES = {
    "catalog.html": "catalogo/index.html",
    "search.html": "buscar/index.html",
}

# Email de contacto (se muestra en páginas de producto)
# CONTACT_EMAIL = "ventas@chepecarlos3d.com" # por el momento no busco venden por email, talves el futuro

# Número de WhatsApp para cotizaciones (formato: 50369737593)
WHATSAPP_NUMBER = "50369737593"  # Modifica con tu número de WhatsApp

# Redes sociales en barra principal
# Completa cada URL para mostrar su botón en el header
SOCIAL_LINKS = {
    "instagram": "https://www.instagram.com/chepecarlos3d",
    "tiktok": "https://www.tiktok.com/@chepecarlos3d",
    "facebook": "https://www.facebook.com/profile.php?id=61559249050146",
}

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
