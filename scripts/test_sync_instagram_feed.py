"""Prueba sin red de sync_instagram_feed.py: uv run python scripts/test_sync_instagram_feed.py"""
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_instagram_feed as ig
REAL_FETCH = ig.fetch

tmp = Path(tempfile.mkdtemp())
ig.SOURCE_MANIFEST = tmp / "feed.json"
ig.PUBLIC_DIR = tmp / "pub"; ig.OPT_DIR = tmp / "opt"; ig.PARTIAL_PATH = tmp / "p.html"
ig.PUBLIC_DIR.mkdir(); ig.OPT_DIR.mkdir()
(ig.PUBLIC_DIR / "instagram-01.jpg").write_bytes(b"old")
(ig.OPT_DIR / "instagram-01.thumb.webp").write_bytes(b"old")
ig.SOURCE_MANIFEST.write_text(json.dumps({"items": [
    {"post_url": "https://www.instagram.com/p/A/", "title": 'Luffy "grande"'},
    {"post_url": "https://www.instagram.com/p/B/"}]}))

# 1) falla la 2da descarga -> nada se toca
ig.fetch = lambda url: (_ for _ in ()).throw(ValueError("429")) if "/B/" in url else (b"new", "image/jpeg")
assert ig.main() == 1
assert (ig.PUBLIC_DIR / "instagram-01.jpg").read_bytes() == b"old"
assert (ig.OPT_DIR / "instagram-01.thumb.webp").exists()

# 2) todo ok -> fotos nuevas, WebP viejo borrado, partial escapado
ig.fetch = lambda url: (b"new", "image/webp")
assert ig.main() == 0
assert (ig.PUBLIC_DIR / "instagram-01.webp").read_bytes() == b"new"
assert not (ig.PUBLIC_DIR / "instagram-01.jpg").exists()
assert not any(ig.OPT_DIR.iterdir())
html = ig.PARTIAL_PATH.read_text()
assert 'alt="Luffy &quot;grande&quot;"' in html and "resolve_thumb('images/instagram/instagram-02.webp')" in html

# 3) respuesta HTML (login de Instagram) se rechaza
ig.fetch = lambda url: (b"<html>", "text/html; charset=utf-8")
try: ig.download_image("https://x/y.jpg"); raise SystemExit("debió fallar")
except ValueError: pass
print("ok")

# 4) modo API: renueva token en .env, Reels usan thumbnail_url, caption -> alt
import os, io, urllib.error
os.environ.pop("INSTAGRAM_TOKEN", None)
ig.ENV_FILE = tmp / ".env"
ig.ENV_FILE.write_text("OTRA=1\nINSTAGRAM_TOKEN=viejo\n")
media = {"data": [
    {"media_type": "IMAGE", "media_url": "https://cdn/1.jpg", "permalink": "https://ig/p/1/", "caption": "\nLuffy gigante 🏴‍☠️\n#onepiece"},
    {"media_type": "VIDEO", "media_url": "https://cdn/2.mp4", "thumbnail_url": "https://cdn/2.jpg", "permalink": "https://ig/reel/2/"},
]}
calls = []
def fake(url):
    calls.append(url)
    if "refresh_access_token" in url: return json.dumps({"access_token": "nuevo", "expires_in": 5184000}).encode(), "application/json"
    if "/me/media" in url: return json.dumps(media).encode(), "application/json"
    assert not url.endswith(".mp4"), "no debe bajar el video"
    return b"img", "image/jpeg"
ig.fetch = fake
assert ig.main() == 0
assert ig.ENV_FILE.read_text() == "OTRA=1\nINSTAGRAM_TOKEN=nuevo\n"
assert "access_token=nuevo" in calls[1]
html = ig.PARTIAL_PATH.read_text()
assert 'alt="Luffy gigante 🏴‍☠️"' in html and 'href="https://ig/reel/2/"' in html and 'alt="Trabajo destacado 2"' in html

# 5) token vencido: el mensaje de la API llega sin filtrar el token
def expired(url):
    raise urllib.error.HTTPError(url, 400, "Bad", {}, io.BytesIO(b'{"error":{"message":"Session has expired"}}'))
ig.urllib.request.urlopen = lambda *a, **k: expired(a[0].full_url)
ig.fetch = REAL_FETCH
try:
    ig.fetch("https://graph.instagram.com/me/media?access_token=SECRETO")
    raise SystemExit("debió fallar")
except ValueError as e:
    assert "Session has expired" in str(e) and "SECRETO" not in str(e), e
print("ok api")
