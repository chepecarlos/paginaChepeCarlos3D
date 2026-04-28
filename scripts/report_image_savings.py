#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_FORMATS = (".jpg", ".jpeg", ".png")


@dataclass
class Totals:
    source_files: int = 0
    optimized_files: int = 0
    missing_optimized: int = 0
    source_bytes: int = 0
    optimized_bytes: int = 0


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


def iter_source_images(source_root: Path, formats: Iterable[str]) -> list[Path]:
    format_set = {item.lower() for item in formats}
    if not source_root.exists():
        return []
    return [
        path
        for path in sorted(source_root.rglob("*"))
        if path.is_file() and path.suffix.lower() in format_set
    ]


def source_to_target(source_file: Path, source_images_dir: Path, dest_images_dir: Path) -> Path:
    rel_to_images = source_file.relative_to(source_images_dir)
    return (dest_images_dir / rel_to_images).with_suffix(".webp")


def human_size(byte_count: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(byte_count)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{byte_count} B"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reporta ahorro de peso entre imagenes originales y WebP optimizadas."
    )
    parser.add_argument("--content-path", default="content")
    parser.add_argument("--source-dir", default="images")
    parser.add_argument("--dest-dir", default="images_opt")
    parser.add_argument("--products-subdir", default="productos")
    parser.add_argument("--formats", default=",".join(DEFAULT_FORMATS))
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    content_path = Path(args.content_path).resolve()
    source_images_dir = (content_path / normalize_relpath(args.source_dir)).resolve()
    dest_images_dir = (content_path / normalize_relpath(args.dest_dir)).resolve()
    products_subdir = normalize_relpath(args.products_subdir)

    source_root = (source_images_dir / products_subdir).resolve()
    formats = parse_formats(args.formats)

    source_files = iter_source_images(source_root, formats)
    if not source_files:
        print(f"No se encontraron imagenes fuente en: {source_root}")
        return 0

    totals = Totals(source_files=len(source_files))

    for source_file in source_files:
        target_file = source_to_target(source_file, source_images_dir, dest_images_dir)
        totals.source_bytes += source_file.stat().st_size

        if target_file.exists():
            totals.optimized_files += 1
            totals.optimized_bytes += target_file.stat().st_size
        else:
            totals.missing_optimized += 1

    if totals.optimized_files == 0:
        print("No hay archivos optimizados para comparar. Ejecuta primero make optimize-images")
        return 0

    absolute_saved = totals.source_bytes - totals.optimized_bytes
    percent_saved = 0.0
    if totals.source_bytes > 0:
        percent_saved = (absolute_saved / totals.source_bytes) * 100

    print("Reporte de ahorro de imagenes")
    print(f"- Fuente evaluada: {source_root}")
    print(f"- Imagenes fuente: {totals.source_files}")
    print(f"- Imagenes optimizadas encontradas: {totals.optimized_files}")
    print(f"- Imagenes sin optimizar: {totals.missing_optimized}")
    print(f"- Peso original total: {human_size(totals.source_bytes)} ({totals.source_bytes} bytes)")
    print(
        f"- Peso optimizado total: {human_size(totals.optimized_bytes)} "
        f"({totals.optimized_bytes} bytes)"
    )
    print(f"- Ahorro absoluto: {human_size(absolute_saved)} ({absolute_saved} bytes)")
    print(f"- Ahorro porcentual: {percent_saved:.2f}%")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
