import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ENTITY_RE = re.compile(r"\b([a-z_]+\.[a-z0-9_]+)\b")


@dataclass(frozen=True)
class Ref:
    path: str
    line: int
    text: str


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})


def iter_text_files(root: Path, include_globs: list[str], exclude_globs: list[str]):
    included: set[Path] = set()
    for g in include_globs:
        for p in root.rglob(g):
            if p.is_file():
                included.add(p)

    excluded: set[Path] = set()
    for g in exclude_globs:
        for p in root.rglob(g):
            if p.is_file():
                excluded.add(p)

    for p in sorted(included - excluded):
        yield p


def scan_repo_entity_references(
    repo_root: Path,
    include_globs: list[str],
    exclude_globs: list[str],
    max_refs_per_entity: int,
):
    counts: Counter[str] = Counter()
    refs: dict[str, list[Ref]] = defaultdict(list)

    for path in iter_text_files(repo_root, include_globs, exclude_globs):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        for i, line in enumerate(text.splitlines(), start=1):
            for m in ENTITY_RE.finditer(line):
                entity_id = m.group(1)
                counts[entity_id] += 1
                if len(refs[entity_id]) < max_refs_per_entity:
                    refs[entity_id].append(Ref(path=rel, line=i, text=line.strip()))

    return counts, refs


def flatten_sanitized_inventory(inv: dict[str, Any]):
    entities = inv.get("entities", [])
    devices = inv.get("devices", [])
    areas = inv.get("areas", [])

    # entities.csv (from exporter) is non-sanitized; sanitized.json may contain hashed fields.
    # We primarily rely on entity_id to be preserved.
    return entities, devices, areas


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit HA inventory (exported from .storage registries) against this repo to find "
            "which entities are referenced (in use) and which appear unreferenced (cleanup candidates)."
        )
    )
    parser.add_argument(
        "--inventory-json",
        type=Path,
        default=Path("exports/ha_inventory/ha_inventory.sanitized.json"),
        help="Path to sanitized inventory JSON (default: exports/ha_inventory/ha_inventory.sanitized.json)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repo root to scan for entity references (default: current directory)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("exports/ha_inventory"),
        help="Output directory (default: exports/ha_inventory)",
    )
    parser.add_argument(
        "--max-refs-per-entity",
        type=int,
        default=5,
        help="Max example references stored per entity (default: 5)",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=["**/*.yaml", "**/*.yml", "**/*.md", "**/*.txt"],
        help="Glob(s) to include when scanning repo (repeatable)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=["**/exports/**", "**/.git/**", "**/.storage/**"],
        help="Glob(s) to exclude when scanning repo (repeatable)",
    )
    args = parser.parse_args()

    inv_path = args.inventory_json
    if not inv_path.exists():
        print(f"ERROR: inventory json not found: {inv_path}")
        return 2

    inv = read_json(inv_path)
    entities, devices, areas = flatten_sanitized_inventory(inv)

    counts, refs = scan_repo_entity_references(
        repo_root=args.repo_root.resolve(),
        include_globs=args.include,
        exclude_globs=args.exclude,
        max_refs_per_entity=args.max_refs_per_entity,
    )

    # Build entity report
    entity_rows: list[dict[str, Any]] = []
    device_used_by_entity: dict[str, int] = Counter()

    for e in entities:
        entity_id = e.get("entity_id")
        if not isinstance(entity_id, str) or "." not in entity_id:
            continue

        domain = entity_id.split(".", 1)[0]
        ref_count = counts.get(entity_id, 0)
        used_in_repo = ref_count > 0
        device_id = e.get("device_id")

        if device_id and used_in_repo:
            device_used_by_entity[str(device_id)] += 1

        examples = [
            {"path": r.path, "line": r.line, "text": r.text}
            for r in refs.get(entity_id, [])
        ]

        entity_rows.append(
            {
                "entity_id": entity_id,
                "domain": domain,
                "unique_id": e.get("unique_id"),
                "platform": e.get("platform"),
                "original_name": e.get("original_name"),
                "device_id": device_id,
                "area_id": e.get("area_id"),
                "disabled_by": e.get("disabled_by"),
                "hidden_by": e.get("hidden_by"),
                "repo_ref_count": ref_count,
                "used_in_repo": used_in_repo,
                "example_refs": examples,
            }
        )

    # Build device report (best-effort)
    device_rows: list[dict[str, Any]] = []
    for d in devices:
        did = d.get("id")
        did_str = str(did) if did is not None else None
        used_by_entities = int(device_used_by_entity.get(did_str, 0)) if did_str else 0
        device_rows.append(
            {
                "device_id": did_str,
                "name": d.get("name"),
                "name_by_user": d.get("name_by_user"),
                "manufacturer": d.get("manufacturer"),
                "model": d.get("model"),
                "area_id": d.get("area_id"),
                "used_by_repo_entities": used_by_entities,
                "cleanup_candidate": used_by_entities == 0,
            }
        )

    # Summary counts
    domain_counts = Counter(r["domain"] for r in entity_rows)
    unused_counts = Counter(r["domain"] for r in entity_rows if not r["used_in_repo"])

    report = {
        "summary": {
            "entities_total": len(entity_rows),
            "entities_used_in_repo": sum(1 for r in entity_rows if r["used_in_repo"]),
            "entities_unused_in_repo": sum(1 for r in entity_rows if not r["used_in_repo"]),
            "devices_total": len(device_rows),
            "devices_cleanup_candidates": sum(1 for r in device_rows if r["cleanup_candidate"]),
            "by_domain_total": dict(domain_counts),
            "by_domain_unused": dict(unused_counts),
            "note": (
                "Unused-in-repo is a heuristic: it only means this repo scan didn’t find references. "
                "An entity can still be used by integrations, UI created in the HA frontend, scripts in the UI, etc."
            ),
        },
        "entities": sorted(entity_rows, key=lambda r: r["entity_id"]),
        "devices": sorted(device_rows, key=lambda r: (r["cleanup_candidate"], r.get("name") or "", r.get("device_id") or "")),
        "areas": areas,
    }

    out_json = args.out_dir / "ha_inventory.usage_report.json"
    write_json(out_json, report)

    # A compact CSV for sorting/filtering
    out_csv = args.out_dir / "entities_usage.csv"
    write_csv(
        out_csv,
        report["entities"],
        fieldnames=[
            "entity_id",
            "domain",
            "unique_id",
            "platform",
            "original_name",
            "device_id",
            "area_id",
            "disabled_by",
            "hidden_by",
            "repo_ref_count",
            "used_in_repo",
        ],
    )

    out_dev_csv = args.out_dir / "devices_usage.csv"
    write_csv(
        out_dev_csv,
        report["devices"],
        fieldnames=[
            "device_id",
            "name",
            "name_by_user",
            "manufacturer",
            "model",
            "area_id",
            "used_by_repo_entities",
            "cleanup_candidate",
        ],
    )

    print(f"Wrote: {out_json}")
    print(f"Wrote: {out_csv}")
    print(f"Wrote: {out_dev_csv}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
