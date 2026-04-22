from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = BASE_DIR / "content" / "instagram-source"
SOURCE_MANIFEST = SOURCE_DIR / "feed.json"
PUBLIC_DIR = BASE_DIR / "content" / "images" / "instagram"
PUBLIC_MANIFEST = PUBLIC_DIR / "feed.json"
PARTIAL_PATH = (
    BASE_DIR / "theme" / "templates" / "partials" / "instagram_feed_items.html"
)
MAX_ITEMS = 6
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
HTTP_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
INSTAGRAM_APP_ID = "936619743392459"


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except urllib.error.URLError as error:
        raise ValueError(f"No se pudo leer la URL {url}: {error}") from error


def fetch_json(url: str, extra_headers: dict[str, str] | None = None) -> dict:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }
    if extra_headers:
        headers.update(extra_headers)

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            payload = response.read().decode(charset, errors="replace")
    except urllib.error.HTTPError as error:
        if error.code == 429:
            raise ValueError(
                "Instagram limito temporalmente el acceso al perfil publico (HTTP 429). "
                "Espera unos minutos o usa el modo manual_urls con post_url."
            ) from error
        raise ValueError(f"No se pudo leer la URL {url}: HTTP {error.code}") from error
    except urllib.error.URLError as error:
        raise ValueError(f"No se pudo leer la URL {url}: {error}") from error

    try:
        return json.loads(payload)
    except json.JSONDecodeError as error:
        raise ValueError(f"La URL {url} no devolvio JSON valido.") from error


def post_media_url(post_url: str) -> str:
    parsed = urllib.parse.urlparse(post_url)
    clean = parsed._replace(query="", fragment="")
    base = urllib.parse.urlunparse(clean).rstrip("/")
    return f"{base}/media/?size=l"


def resolve_image_url_from_post(post_url: str) -> str:
    page = fetch_text(post_url)

    patterns = [
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
        r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
    ]

    for pattern in patterns:
        match = re.search(pattern, page, flags=re.IGNORECASE)
        if match:
            return html.unescape(match.group(1))

    json_url_patterns = [
        r'"display_url":"(https:[^"]+)"',
        r'"thumbnail_src":"(https:[^"]+)"',
    ]

    for pattern in json_url_patterns:
        match = re.search(pattern, page, flags=re.IGNORECASE)
        if match:
            raw_url = match.group(1)
            return (
                raw_url.replace("\\u0026", "&")
                .replace("\\/", "/")
                .replace("\\u002F", "/")
            )

    raise ValueError(
        f"No se pudo extraer og:image desde el post {post_url}. "
        "Prueba agregando image_url manualmente en feed.json."
    )


def fetch_profile_latest_items(username: str, max_items: int) -> list[dict]:
    if not username:
        raise ValueError("Debes indicar 'username' en feed.json o usar --username.")

    api_url = (
        "https://www.instagram.com/api/v1/users/web_profile_info/"
        f"?username={urllib.parse.quote(username)}"
    )
    data = fetch_json(api_url, extra_headers={"X-IG-App-ID": INSTAGRAM_APP_ID})

    user = data.get("data", {}).get("user")
    if not isinstance(user, dict):
        raise ValueError(
            "Instagram no devolvio datos del perfil. Verifica si el username es publico y correcto."
        )

    timeline = user.get("edge_owner_to_timeline_media", {})
    edges = timeline.get("edges", []) if isinstance(timeline, dict) else []
    if not isinstance(edges, list) or not edges:
        raise ValueError(
            "Instagram no devolvio publicaciones recientes para ese perfil."
        )

    items = []
    for edge in edges:
        node = edge.get("node", {}) if isinstance(edge, dict) else {}
        shortcode = str(node.get("shortcode") or "").strip()
        if not shortcode:
            continue

        caption_edges = (
            node.get("edge_media_to_caption", {}).get("edges", [])
            if isinstance(node.get("edge_media_to_caption"), dict)
            else []
        )
        caption_text = ""
        if caption_edges:
            caption_node = caption_edges[0].get("node", {})
            if isinstance(caption_node, dict):
                caption_text = str(caption_node.get("text") or "").strip()

        title = _title_from_caption(caption_text, f"Trabajo destacado {len(items) + 1}")
        items.append(
            {
                "index": len(items) + 1,
                "post_url": f"https://www.instagram.com/p/{shortcode}/",
                "image_url": post_media_url(
                    f"https://www.instagram.com/p/{shortcode}/"
                ),
                "title": title,
                "alt": title,
                "url": f"https://www.instagram.com/p/{shortcode}/",
            }
        )

        if len(items) >= max_items:
            break

    if not items:
        raise ValueError(
            "No se pudieron construir publicaciones desde el perfil indicado."
        )

    return items


def detect_extension(url: str, content_type: str | None = None) -> str:
    if content_type:
        ctype = content_type.split(";")[0].strip().lower()
        content_map = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/gif": ".gif",
            "image/avif": ".avif",
        }
        if ctype in content_map:
            return content_map[ctype]

    parsed = urllib.parse.urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return suffix

    return ".jpg"


def download_image(url: str, target_stem: str) -> Path:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            content_type = response.headers.get("Content-Type")
            extension = detect_extension(url, content_type)
            target_file = PUBLIC_DIR / f"{target_stem}{extension}"
            content = response.read()
            target_file.write_bytes(content)
            return target_file
    except urllib.error.URLError as error:
        raise ValueError(
            f"No se pudo descargar la imagen desde {url}: {error}"
        ) from error


def _title_from_caption(text: str, fallback: str) -> str:
    text = (text or "").strip()
    if not text:
        return fallback
    first_line = text.splitlines()[0].strip()
    return (first_line[:90] + "...") if len(first_line) > 90 else first_line


def discover_source_images() -> list[Path]:
    if not SOURCE_DIR.exists():
        return []

    return sorted(
        [
            file_path
            for file_path in SOURCE_DIR.iterdir()
            if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS
        ],
        key=lambda file_path: file_path.name.lower(),
    )


def load_manifest() -> dict:
    if not SOURCE_MANIFEST.exists():
        return {
            "mode": "local_files",
            "max_items": MAX_ITEMS,
            "username": "",
            "items": [],
        }

    with SOURCE_MANIFEST.open("r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)

    if isinstance(data, dict):
        mode = str(data.get("mode", "local_files")).strip() or "local_files"
        try:
            max_items = int(data.get("max_items", MAX_ITEMS))
        except (TypeError, ValueError):
            raise ValueError("'max_items' debe ser un numero entero.")
        max_items = max(1, min(max_items, MAX_ITEMS))

        items = data.get("items", [])
        return {
            "mode": mode,
            "max_items": max_items,
            "username": str(data.get("username") or "").strip(),
            "items": items,
        }
    elif isinstance(data, list):
        return {
            "mode": "local_files",
            "max_items": MAX_ITEMS,
            "username": "",
            "items": data,
        }
    else:
        raise ValueError(
            "feed.json debe ser una lista o un objeto con la clave 'items'."
        )


def normalize_items(raw_items: list[dict], max_items: int) -> list[dict]:
    normalized = []

    for index, item in enumerate(raw_items[:max_items], start=1):
        if not isinstance(item, dict):
            raise ValueError(f"El item #{index} debe ser un objeto JSON.")

        image_name = item.get("image")
        if not image_name:
            raise ValueError(f"El item #{index} no tiene 'image'.")

        source_image = (SOURCE_DIR / str(image_name)).resolve()
        try:
            source_image.relative_to(SOURCE_DIR.resolve())
        except ValueError as error:
            raise ValueError(
                f"La imagen del item #{index} apunta fuera de content/instagram-source."
            ) from error

        if not source_image.exists() or not source_image.is_file():
            raise ValueError(
                f"No existe la imagen indicada en el item #{index}: {image_name}"
            )

        if source_image.suffix.lower() not in IMAGE_EXTENSIONS:
            raise ValueError(
                f"La imagen del item #{index} tiene una extensión no soportada: {source_image.suffix}"
            )

        title = str(item.get("title") or f"Trabajo destacado {index}").strip()
        alt = str(item.get("alt") or title).strip()
        url = str(
            item.get("instagram_url")
            or item.get("url")
            or "{{ SOCIAL_LINKS.get('instagram') }}"
        ).strip()
        normalized.append(
            {
                "index": index,
                "source_image": source_image,
                "title": title,
                "alt": alt,
                "url": url,
            }
        )

    return normalized


def normalize_url_items(raw_items: list[dict], max_items: int) -> list[dict]:
    normalized = []

    for index, item in enumerate(raw_items[:max_items], start=1):
        if not isinstance(item, dict):
            raise ValueError(f"El item #{index} debe ser un objeto JSON.")

        post_url = str(
            item.get("post_url") or item.get("instagram_url") or item.get("url") or ""
        ).strip()
        image_url = str(item.get("image_url") or "").strip()

        if not image_url and post_url:
            image_url = post_media_url(post_url)

        if not image_url:
            raise ValueError(f"El item #{index} debe tener 'image_url' o 'post_url'.")

        if not image_url.startswith(("http://", "https://")):
            raise ValueError(f"El item #{index} tiene image_url invalida: {image_url}")

        title = str(item.get("title") or f"Trabajo destacado {index}").strip()
        alt = str(item.get("alt") or title).strip()
        url = str(
            item.get("instagram_url")
            or item.get("post_url")
            or item.get("url")
            or "{{ SOCIAL_LINKS.get('instagram') }}"
        ).strip()

        normalized.append(
            {
                "index": index,
                "image_url": image_url,
                "post_url": post_url,
                "title": title,
                "alt": alt,
                "url": url,
            }
        )

    return normalized


def prepare_public_dir() -> None:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    PARTIAL_PATH.parent.mkdir(parents=True, exist_ok=True)

    for file_path in PUBLIC_DIR.glob("instagram-*"):
        if file_path.is_file():
            file_path.unlink()


def copy_images(items: list[dict]) -> list[dict]:
    public_items = []

    for item in items:
        ext = item["source_image"].suffix.lower()
        public_name = f"instagram-{item['index']:02d}{ext}"
        public_image = PUBLIC_DIR / public_name
        shutil.copy2(item["source_image"], public_image)

        public_items.append(
            {
                "title": item["title"],
                "alt": item["alt"],
                "url": item["url"],
                "image": f"images/instagram/{public_name}",
            }
        )

    return public_items


def download_url_images(items: list[dict]) -> list[dict]:
    public_items = []

    for item in items:
        target_stem = f"instagram-{item['index']:02d}"
        try:
            downloaded_path = download_image(item["image_url"], target_stem)
        except ValueError:
            if not item.get("post_url"):
                raise
            fallback_url = resolve_image_url_from_post(item["post_url"])
            downloaded_path = download_image(fallback_url, target_stem)

        public_items.append(
            {
                "title": item["title"],
                "alt": item["alt"],
                "url": item["url"],
                "image": f"images/instagram/{downloaded_path.name}",
            }
        )

    return public_items


def write_public_manifest(items: list[dict]) -> None:
    payload = {"items": items}
    PUBLIC_MANIFEST.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def render_feed_partial(items: list[dict]) -> str:
    lines = ["{# Archivo generado por scripts/sync_instagram_feed.py #}"]

    if not items:
        lines.extend(
            [
                "{% for product in img_products[:6] %}",
                '<a href="{{ SITEURL }}/{{ product.url }}" class="social-mosaic-item">',
                '  <img src="{{ SITEURL }}/{{ product.image }}" alt="{{ product.title }}" loading="lazy" />',
                "</a>",
                "{% endfor %}",
            ]
        )
        return "\n".join(lines) + "\n"

    for item in items:
        title = html.escape(item["title"], quote=True)
        alt = html.escape(item["alt"], quote=True)
        url = item["url"].replace('"', "&quot;")
        image = item["image"].replace('"', "&quot;")
        lines.extend(
            [
                f"<!-- {title} -->",
                f'<a href="{url}" class="social-mosaic-item" target="_blank" rel="noopener">',
                f'  <img src="{{{{ SITEURL }}}}/{image}" alt="{alt}" loading="lazy" />',
                "</a>",
            ]
        )

    return "\n".join(lines) + "\n"


def write_partial(items: list[dict]) -> None:
    PARTIAL_PATH.write_text(render_feed_partial(items), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sincroniza publicaciones para la seccion Nuestros trabajos"
    )
    parser.add_argument(
        "--mode",
        choices=["local_files", "manual_urls", "profile_latest"],
        help="Modo de origen de publicaciones",
    )
    parser.add_argument(
        "--max-items", type=int, help="Cantidad maxima de publicaciones a procesar"
    )
    parser.add_argument(
        "--username",
        help="Username publico de Instagram para obtener publicaciones recientes",
    )
    args = parser.parse_args()

    try:
        config = load_manifest()
        mode = args.mode or config.get("mode", "local_files")
        max_items = args.max_items or int(config.get("max_items", MAX_ITEMS))
        username = (args.username or config.get("username") or "").strip()
        max_items = max(1, min(max_items, MAX_ITEMS))

        raw_items = config.get("items", [])
        if not isinstance(raw_items, list):
            raise ValueError("La clave 'items' debe contener una lista.")

        if mode == "profile_latest":
            items = fetch_profile_latest_items(username, max_items)
        elif mode == "manual_urls":
            items = normalize_url_items(raw_items, max_items)
        else:
            items = normalize_items(raw_items, max_items)

        prepare_public_dir()
        if mode == "manual_urls":
            public_items = download_url_images(items)
        else:
            public_items = copy_images(items)

        write_public_manifest(public_items)
        write_partial(public_items)
    except Exception as error:
        print(f"[instagram-feed] Error: {error}", file=sys.stderr)
        return 1

    if not raw_items and mode == "local_files":
        source_images = discover_source_images()
        print(
            "[instagram-feed] No hay publicaciones configuradas en content/instagram-source/feed.json"
        )
        print(
            f"[instagram-feed] Imagenes detectadas en content/instagram-source: {len(source_images)}"
        )
        print(
            "[instagram-feed] El home seguira mostrando el fallback de productos hasta que agregues items al feed."
        )
        return 0

    print(f"[instagram-feed] Modo: {mode}")
    print(f"[instagram-feed] Publicaciones preparadas: {len(public_items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
