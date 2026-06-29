import re
from datetime import date, datetime
from pathlib import Path

from pelican import signals

try:
    import markdown as _md_module
    def _md_inline(text: str) -> str:
        """Convierte markdown a HTML inline (sin <p> envolvente)."""
        html = _md_module.markdown(str(text)).strip()
        if html.startswith("<p>") and html.endswith("</p>"):
            html = html[3:-4]
        return html
except ImportError:
    def _md_inline(text: str) -> str:
        return str(text)


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
    "variation": ("variacion",),
    "variation_name": ("variacion_nombre",),
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
    "variation_name",
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

        if canonical_name in ("date", "modified") and isinstance(value, date):
            # YAML front matter auto-parses bare dates (e.g. "fecha: 2026-01-15")
            # into date/datetime objects; Pelican's date processor expects a string.
            value = value.isoformat()

        if canonical_name == "product":
            # El parser plano de Pelican lee `producto: false` como la cadena
            # "false", que es truthy en Jinja2. Lo convertimos a booleano real.
            if isinstance(value, str):
                value = value.strip().lower() not in ("false", "0", "no", "")

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


def _parse_variation_options_flat(raw_value):
    """Convierte 'Grande:$28.00, Pequeño:$12.00' en una lista de dicts."""
    if not raw_value:
        return []

    options = []
    for chunk in str(raw_value).split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        titulo, _, precio = chunk.rpartition(":")
        if not titulo:
            titulo, precio = precio, ""
        options.append({"titulo": titulo.strip(), "precio": precio.strip()})
    return options


_VARIATION_RESERVED_KEYS = {
    "titulo", "title", "precio", "price",
    "galeria", "gallerydir", "gallery_dir", "imagen", "image",
    "producto", "product",
}


def _parse_variation_options_nested(raw_value):
    """Lee la forma YAML anidada: {nombre, lista: [{titulo, precio, galeria, imagen, ...}]}.

    Cualquier otra clave por variación (ej. "altura") se conserva tal cual,
    para que la plantilla pueda mostrarla y el JS la intercambie al elegir variante.
    """
    name = str(raw_value.get("nombre") or raw_value.get("name") or "").strip()
    entries = raw_value.get("lista") or raw_value.get("list") or []

    options = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        product_flag = entry.get("producto") if "producto" in entry else entry.get("product")
        if product_flag is not None:
            active = str(product_flag).strip().lower() not in ("false", "0", "no")
            if not active:
                continue
        titulo = str(entry.get("titulo") or entry.get("title") or "").strip()
        precio = str(entry.get("precio") or entry.get("price") or "").strip()
        galeria = entry.get("galeria") or entry.get("gallerydir") or entry.get("gallery_dir")
        imagen = entry.get("imagen") or entry.get("image")
        option = {"titulo": titulo, "precio": precio}
        if galeria:
            option["galeria"] = galeria
        if imagen:
            option["imagen"] = imagen
        for key, value in entry.items():
            if key.lower() not in _VARIATION_RESERVED_KEYS and value not in (None, ""):
                if isinstance(value, str):
                    value = _md_inline(value)
                option[key.lower()] = value
        options.append(option)

    return name, options


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

    variation_raw = metadata.get("variation")
    variation_groups = []

    if isinstance(variation_raw, list):
        # Varios grupos de variación combinables (ej. Tamaño + Personalización):
        # cada item de la lista es un grupo con la misma forma {nombre, lista}
        # que el caso de un solo grupo.
        for group_raw in variation_raw:
            if not isinstance(group_raw, dict):
                continue
            group_name, group_options = _parse_variation_options_nested(group_raw)
            if group_options:
                variation_groups.append({"nombre": group_name, "opciones": group_options})
    elif isinstance(variation_raw, dict):
        variation_name, variation_options = _parse_variation_options_nested(variation_raw)
        if variation_options:
            variation_groups.append({"nombre": variation_name, "opciones": variation_options})
            if variation_name and not metadata.get("variation_name"):
                metadata["variation_name"] = variation_name
                content.variation_name = variation_name
    else:
        variation_options = _parse_variation_options_flat(variation_raw)
        if variation_options:
            variation_groups.append({"nombre": metadata.get("variation_name", ""), "opciones": variation_options})

    if variation_groups:
        metadata["variation_groups"] = variation_groups
        content.variation_groups = variation_groups

        # Compatibilidad: el primer grupo (el principal, ej. Tamaño) se expone
        # también como "variaciones" (lista plana), igual que antes, para no
        # romper plantillas o lógica que solo conocían un grupo.
        primary_options = variation_groups[0]["opciones"]
        metadata["variaciones"] = primary_options
        content.variaciones = primary_options


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


def _build_ordered_gallery(content_root, gallery_dir, main_image=None):
    """Descubre las imágenes de gallery_dir y las ordena con main_image primero."""
    discovered_images = _discover_images(content_root, gallery_dir)
    if not discovered_images:
        return None, []

    if main_image:
        main_image = _normalize(_resolve_gallery_dir(main_image))

    if main_image and main_image in discovered_images:
        ordered_images = [main_image] + [
            image for image in discovered_images if image != main_image
        ]
    elif main_image:
        ordered_images = [main_image] + discovered_images
    else:
        ordered_images = discovered_images
        main_image = discovered_images[0]

    return main_image, ordered_images


def enrich_articles_with_auto_gallery(generator):
    content_root = Path(generator.settings.get("PATH", "content")).resolve()

    for article in generator.articles:
        gallery_dir = _meta_value(article, "gallerydir", "gallery_dir")
        if not gallery_dir:
            continue

        main_image, ordered_images = _build_ordered_gallery(
            content_root, gallery_dir, _meta_value(article, "image")
        )
        if not ordered_images:
            continue

        if not _meta_value(article, "image"):
            article.image = main_image
            article.metadata["image"] = main_image

        article.auto_gallery = ordered_images
        article.metadata["auto_gallery"] = ordered_images


def _price_to_float(value):
    if not value:
        return None
    cleaned = re.sub(r"[^\d.]", "", str(value))
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


_PRICE_NUMBER_RE = re.compile(r"[\d.]+")


def _format_price_like(reference, value):
    """Formatea `value` reusando el prefijo/sufijo de moneda de `reference`
    (ej. referencia '$17.00' y value 18.0 -> '$18.00')."""
    reference = str(reference)
    match = _PRICE_NUMBER_RE.search(reference)
    if not match:
        return f"{value:.2f}"
    prefix, suffix = reference[: match.start()], reference[match.end() :]
    return f"{prefix}{value:.2f}{suffix}"


def _resolve_relative_price(base_price, option_price):
    """Si `option_price` es relativo al precio base (ej. '+$1.00' o '-$2.00'),
    devuelve el precio absoluto resultante (base + delta); si no es relativo,
    devuelve `option_price` sin cambios."""
    text = str(option_price).strip()
    if not text.startswith(("+", "-")):
        return option_price

    base_value = _price_to_float(base_price)
    delta = _price_to_float(text)
    if base_value is None or delta is None:
        return option_price

    if text.startswith("-"):
        delta = -delta

    return _format_price_like(base_price, base_value + delta)


def enrich_variation_galleries(generator):
    """Resuelve imagen, galería y precios para cada grupo de variación.

    Soporta uno o varios grupos combinables (ej. Tamaño + Personalización).
    El primer grupo es el "principal": sus precios son absolutos (o heredan
    el precio base del producto si no definen uno propio), igual que un
    producto de variación simple. Los grupos siguientes son aditivos: su
    precio (ej. "+$1.00") se suma/resta sobre el total acumulado de los
    grupos anteriores, no sobre un precio base fijo — así "Personalizado"
    suma $1 al precio de la variación de Tamaño que esté activa.
    """
    content_root = Path(generator.settings.get("PATH", "content")).resolve()

    for article in generator.articles:
        variation_groups = getattr(article, "variation_groups", None)
        if not variation_groups:
            continue

        # Precio base del producto (campo "precio" del front matter), leído
        # antes de que las variaciones lo sobrescriban. Solo lo usa el grupo
        # principal como respaldo, y se recalcula en cada build para
        # reflejar cambios futuros al precio base.
        base_price = getattr(article, "price", None)

        for group_index, group in enumerate(variation_groups):
            options = group.get("opciones") or []

            for option in options:
                gallery_dir = option.get("galeria")
                if gallery_dir:
                    main_image, ordered_images = _build_ordered_gallery(
                        content_root, gallery_dir, option.get("imagen")
                    )
                    if ordered_images:
                        option["imagen"] = main_image
                        option["galeria_images"] = ordered_images
                    else:
                        img = option.get("imagen", "")
                        if not Path(img).suffix.lower() in IMAGE_EXTENSIONS:
                            option.pop("imagen", None)

                precio = option.get("precio")
                if group_index == 0:
                    if not precio:
                        precio = base_price
                    elif base_price:
                        resolved = _resolve_relative_price(base_price, precio)
                        if resolved != precio:
                            option["precio_relativo"] = precio
                        precio = resolved
                    option["precio"] = precio
                    option["precio_valor"] = _price_to_float(precio) or 0.0
                else:
                    # Grupo aditivo: su precio es un ajuste (+/-) sobre el
                    # total acumulado, no un precio fijo. Si no define
                    # precio, no agrega nada (ej. "Normal" = +$0.00).
                    if not precio:
                        option["precio_valor"] = 0.0
                        continue
                    text = str(precio).strip()
                    delta = _price_to_float(text) or 0.0
                    if text.startswith("-"):
                        delta = -delta
                    option["precio_relativo"] = text
                    option["precio_valor"] = delta

        primary_options = variation_groups[0].get("opciones") or []
        if not primary_options:
            continue

        # La primera opción de cada grupo es la que se ve "activa" al cargar
        # la página, así que su combinación define el precio/imagen/galería
        # que se muestran por defecto.
        first_primary = primary_options[0]
        reference_price = first_primary.get("precio") or base_price

        if reference_price:
            total_valor = first_primary.get("precio_valor", 0.0)
            for group in variation_groups[1:]:
                options = group.get("opciones") or []
                if options:
                    total_valor += options[0].get("precio_valor", 0.0)

            total_price = _format_price_like(reference_price, total_valor)
            article.price = total_price
            article.metadata["price"] = total_price

        if first_primary.get("imagen"):
            article.image = first_primary["imagen"]
            article.metadata["image"] = first_primary["imagen"]
        if first_primary.get("galeria_images"):
            article.auto_gallery = first_primary["galeria_images"]
            article.metadata["auto_gallery"] = first_primary["galeria_images"]

        # Rango de precio (menor a mayor) combinando el rango del grupo
        # principal con el ajuste mínimo/máximo de los grupos adicionales,
        # para mostrarlo en tarjetas de catálogo/listados.
        primary_values = [
            option.get("precio_valor")
            for option in primary_options
            if option.get("precio_valor") is not None
        ]
        if reference_price and primary_values:
            min_total = min(primary_values)
            max_total = max(primary_values)
            for group in variation_groups[1:]:
                deltas = [option.get("precio_valor", 0.0) for option in (group.get("opciones") or [])]
                if deltas:
                    min_total += min(deltas)
                    max_total += max(deltas)

            min_label = _format_price_like(reference_price, min_total)
            max_label = _format_price_like(reference_price, max_total)
            price_range = min_label if min_total == max_total else f"{min_label} - {max_label}"

            article.price_min = min_label
            article.price_max = max_label
            article.price_range = price_range
            article.metadata["price_min"] = min_label
            article.metadata["price_max"] = max_label
            article.metadata["price_range"] = price_range


def register():
    signals.readers_init.connect(register_reader_aliases)
    signals.content_object_init.connect(normalize_bilingual_metadata)
    signals.article_generator_finalized.connect(enrich_articles_with_auto_gallery)
    signals.article_generator_finalized.connect(enrich_variation_galleries)
    signals.generator_init.connect(_register_template_helpers)
