#!/usr/bin/env python3
"""Audita los archivos de producto y reporta campos faltantes o inválidos."""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML no instalado. Ejecuta: uv sync") from exc

try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
except ImportError as exc:
    raise SystemExit("Rich no instalado. Ejecuta: uv sync") from exc

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".svg", ".avif", ".gif"}
VALID_PRICE_RE = re.compile(r"^\$\d+(\.\d+)?$")

console = Console()


# ---------------------------------------------------------------------------
# Aliases (igual que el plugin auto_gallery)
# ---------------------------------------------------------------------------
ALIASES: dict[str, tuple[str, ...]] = {
    "title":       ("titulo",),
    "date":        ("fecha",),
    "slug":        ("slug",),
    "category":    ("categoria",),
    "tags":        ("etiquetas",),
    "summary":     ("resumen",),
    "image":       ("imagen",),
    "gallerydir":  ("galeria", "directorio_galeria", "gallery_dir"),
    "price":       ("precio",),
    "product":     ("producto",),
    "variation":   ("variacion",),
    "id_dolibarr": ("id_dolibarr",),
}


def _aliases_for(canonical: str) -> list[str]:
    return [canonical] + list(ALIASES.get(canonical, ()))


def _get(meta: dict, canonical: str):
    for key in _aliases_for(canonical):
        if key in meta:
            return meta[key]
    return None


# ---------------------------------------------------------------------------
# Parseo de front matter
# ---------------------------------------------------------------------------

def _parse_yaml_block(text: str) -> dict:
    try:
        data = yaml.safe_load(text) or {}
        return {str(k): v for k, v in data.items()}
    except yaml.YAMLError:
        return {}


def _parse_pelican_flat(text: str) -> dict:
    """Parsea metadatos planos estilo Pelican (clave: valor, hasta línea vacía)."""
    meta: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            break
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip().lower()] = value.strip()
    return meta


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return _parse_yaml_block(text[3:end])
    return _parse_pelican_flat(text)


# ---------------------------------------------------------------------------
# Resolución de rutas de imagen (igual que plugin)
# ---------------------------------------------------------------------------

def _resolve_media_path(raw: str, content_root: Path) -> Path:
    raw = raw.replace("\\", "/").strip().lstrip("/")
    if "images/productos/" not in raw and not raw.startswith("images/"):
        raw = f"images/productos/{raw}"
    return content_root / raw


def _has_images(directory: Path) -> bool:
    if not directory.is_dir():
        return False
    return any(f.suffix.lower() in IMAGE_EXTENSIONS for f in directory.iterdir() if f.is_file())


# ---------------------------------------------------------------------------
# Checks por producto
# ---------------------------------------------------------------------------

@dataclass
class Issue:
    level: str  # "error" | "warning" | "info"
    message: str


@dataclass
class ProductResult:
    path: Path
    issues: list[Issue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.level == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.level == "warning" for i in self.issues)

    @property
    def ok(self) -> bool:
        return not self.issues


def _check_price(value, label: str) -> list[Issue]:
    issues = []
    if not value:
        issues.append(Issue("error", f"Precio faltante en {label}"))
    else:
        s = str(value).strip()
        if s in ("???", "", "0", "$0", "$0.00"):
            issues.append(Issue("warning", f"Precio sin definir ({s!r}) en {label}"))
        elif not VALID_PRICE_RE.match(s) and not s.startswith("+") and not s.startswith("-"):
            issues.append(Issue("warning", f"Precio con formato inusual ({s!r}) en {label}"))
    return issues


def _check_image_path(raw: str, content_root: Path, label: str) -> list[Issue]:
    """Verifica que una ruta imagen apunte a un archivo real."""
    issues = []
    resolved = _resolve_media_path(raw, content_root)
    if resolved.suffix.lower() in IMAGE_EXTENSIONS:
        if not resolved.exists():
            issues.append(Issue("error", f"Imagen no existe: {raw!r} ({label})"))
    else:
        # Es ruta de directorio — buscar como galería
        if not _has_images(resolved):
            issues.append(Issue("error", f"Directorio de imagen vacío o inexistente: {raw!r} ({label})"))
    return issues


def _check_gallery(raw: str, content_root: Path, label: str) -> list[Issue]:
    resolved = _resolve_media_path(raw, content_root)
    if not _has_images(resolved):
        return [Issue("error", f"Galería vacía o inexistente: {raw!r} ({label})")]
    return []


def audit_product(path: Path, content_root: Path) -> ProductResult:
    result = ProductResult(path=path)
    add = result.issues.append

    # Nombre de archivo con caracteres problemáticos
    if " " in path.name:
        add(Issue("warning", f"Nombre de archivo con espacios: {path.name!r}"))
    if any(ord(c) > 127 for c in path.stem):
        add(Issue("warning", f"Nombre de archivo con caracteres no-ASCII: {path.name!r}"))

    meta = parse_frontmatter(path)
    if not meta:
        add(Issue("error", "No se pudo leer el front matter"))
        return result

    # Campos requeridos
    if not _get(meta, "title"):
        add(Issue("error", "Falta titulo"))
    if not _get(meta, "date"):
        add(Issue("warning", "Falta fecha"))
    if not _get(meta, "slug"):
        add(Issue("warning", "Falta slug"))

    is_product = str(_get(meta, "product") or "").lower() in ("true", "1", "yes", "sí", "si")

    # Precio solo obligatorio para productos activos
    if is_product:
        variation_raw = _get(meta, "variation")
        has_variation = bool(variation_raw)

        if not has_variation:
            result.issues.extend(_check_price(_get(meta, "price"), "producto"))

        # id_dolibarr recomendado
        if not _get(meta, "id_dolibarr"):
            add(Issue("info", "Sin id_dolibarr (recomendado para sincronizar con Dolibarr)"))

    # Resumen recomendado
    if not _get(meta, "summary"):
        add(Issue("info", "Sin resumen (aparece en tarjetas del catálogo)"))

    # Imágenes del producto base
    variation_raw = _get(meta, "variation")
    img = _get(meta, "image")
    gallery = _get(meta, "gallerydir")
    if img:
        result.issues.extend(_check_image_path(str(img), content_root, "imagen principal"))
    if gallery:
        result.issues.extend(_check_gallery(str(gallery), content_root, "galeria principal"))
    if not img and not gallery and not variation_raw:
        add(Issue("warning", "Sin imagen ni galería"))

    # Variaciones
    if variation_raw:
        groups = variation_raw if isinstance(variation_raw, list) else [variation_raw]
        for group in groups:
            if not isinstance(group, dict):
                continue
            group_name = group.get("nombre") or group.get("name") or "grupo"
            items = group.get("lista") or group.get("list") or []
            if not items:
                add(Issue("warning", f"Variación '{group_name}' sin opciones en lista"))
                continue

            # Grupo aditivo: algún ítem tiene precio relativo (+/-); precio
            # vacío en esos ítems significa "+$0" y no es un error.
            is_additive = any(
                str(i.get("precio") or i.get("price") or "").strip().startswith(("+", "-"))
                for i in items if isinstance(i, dict)
            )

            for item in items:
                if not isinstance(item, dict):
                    continue
                item_name = item.get("titulo") or item.get("title") or "?"
                label = f"variación '{group_name}' → '{item_name}'"

                precio = item.get("precio") or item.get("price")
                if not is_additive:
                    result.issues.extend(_check_price(precio, label))

                item_img = item.get("imagen") or item.get("image")
                item_gallery = item.get("galeria") or item.get("gallerydir") or item.get("gallery_dir")

                if item_img:
                    result.issues.extend(_check_image_path(str(item_img), content_root, label))
                if item_gallery:
                    result.issues.extend(_check_gallery(str(item_gallery), content_root, label))
                if not item_img and not item_gallery and not is_additive:
                    add(Issue("info", f"Sin imagen ni galería en {label}"))

    return result


# ---------------------------------------------------------------------------
# Salida en consola
# ---------------------------------------------------------------------------

LEVEL_STYLE = {
    "error":   "[bold red]ERROR  [/]",
    "warning": "[yellow]AVISO  [/]",
    "info":    "[dim]INFO   [/]",
}

LEVEL_ICON = {"error": "✗", "warning": "△", "info": "·"}


def _relative(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def print_report(results: list[ProductResult], base: Path, show_info: bool) -> int:
    errors_total = 0
    warnings_total = 0
    ok_total = 0
    files_with_issues = 0

    for r in results:
        visible = [i for i in r.issues if show_info or i.level != "info"]
        if not visible:
            ok_total += 1
            continue

        files_with_issues += 1
        rel = _relative(r.path, base)
        console.print(f"\n[bold]{rel}[/]")
        for issue in visible:
            icon = LEVEL_ICON[issue.level]
            style = LEVEL_STYLE[issue.level]
            console.print(f"  {style}{icon} {issue.message}")
            if issue.level == "error":
                errors_total += 1
            elif issue.level == "warning":
                warnings_total += 1

    # Resumen final
    console.print()
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column(style="dim")
    table.add_column(justify="right")
    total = len(results)
    table.add_row("Productos revisados", str(total))
    table.add_row("[green]Sin problemas[/]",  f"[green]{ok_total}[/]")
    table.add_row("[yellow]Con avisos[/]",     f"[yellow]{warnings_total}[/]")
    table.add_row("[bold red]Con errores[/]",  f"[bold red]{errors_total}[/]")
    console.print(table)

    return 1 if errors_total else 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Audita productos del catálogo ChepeCarlos3D")
    parser.add_argument(
        "--content-path", default="content",
        help="Directorio raíz de contenido (default: content)"
    )
    parser.add_argument(
        "--products-subdir", default="productos",
        help="Subdirectorio de productos dentro de content (default: productos)"
    )
    parser.add_argument(
        "--info", action="store_true",
        help="Mostrar también avisos informativos (resumen, id_dolibarr)"
    )
    parser.add_argument(
        "--only-errors", action="store_true",
        help="Mostrar solo errores, omitir avisos"
    )
    args = parser.parse_args()

    content_root = Path(args.content_path).resolve()
    products_dir = content_root / args.products_subdir

    if not products_dir.is_dir():
        console.print(f"[red]No se encontró el directorio: {products_dir}[/]")
        return 1

    md_files = sorted(products_dir.rglob("*.md"))
    if not md_files:
        console.print("[yellow]No se encontraron archivos .md[/]")
        return 0

    console.print(f"[bold]Auditando {len(md_files)} producto(s) en {products_dir}[/]\n")

    results = [audit_product(f, content_root) for f in md_files]

    show_info = args.info and not args.only_errors

    if args.only_errors:
        results_filtered = [r for r in results if r.has_errors]
        for r in results:
            r.issues = [i for i in r.issues if i.level == "error"]
    else:
        results_filtered = results

    exit_code = print_report(results_filtered if args.only_errors else results, content_root, show_info)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
