AUTHOR = "ChepeCarlos"
SITENAME = "ChepeCarlos3D"
SITEDESCRIPTION = "Productos de calidad para tu día a día"
SITEURL = ""

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
# Descomenta y modifica para activarlo:
# CONTACT_EMAIL = 'ventas@tuemprendimiento.com'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
