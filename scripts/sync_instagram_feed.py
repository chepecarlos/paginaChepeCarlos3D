"""Descarga las fotos de los últimos posts y genera el partial del mosaico
"Trabajos recientes" del home.

Con INSTAGRAM_TOKEN (variable de entorno o .env) usa la API oficial de Instagram;
sin token, usa los post_url de content/instagram-source/feed.json."""

from __future__ import annotations

import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
GRAPH_URL = "https://graph.instagram.com"
SOURCE_MANIFEST = BASE_DIR / "content" / "instagram-source" / "feed.json"
PUBLIC_DIR = BASE_DIR / "content" / "images" / "instagram"
OPT_DIR = BASE_DIR / "content" / "images_opt" / "instagram"
PARTIAL_PATH = (
    BASE_DIR / "theme" / "templates" / "partials" / "instagram_feed_items.html"
)
MAX_ITEMS = 6
HTTP_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/avif": ".avif",
}


def fetch(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            return response.read(), response.headers.get("Content-Type") or ""
    except urllib.error.HTTPError as error:
        if error.code == 429:
            raise ValueError(
                "Instagram limito temporalmente el acceso (HTTP 429). Espera unos minutos."
            ) from error
        # La API explica el error en el cuerpo (ej. token vencido); sin la URL, que lleva el token
        detail = error.read().decode("utf-8", errors="replace")[:300]
        host = urllib.parse.urlparse(url).netloc
        raise ValueError(f"{host} respondio HTTP {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise ValueError(f"No se pudo leer la URL {url}: {error}") from error


def post_media_url(post_url: str) -> str:
    parsed = urllib.parse.urlparse(post_url)
    base = urllib.parse.urlunparse(parsed._replace(query="", fragment="")).rstrip("/")
    return f"{base}/media/?size=l"


def resolve_image_url_from_post(post_url: str) -> str:
    page = fetch(post_url)[0].decode("utf-8", errors="replace")

    patterns = [
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
        r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, page, flags=re.IGNORECASE)
        if match:
            return html.unescape(match.group(1))

    for pattern in (r'"display_url":"(https:[^"]+)"', r'"thumbnail_src":"(https:[^"]+)"'):
        match = re.search(pattern, page, flags=re.IGNORECASE)
        if match:
            return (
                match.group(1)
                .replace("\\u0026", "&")
                .replace("\\/", "/")
                .replace("\\u002F", "/")
            )

    raise ValueError(
        f"No se pudo extraer og:image desde el post {post_url}. "
        "Prueba agregando image_url manualmente en feed.json."
    )


def download_image(url: str) -> tuple[bytes, str]:
    content, content_type = fetch(url)
    ctype = content_type.split(";")[0].strip().lower()
    if ctype in CONTENT_TYPES:
        return content, CONTENT_TYPES[ctype]
    if ctype.startswith("text/"):
        # Instagram responde HTML (login/bloqueo) en vez de la imagen
        raise ValueError(f"{url} no devolvio una imagen ({ctype}).")
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    return content, suffix if suffix in CONTENT_TYPES.values() else ".jpg"


def _title_from_caption(caption: str, fallback: str) -> str:
    first_line = next((line.strip() for line in caption.splitlines() if line.strip()), "")
    if not first_line:
        return fallback
    return (first_line[:90] + "...") if len(first_line) > 90 else first_line


def load_token() -> tuple[str, bool]:
    """Devuelve (token, viene_de_.env)."""
    token = os.environ.get("INSTAGRAM_TOKEN", "").strip()
    if token:
        return token, False
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition("=")
            if key.strip() == "INSTAGRAM_TOKEN" and value.strip():
                return value.strip().strip("\"'"), True
    return "", False


def save_token(token: str) -> None:
    lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    lines = [
        f"INSTAGRAM_TOKEN={token}" if line.partition("=")[0].strip() == "INSTAGRAM_TOKEN" else line
        for line in lines
    ]
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def refresh_token(token: str, from_env_file: bool) -> str:
    """El token dura 60 días; cada renovación da 60 más (solo si tiene más de 24 h)."""
    query = urllib.parse.urlencode(
        {"grant_type": "ig_refresh_token", "access_token": token}
    )
    try:
        data = json.loads(fetch(f"{GRAPH_URL}/refresh_access_token?{query}")[0])
    except ValueError as error:
        print(f"[instagram-feed] Aviso: no se renovo el token ({error})", file=sys.stderr)
        return token

    new_token = str(data.get("access_token") or token)
    days = int(data.get("expires_in", 0)) // 86400
    print(f"[instagram-feed] Token renovado, vence en {days} dias.")
    if from_env_file and new_token != token:
        save_token(new_token)
    return new_token


def load_api_items(token: str) -> list[dict]:
    query = urllib.parse.urlencode(
        {
            "fields": "caption,media_type,media_url,thumbnail_url,permalink",
            "limit": MAX_ITEMS,
            "access_token": token,
        }
    )
    data = json.loads(fetch(f"{GRAPH_URL}/me/media?{query}")[0])

    items = []
    for post in data.get("data", []):
        # Reels/videos: media_url es el .mp4, la portada está en thumbnail_url
        image_url = (
            post.get("thumbnail_url")
            if post.get("media_type") == "VIDEO"
            else post.get("media_url")
        )
        if not image_url:
            continue
        index = len(items) + 1
        title = _title_from_caption(post.get("caption") or "", f"Trabajo destacado {index}")
        items.append(
            {
                "index": index,
                "image_url": image_url,
                "post_url": "",
                "title": title,
                "alt": title,
                "url": post.get("permalink") or "{{ SOCIAL_LINKS.get('instagram') }}",
            }
        )
    if not items:
        raise ValueError("La API de Instagram no devolvio publicaciones con imagen.")
    return items


def load_items() -> list[dict]:
    if not SOURCE_MANIFEST.exists():
        return []

    data = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("items", []), list):
        raise ValueError("feed.json debe ser un objeto con la clave 'items' (lista).")

    try:
        max_items = int(data.get("max_items", MAX_ITEMS))
    except (TypeError, ValueError):
        raise ValueError("'max_items' debe ser un numero entero.")
    max_items = max(1, min(max_items, MAX_ITEMS))

    items = []
    for index, item in enumerate(data.get("items", [])[:max_items], start=1):
        if not isinstance(item, dict):
            raise ValueError(f"El item #{index} debe ser un objeto JSON.")

        post_url = str(
            item.get("post_url") or item.get("instagram_url") or item.get("url") or ""
        ).strip()
        image_url = str(item.get("image_url") or "").strip() or (
            post_media_url(post_url) if post_url else ""
        )
        if not image_url:
            raise ValueError(f"El item #{index} debe tener 'image_url' o 'post_url'.")
        if not image_url.startswith(("http://", "https://")):
            raise ValueError(f"El item #{index} tiene image_url invalida: {image_url}")

        title = str(item.get("title") or f"Trabajo destacado {index}").strip()
        items.append(
            {
                "index": index,
                "image_url": image_url,
                "post_url": post_url,
                "title": title,
                "alt": str(item.get("alt") or title).strip(),
                "url": post_url or "{{ SOCIAL_LINKS.get('instagram') }}",
            }
        )

    return items


def download_all(items: list[dict]) -> list[dict]:
    """Descarga todo a memoria; si algo falla, las fotos actuales quedan intactas."""
    for item in items:
        try:
            item["content"], item["ext"] = download_image(item["image_url"])
        except ValueError:
            if not item["post_url"]:
                raise
            item["content"], item["ext"] = download_image(
                resolve_image_url_from_post(item["post_url"])
            )
    return items


def replace_public_images(items: list[dict]) -> list[dict]:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    # Los WebP viejos taparían las fotos nuevas (resolve_thumb los prefiere);
    # sin ellos se sirve el original hasta que optimize_images los regenere.
    for directory in (PUBLIC_DIR, OPT_DIR):
        for file_path in directory.glob("instagram-*"):
            file_path.unlink()

    public_items = []
    for item in items:
        name = f"instagram-{item['index']:02d}{item['ext']}"
        (PUBLIC_DIR / name).write_bytes(item["content"])
        public_items.append({**item, "image": f"images/instagram/{name}"})
    return public_items


def render_feed_partial(items: list[dict]) -> str:
    lines = ["{# Archivo generado por scripts/sync_instagram_feed.py #}"]

    if not items:
        lines.extend(
            [
                "{% for product in img_products[:6] %}",
                '<a href="{{ SITEURL }}/{{ product.url }}" class="social-mosaic-item">',
                '  <img src="{{ SITEURL }}/{{ resolve_thumb(product.image) }}" alt="{{ product.title }}" loading="lazy" />',
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
                # Miniatura WebP de optimize_images.py (fallback al original si no existe)
                f'  <img src="{{{{ SITEURL }}}}/{{{{ resolve_thumb(\'{image}\') }}}}" alt="{alt}" loading="lazy" />',
                "</a>",
            ]
        )

    return "\n".join(lines) + "\n"


def main() -> int:
    try:
        token, from_env_file = load_token()
        if token:
            items = load_api_items(refresh_token(token, from_env_file))
        else:
            items = load_items()
        public_items = replace_public_images(download_all(items)) if items else []
        PARTIAL_PATH.write_text(render_feed_partial(public_items), encoding="utf-8")
    except Exception as error:
        print(f"[instagram-feed] Error: {error}", file=sys.stderr)
        return 1

    if not public_items:
        print(
            "[instagram-feed] feed.json sin items: el home muestra fotos de productos."
        )
    else:
        print(f"[instagram-feed] Publicaciones preparadas: {len(public_items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
