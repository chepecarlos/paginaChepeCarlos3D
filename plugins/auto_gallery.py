from datetime import datetime
from pathlib import Path

from pelican import signals


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".svg", ".avif", ".gif"}


# Canonical field names used by templates plus Spanish aliases for content editing.
METADATA_ALIASES = {
    "title": ("titulo",),
    "category": ("categoria",),
    "tags": ("etiquetas",),
    "summary": ("resumen",),
    "description": ("descripcion",),
    "image": ("imagen",),
    "price": ("precio",),
    "product": ("producto",),
    "gallerydir": ("directorio_galeria", "gallery_dir", "galeria"),
    "slug": ("slug_es",),
    "date": ("fecha",),
    "modified": ("modificado",),
    "author": ("autor",),
    "lang": ("idioma",),
}


SAFE_DIRECT_ATTR_FIELDS = {
    "title",
    "summary",
    "description",
    "image",
    "price",
    "product",
    "gallerydir",
    "slug",
    "lang",
}


def _meta_value(article, *names):
    for name in names:
        value = getattr(article, name, None)
        if value:
            return value

    metadata = getattr(article, "metadata", {}) or {}
    for name in names:
        value = metadata.get(name)
        if value:
            return value

    return None


def _resolve_aliases(metadata, *names):
    for name in names:
        value = metadata.get(name)
        if value not in (None, ""):
            return value

        for alias in METADATA_ALIASES.get(name, ()):
            alias_value = metadata.get(alias)
            if alias_value not in (None, ""):
                return alias_value

    return None


def _normalize_reader_metadata(reader, metadata):
    if not metadata:
        return metadata

    normalized = dict(metadata)
    for canonical_name, aliases in METADATA_ALIASES.items():
        value = _resolve_aliases(normalized, canonical_name)
        if value in (None, ""):
            continue

        try:
            processed_value = reader.process_metadata(canonical_name, value)
        except Exception:
            processed_value = value

        normalized[canonical_name] = processed_value
        for alias in aliases:
            if normalized.get(alias) in (None, ""):
                normalized[alias] = processed_value

    return normalized


def _build_bilingual_reader(reader_class):
    if getattr(reader_class, "_bilingual_alias_support", False):
        return reader_class

    class BilingualReader(reader_class):
        _bilingual_alias_support = True

        def read(self, source_path):
            content, metadata = super().read(source_path)
            metadata = _normalize_reader_metadata(self, metadata)
            return content, metadata

    BilingualReader.__name__ = f"Bilingual{reader_class.__name__}"
    return BilingualReader


def register_reader_aliases(readers):
    for extension, reader_class in list(readers.reader_classes.items()):
        if reader_class is None:
            continue
        readers.reader_classes[extension] = _build_bilingual_reader(reader_class)


def normalize_bilingual_metadata(content):
    metadata = getattr(content, "metadata", None)
    if not metadata:
        return

    for canonical_name, aliases in METADATA_ALIASES.items():
        value = _resolve_aliases(metadata, canonical_name)
        if value in (None, ""):
            continue

        if canonical_name in ("date", "modified") and isinstance(value, str):
            # Pelican expects datetime-like values for ordering.
            try:
                value = datetime.fromisoformat(value.strip())
            except ValueError:
                pass

        metadata[canonical_name] = value
        if canonical_name in SAFE_DIRECT_ATTR_FIELDS:
            setattr(content, canonical_name, value)

        # Keep aliases in metadata so both styles can be used safely.
        for alias in aliases:
            if metadata.get(alias) in (None, ""):
                metadata[alias] = value


def _normalize(path_value):
    text = str(path_value).replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    return text.lstrip("/")


def normalize_media_path(path_value):
    if not path_value:
        return ""
    return _normalize(path_value)


def _is_external_or_data_url(path_value):
    return path_value.startswith(("http://", "https://", "data:", "//"))


def resolve_optimized_image_path(path_value, settings):
    if not path_value:
        return path_value

    normalized = normalize_media_path(path_value)
    if not normalized or _is_external_or_data_url(normalized):
        return path_value

    # Aplicar lógica de rutas cortas para productos
    if "images/productos/" not in normalized and not normalized.startswith("images/"):
        normalized = f"images/productos/{normalized}"

    source_dir = normalize_media_path(
        settings.get("IMAGE_OPTIMIZATION_SOURCE_DIR", "images")
    )
    dest_dir = normalize_media_path(
        settings.get("IMAGE_OPTIMIZATION_DEST_DIR", "images_opt")
    )
    optimize_enabled = settings.get("IMAGE_OPTIMIZATION_ENABLED", True)

    if not optimize_enabled:
        return normalized

    source_prefix = f"{source_dir}/"
    if not normalized.startswith(source_prefix):
        return normalized

    suffix = Path(normalized[len(source_prefix) :]).with_suffix(".webp")
    optimized_rel = normalize_media_path(Path(dest_dir) / suffix)

    content_root = Path(settings.get("PATH", "content")).resolve()
    optimized_fs = content_root / optimized_rel
    if optimized_fs.exists():
        return optimized_rel

    return normalized


def _attach_helpers_to_env(env, settings):
    def _resolve_image(path_value):
        return resolve_optimized_image_path(path_value, settings)

    def _resolve_gallery(paths):
        if not paths:
            return []
        return [_resolve_image(item) for item in paths]

    env.filters["optimized_image"] = _resolve_image
    env.filters["optimized_gallery"] = _resolve_gallery
    env.globals["resolve_image"] = _resolve_image
    env.globals["resolve_gallery"] = _resolve_gallery


def _register_template_helpers(generator):
    env = getattr(generator, "env", None)
    if env is None:
        return
    settings = getattr(generator, "settings", {})
    _attach_helpers_to_env(env, settings)


def _resolve_gallery_dir(gallery_dir):
    """
    Resuelve la ruta del directorio de galería.
    Si no contiene 'images/productos/', lo agrega automáticamente.
    Esto permite usar rutas cortas como 'onepiece/luffy-grande/'
    en lugar de 'images/productos/onepiece/luffy-grande/'
    """
    normalized = _normalize(gallery_dir)
    if not normalized or _is_external_or_data_url(normalized):
        return normalized

    # Si ya contiene la ruta completa, devolverla tal cual
    if "images/productos/" in normalized:
        return normalized

    # Si no contiene la ruta, agregarla automáticamente
    return f"images/productos/{normalized}"


def _discover_images(content_root, gallery_dir):
    resolved_dir = _resolve_gallery_dir(gallery_dir)
    gallery_path = (content_root / resolved_dir).resolve()
    if not gallery_path.exists() or not gallery_path.is_dir():
        return []

    files = []
    for item in sorted(
        gallery_path.iterdir(), key=lambda file_path: file_path.name.lower()
    ):
        if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
            files.append(_normalize(item.relative_to(content_root)))
    return files


def enrich_articles_with_auto_gallery(generator):
    content_root = Path(generator.settings.get("PATH", "content")).resolve()

    for article in generator.articles:
        gallery_dir = _meta_value(article, "gallerydir", "gallery_dir")
        if not gallery_dir:
            continue

        discovered_images = _discover_images(content_root, gallery_dir)
        if not discovered_images:
            continue

        main_image = _meta_value(article, "image")
        if main_image:
            # Resolver rutas cortas en la imagen principal
            resolved_main = _resolve_gallery_dir(main_image)
            main_image = _normalize(resolved_main)

        if main_image and main_image in discovered_images:
            ordered_images = [main_image] + [
                image for image in discovered_images if image != main_image
            ]
        elif main_image:
            ordered_images = [main_image] + discovered_images
        else:
            ordered_images = discovered_images
            article.image = ordered_images[0]
            article.metadata["image"] = ordered_images[0]

        article.auto_gallery = ordered_images
        article.metadata["auto_gallery"] = ordered_images


def register():
    signals.readers_init.connect(register_reader_aliases)
    signals.content_object_init.connect(normalize_bilingual_metadata)
    signals.article_generator_finalized.connect(enrich_articles_with_auto_gallery)
    signals.generator_init.connect(_register_template_helpers)
