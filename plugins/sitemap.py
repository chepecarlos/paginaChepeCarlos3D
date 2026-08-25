"""Genera sitemap.xml a partir de los artículos y páginas del sitio.

Se conecta a los mismos signals de finalizado de generador que usa
auto_gallery.py para recolectar contenido, y escribe el XML al finalizar
todo el build (signals.finalized), cuando OUTPUT_PATH ya existe.
"""
from pathlib import Path
from xml.sax.saxutils import escape

from pelican import signals

_collected = {"articles": [], "pages": []}


def _collect_articles(generator):
    _collected["articles"] = list(generator.articles)


def _collect_pages(generator):
    _collected["pages"] = list(generator.pages)


def _url_entry(loc, lastmod=None):
    lines = ["  <url>", f"    <loc>{escape(loc)}</loc>"]
    if lastmod:
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
    lines.append("  </url>")
    return "\n".join(lines)


def _catalog_url(siteurl, settings):
    for template, target in (settings.get("TEMPLATE_PAGES") or {}).items():
        if template == "catalog.html":
            return f"{siteurl}/{target.rsplit('index.html', 1)[0]}"
    return None


def generate_sitemap(pelican_object):
    settings = pelican_object.settings
    siteurl = settings.get("SITEURL", "").rstrip("/")
    output_path = Path(settings.get("OUTPUT_PATH", "output"))

    entries = [_url_entry(f"{siteurl}/")]

    catalog_url = _catalog_url(siteurl, settings)
    if catalog_url:
        entries.append(_url_entry(catalog_url))

    for article in _collected["articles"]:
        date_value = getattr(article, "modified", None) or getattr(article, "date", None)
        lastmod = date_value.date().isoformat() if date_value else None
        entries.append(_url_entry(f"{siteurl}/{article.url}", lastmod))

    for page in _collected["pages"]:
        date_value = getattr(page, "date", None)
        lastmod = date_value.date().isoformat() if date_value else None
        entries.append(_url_entry(f"{siteurl}/{page.url}", lastmod))

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )

    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "sitemap.xml").write_text(xml, encoding="utf-8")


def register():
    signals.article_generator_finalized.connect(_collect_articles)
    signals.page_generator_finalized.connect(_collect_pages)
    signals.finalized.connect(generate_sitemap)
