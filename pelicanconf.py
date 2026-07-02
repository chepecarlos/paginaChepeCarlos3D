import os

AUTHOR = "ChepeCarlos"
SITENAME = "ChepeCarlos3D"
SITEDESCRIPTION = "Impresion 3D y fabricacion digital en San Miguel, El Salvador. Piezas geek y personalizadas con acabado profesional."
SITEURL = os.getenv("SITEURL", "http://127.0.0.1:8000/").rstrip("/")

PATH = "content"

TIMEZONE = "America/Mexico_City"

DEFAULT_LANG = "es"

# Tema personalizado
THEME = "theme"

# Rutas de contenido
STATIC_PATHS = ["images", "images_opt"]

# Pipeline de optimizacion de imagenes (fuente original intacta)
IMAGE_OPTIMIZATION_ENABLED = True
IMAGE_OPTIMIZATION_QUALITY = 72
IMAGE_OPTIMIZATION_SOURCE_DIR = "images"
IMAGE_OPTIMIZATION_DEST_DIR = "images_opt"
IMAGE_OPTIMIZATION_PRODUCTS_SUBDIR = "productos"
IMAGE_OPTIMIZATION_FORMATS = [".jpg", ".jpeg", ".png"]

# Plugins locales
PLUGIN_PATHS = ["plugins"]
PLUGINS = ["yaml_metadata", "auto_gallery"]

# Página de catálogo generada desde template
# → accesible en /catalogo/index.html
TEMPLATE_PAGES = {
    "catalog.html": "catalogo/index.html",
    "search.html": "buscar/index.html",
    "404.html": "404.html",
}

# Email de contacto (se muestra en páginas de producto)
# CONTACT_EMAIL = "ventas@chepecarlos3d.com" # por el momento no busco venden por email, talves el futuro

# Número de WhatsApp para cotizaciones (formato: 50369737593)
WHATSAPP_NUMBER = "50376161812"  # Modifica con tu número de WhatsApp

# Verificación de Google Search Console
# Pega aquí el valor del atributo content del meta tag que te da Google
# Ejemplo: "abc123XYZ..."
GOOGLE_SITE_VERIFICATION = ""

# Meta Pixel (Facebook Ads)
# Se activa solo si la variable de entorno FACEBOOK_PIXEL_ID está definida
# (evita mezclar tráfico de pruebas/devserver con los datos reales de Meta).
# En producción, defínela en Dokploy con el ID de Events Manager → Configuración del pixel.
FACEBOOK_PIXEL_ID = os.getenv("FACEBOOK_PIXEL_ID", "")

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
