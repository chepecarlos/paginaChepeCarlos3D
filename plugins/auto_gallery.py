from pathlib import Path

from pelican import signals


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".svg", ".avif", ".gif"}


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


def _normalize(path_value):
    text = str(path_value).replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    return text.lstrip("/")


def _discover_images(content_root, gallery_dir):
    gallery_path = (content_root / _normalize(gallery_dir)).resolve()
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
            main_image = _normalize(main_image)

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
    signals.article_generator_finalized.connect(enrich_articles_with_auto_gallery)
