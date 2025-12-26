import argparse
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI_PATH = ROOT / "ui-automation.yaml"


def slugify(text: str) -> str:
    text = text.strip().strip('"').strip("'")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text


def extract_ui_automation_entity_ids(ui_text: str) -> set[str]:
    return set(re.findall(r"\bautomation\.[a-z0-9_]+\b", ui_text))


def iter_yaml_defined_automation_entities(root: Path):
    alias_re = re.compile(r"^\s*-\s*alias:\s*(.+?)\s*$")

    # entity_id -> (alias, file)
    def_ids: dict[str, tuple[str, str]] = {}

    for path in root.rglob("*.yaml"):
        # Skip Lovelace dashboards
        if path.name.startswith("ui-"):
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for line in text.splitlines():
            m = alias_re.match(line)
            if not m:
                continue

            alias = m.group(1)
            slug = slugify(alias)
            if not slug:
                continue

            entity_id = f"automation.{slug}"
            rel = str(path.relative_to(root)).replace("\\", "/")

            # Prefer definitions in automations/ if duplicates exist elsewhere
            existing = def_ids.get(entity_id)
            if existing is None:
                def_ids[entity_id] = (alias.strip(), rel)
                continue

            _, old_rel = existing
            if old_rel.startswith("automations/"):
                continue
            if rel.startswith("automations/"):
                def_ids[entity_id] = (alias.strip(), rel)

    for entity_id, (alias, rel) in def_ids.items():
        yield entity_id, alias, rel


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit ui-automation.yaml vs YAML-defined automations")
    parser.add_argument("--by-file", action="store_true", help="Print YAML-defined automations grouped by source file")
    parser.add_argument(
        "--filter-prefix",
        action="append",
        default=[],
        help="Only include definitions whose file path starts with this prefix (repeatable), e.g. automations/ or packages/",
    )
    args = parser.parse_args()

    if not UI_PATH.exists():
        print(f"ERROR: ui file not found: {UI_PATH}", file=sys.stderr)
        return 2

    ui_text = UI_PATH.read_text(encoding="utf-8")
    ui_ids = extract_ui_automation_entity_ids(ui_text)

    defs = list(iter_yaml_defined_automation_entities(ROOT))
    if args.filter_prefix:
        defs = [(eid, alias, rel) for (eid, alias, rel) in defs if any(rel.startswith(p) for p in args.filter_prefix)]

    def_map = {entity_id: (alias, rel) for entity_id, alias, rel in defs}
    defined_ids = set(def_map.keys())

    if args.by_file:
        grouped: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for entity_id, (alias, rel) in def_map.items():
            grouped[rel].append((entity_id, alias))

        for rel in sorted(grouped.keys()):
            items = sorted(grouped[rel], key=lambda x: x[0])
            print(f"\n# {rel} ({len(items)})")
            for entity_id, alias in items:
                print(f"- {entity_id}  # {alias}")
        return 0

    in_ui_missing = sorted(ui_ids - defined_ids)
    not_in_ui = sorted(defined_ids - ui_ids)

    print(f"UI automations: {len(ui_ids)}")
    print(f"Defined automations (from YAML aliases): {len(defined_ids)}")
    print(f"UI entries not found in YAML: {len(in_ui_missing)}")
    print(f"YAML-defined automations missing from UI: {len(not_in_ui)}")

    print("\n--- UI entries not found in YAML ---")
    for x in in_ui_missing:
        print(x)

    print("\n--- YAML-defined automations missing from UI ---")
    for x in not_in_ui:
        alias, rel = def_map[x]
        print(f"{x} | {rel} | {alias}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
