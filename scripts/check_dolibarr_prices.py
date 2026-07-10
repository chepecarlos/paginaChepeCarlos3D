#!/usr/bin/env python3
"""Compara precios locales vs Dolibarr para detectar productos desactualizados."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from audit_products import _get, parse_frontmatter  # noqa: E402

try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
except ImportError as exc:
    raise SystemExit("Rich no instalado. Ejecuta: uv sync") from exc

console = Console()


def _load_env(path: Path) -> dict:
    env = {}
    if not path.is_file():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def _fetch_dolibarr_price(base_url: str, api_key: str, product_id: str) -> str:
    req = urllib.request.Request(
        f"{base_url}/api/index.php/products/{product_id}",
        headers={"DOLAPIKEY": api_key, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        return "no encontrado" if e.code == 404 else f"error {e.code}"
    except (urllib.error.URLError, TimeoutError):
        return "sin conexión"
    price = data.get("price")
    return f"${float(price):.2f}" if price not in (None, "") else "?"


def _fetch_source_prices(source_path: str) -> dict[str, str]:
    """id_dolibarr -> precio_venta según printtool (proyectos fuente con gcode/costo)."""
    try:
        result = subprocess.run(
            ["printtool", "productos", "listar", source_path],
            capture_output=True, text=True, timeout=120, check=True,
        )
        productos = json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as e:
        console.print(f"[yellow]No se pudo consultar printtool ({e}), se omite el precio de fuente[/]\n")
        return {}
    return {
        str(int(p["id_producto_dolibarr"])): f"${float(p['precio_venta']):.2f}"
        for p in productos
        if p.get("id_producto_dolibarr")
    }


def _price_to_float(price: str) -> float | None:
    try:
        return round(float(price.lstrip("$+")), 2)
    except ValueError:
        return None


def _price_of(meta: dict) -> str:
    price = _get(meta, "price")
    if price:
        return str(price)
    variation = _get(meta, "variation")
    if variation:
        group = variation[0] if isinstance(variation, list) else variation
        if isinstance(group, dict):
            items = group.get("lista") or group.get("list") or []
            if items and isinstance(items[0], dict):
                # ponytail: primer item del primer grupo = precio por defecto (ver GUIA_PRODUCTOS.md)
                return str(items[0].get("precio") or items[0].get("price") or "?")
    return "?"


def _entries_for(meta: dict, title: str) -> list[tuple[str, str, str]]:
    """(id_dolibarr, etiqueta, precio) del producto, o uno por variante con id_dolibarr propio."""
    top_id = _get(meta, "id_dolibarr")
    if top_id:
        return [(str(top_id), title, _price_of(meta))]

    entries = []
    variation = _get(meta, "variation")
    groups = variation if isinstance(variation, list) else [variation] if variation else []
    for group in groups:
        if not isinstance(group, dict):
            continue
        items = group.get("lista") or group.get("list") or []
        for item in items:
            if not isinstance(item, dict):
                continue
            item_id = item.get("id_dolibarr")
            if not item_id:
                continue
            item_title = item.get("titulo") or item.get("title") or "?"
            item_price = str(item.get("precio") or item.get("price") or "?")
            entries.append((str(item_id), f"{title} - {item_title}", item_price))
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara precios locales vs Dolibarr vs fuente (printtool)")
    parser.add_argument("--content-path", default="content")
    parser.add_argument("--products-subdir", default="productos")
    parser.add_argument("--no-dolibarr", action="store_true", help="Omite la consulta a Dolibarr")
    parser.add_argument("--no-source", action="store_true", help="Omite la consulta a printtool (proyectos fuente)")
    args = parser.parse_args()

    env = _load_env(Path(__file__).parent.parent / ".env")
    base_url = env.get("DOLIBARR_URL", "").rstrip("/")
    api_key = env.get("DOLIBARR_API_KEY", "")
    query_dolibarr = not args.no_dolibarr and base_url and api_key
    if not args.no_dolibarr and not query_dolibarr:
        console.print("[yellow]DOLIBARR_URL / DOLIBARR_API_KEY no configurados en .env, se omite la consulta[/]\n")

    source_path = env.get("SOURCE_PROJECTS_PATH", "")
    query_source = not args.no_source and source_path
    if not args.no_source and not query_source:
        console.print("[yellow]SOURCE_PROJECTS_PATH no configurado en .env, se omite el precio de fuente[/]\n")
    source_prices = _fetch_source_prices(source_path) if query_source else {}

    products_dir = Path(args.content_path).resolve() / args.products_subdir
    md_files = sorted(products_dir.rglob("*.md"))

    rows = []
    missing = []
    for f in md_files:
        meta = parse_frontmatter(f)
        title = _get(meta, "title") or "?"
        entries = _entries_for(meta, title)
        if not entries:
            missing.append(title)
            continue
        for id_dolibarr, label, local_price in entries:
            dolibarr_price = _fetch_dolibarr_price(base_url, api_key, id_dolibarr) if query_dolibarr else "-"
            source_price = source_prices.get(id_dolibarr, "-")
            rows.append((id_dolibarr, label, local_price, dolibarr_price, source_price))

    rows.sort(key=lambda r: (r[0].isdigit() is False, int(r[0]) if r[0].isdigit() else 0))

    counts = Counter(r[0] for r in rows)
    duplicated = {id_ for id_, n in counts.items() if n > 1}

    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("id_dolibarr", justify="right")
    table.add_column("Nombre")
    table.add_column("Precio local", justify="right")
    table.add_column("Precio Dolibarr", justify="right")
    table.add_column("Precio fuente", justify="right")
    mismatches = 0
    no_source = 0
    shown = 0
    for id_dolibarr, title, local_price, dolibarr_price, source_price in rows:
        if id_dolibarr in duplicated:
            shown += 1
            table.add_row(*(f"[bold red]{v}[/]" for v in (id_dolibarr, title, local_price, dolibarr_price, source_price)))
            continue

        local_float = _price_to_float(local_price)
        dolibarr_not_found = dolibarr_price == "no encontrado"
        dolibarr_differs = dolibarr_price.startswith("$") and _price_to_float(dolibarr_price) != local_float
        source_missing = query_source and source_price == "-"
        source_differs = source_price.startswith("$") and _price_to_float(source_price) != local_float

        if not (dolibarr_not_found or dolibarr_differs or source_missing or source_differs):
            continue  # precio igual en las tres fuentes (o sin datos para comparar): no se muestra

        shown += 1
        if dolibarr_differs or source_differs:
            mismatches += 1
        if source_missing:
            no_source += 1

        dolibarr_cell = f"[bold red]{dolibarr_price}[/]" if dolibarr_not_found else (
            f"[yellow]{dolibarr_price}[/]" if dolibarr_differs else dolibarr_price
        )
        source_cell = "[bold red]sin folder[/]" if source_missing else (
            f"[yellow]{source_price}[/]" if source_differs else source_price
        )
        table.add_row(id_dolibarr, title, local_price, dolibarr_cell, source_cell)

    console.print(table)
    console.print(f"\n[dim]{len(rows)} producto(s) con id_dolibarr, {shown} con problema(s)[/]")
    if missing:
        console.print(f"[yellow]{len(missing)} producto(s) sin id_dolibarr[/]")
    if mismatches:
        console.print(f"[yellow]{mismatches} producto(s) con precio distinto entre sitio, Dolibarr y/o fuente[/]")
    if no_source:
        console.print(f"[yellow]{no_source} producto(s) sin folder configurado en printtool (no se puede verificar el precio de fuente)[/]")

    not_found = [(id_dolibarr, title) for id_dolibarr, title, _, dolibarr_price, _ in rows if dolibarr_price == "no encontrado"]
    if not_found:
        console.print("\n[bold red]No encontrados en Dolibarr:[/]")
        for id_dolibarr, title in not_found:
            console.print(f"  [red]· {id_dolibarr}[/] — {title}")

    if query_source:
        site_ids = {id_dolibarr for id_dolibarr, *_ in rows}
        source_only = {id_ for id_ in source_prices if id_ not in site_ids}
        if source_only:
            console.print(f"\n[yellow]{len(source_only)} producto(s) en printtool sin artículo en el sitio:[/]")
            for id_ in sorted(source_only, key=lambda x: int(x) if x.isdigit() else 0):
                console.print(f"  [yellow]· {id_}[/]")

    if duplicated:
        console.print(f"\n[bold red]ERROR[/] id_dolibarr repetido(s): {', '.join(sorted(duplicated))}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
