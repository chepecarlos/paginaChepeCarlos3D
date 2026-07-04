#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise SystemExit("Pillow no esta instalado. Ejecuta: pip install pillow") from exc


DEFAULT_FORMATS = (".jpg", ".jpeg", ".png")
STATE_FILE_NAME = ".optimize_state.json"


@dataclass
class Counters:
    processed: int = 0
    skipped: int = 0
    errors: int = 0
    deleted: int = 0


def normalize_relpath(path_value: str | Path) -> str:
    text = str(path_value).replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    return text.lstrip("/")


def parse_formats(value: str | None) -> tuple[str, ...]:
    if not value:
        return DEFAULT_FORMATS
    result = []
    for item in value.split(","):
        ext = item.strip().lower()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = f".{ext}"
        result.append(ext)
    return tuple(result) or DEFAULT_FORMATS


def load_state(state_file: Path) -> Dict[str, dict]:
    if not state_file.exists():
        return {}
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_state(state_file: Path, state: Dict[str, dict]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(
        json.dumps(state, ensure_ascii=True, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def source_signature(source_path: Path) -> dict:
    stat = source_path.stat()
    return {
        "mtime_ns": stat.st_mtime_ns,
        "size": stat.st_size,
    }


def iter_source_images(source_root: Path, formats: Iterable[str]) -> Iterable[Path]:
    formats_set = {ext.lower() for ext in formats}
    if not source_root.exists():
        return []
    files = [
        path
        for path in sorted(source_root.rglob("*"))
        if path.is_file() and path.suffix.lower() in formats_set
    ]
    return files


def source_to_target(
    source_file: Path, source_images_dir: Path, dest_images_dir: Path
) -> Path:
    rel_to_images = source_file.relative_to(source_images_dir)
    return (dest_images_dir / rel_to_images).with_suffix(".webp")


def should_process(
    source_file: Path,
    target_file: Path,
    state: Dict[str, dict],
    quality: int,
    force: bool,
) -> bool:
    if force:
        return True

    source_key = normalize_relpath(source_file)
    signature = source_signature(source_file)
    previous = state.get(source_key)

    if not target_file.exists() or not previous:
        return True

    if previous.get("quality") != quality:
        return True

    return not (
        previous.get("mtime_ns") == signature["mtime_ns"]
        and previous.get("size") == signature["size"]
    )


def cleanup_orphaned_webp(
    dest_images_dir: Path,
    source_images_dir: Path,
    formats: tuple[str, ...],
    state: Dict[str, dict],
) -> int:
    dest_root = dest_images_dir
    if not dest_root.exists():
        return 0

    deleted = 0
    for webp_file in sorted(dest_root.rglob("*.webp")):
        rel = webp_file.relative_to(dest_images_dir)
        source_base = (source_images_dir / rel).with_suffix("")
        source_parent = source_base.parent
        # Comparacion insensible a mayusculas: el filesystem puede tener
        # ".PNG" mientras --formats siempre trae minusculas.
        source_exists = source_parent.exists() and any(
            f.is_file() and f.stem == source_base.name and f.suffix.lower() in formats
            for f in source_parent.iterdir()
        )

        if not source_exists:
            webp_file.unlink()
            deleted += 1
            print(f"[limpieza] Eliminado: {rel}")
            for ext in formats:
                state.pop(normalize_relpath(source_base.with_suffix(ext)), None)

    for dirpath in sorted(dest_root.rglob("*"), reverse=True):
        if dirpath.is_dir() and not any(dirpath.iterdir()):
            dirpath.rmdir()

    return deleted


def optimize_image(source_file: Path, target_file: Path, quality: int) -> None:
    target_file.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source_file) as image:
        image.save(target_file, format="WEBP", quality=quality, method=6)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Optimiza imagenes PNG/JPG/JPEG a WebP en modo incremental."
    )
    parser.add_argument("--content-path", default="content")
    parser.add_argument("--source-dir", default="images")
    parser.add_argument("--dest-dir", default="images_opt")
    parser.add_argument("--formats", default=",".join(DEFAULT_FORMATS))
    parser.add_argument("--quality", type=int, default=72)
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not (0 <= args.quality <= 100):
        parser.error("--quality debe estar entre 0 y 100")

    content_path = Path(args.content_path).resolve()
    source_images_dir = (content_path / normalize_relpath(args.source_dir)).resolve()
    source_root = source_images_dir
    dest_images_dir = (content_path / normalize_relpath(args.dest_dir)).resolve()
    state_file = dest_images_dir / STATE_FILE_NAME
    formats = parse_formats(args.formats)

    state = load_state(state_file)
    counters = Counters()

    source_files = iter_source_images(source_root, formats)
    if not source_files:
        print(f"No se encontraron imagenes para optimizar en: {source_root}")
        print("Resumen: procesadas=0 omitidas=0 errores=0")
        return 0

    total = len(source_files)
    tty = sys.stdout.isatty()
    for i, source_file in enumerate(source_files, 1):
        if tty:
            filled = i * 40 // total
            bar = "█" * filled + "░" * (40 - filled)
            sys.stdout.write(f"\r[{bar}] {i}/{total}  {source_file.name[:40]:<40}")
            sys.stdout.flush()

        target_file = source_to_target(source_file, source_images_dir, dest_images_dir)
        source_key = normalize_relpath(source_file)

        try:
            if not should_process(
                source_file, target_file, state, args.quality, args.force
            ):
                counters.skipped += 1
                continue

            optimize_image(source_file, target_file, args.quality)
            signature = source_signature(source_file)
            state[source_key] = {
                **signature,
                "quality": args.quality,
                "target": normalize_relpath(target_file),
            }
            counters.processed += 1
        except Exception as exc:  # pragma: no cover - runtime errors logged
            counters.errors += 1
            print(f"\n[ERROR] {source_file}: {exc}", file=sys.stderr)

    if tty:
        print()

    counters.deleted = cleanup_orphaned_webp(
        dest_images_dir, source_images_dir, formats, state
    )

    save_state(state_file, state)

    print(
        "Resumen: "
        f"procesadas={counters.processed} "
        f"omitidas={counters.skipped} "
        f"eliminadas={counters.deleted} "
        f"errores={counters.errors}"
    )

    return 1 if counters.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
