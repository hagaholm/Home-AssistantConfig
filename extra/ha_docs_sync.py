import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "SYSTEM_OVERVIEW.md"
PACKAGES_DIR = ROOT / "packages"

START = "<!-- AUTO:PACKAGE_INVENTORY_START -->"
END = "<!-- AUTO:PACKAGE_INVENTORY_END -->"


def iter_yaml_files(path: Path):
    for p in sorted(path.glob("*.yaml")):
        if p.name.startswith("."):
            continue
        yield p


def classify_files(files):
    active = []
    disabled = []
    for p in files:
        name = p.name
        if name.endswith("_not_used.yaml") or "_not_used" in name or name.endswith(".temp_not_used") or ".temp_not_used" in name:
            disabled.append(p)
        else:
            active.append(p)
    return active, disabled


def generate_inventory_md() -> str:
    if not PACKAGES_DIR.exists():
        return "(packages/ folder not found)\n"

    top_level_yaml = list(iter_yaml_files(PACKAGES_DIR))
    folders = [p for p in sorted(PACKAGES_DIR.iterdir()) if p.is_dir() and not p.name.startswith(".")]

    lines = []
    lines.append(START)
    lines.append("")
    lines.append("This section is auto-generated from the filesystem.")
    lines.append("Run `py extra/ha_docs_sync.py` to refresh it.")
    lines.append("")

    if top_level_yaml:
        active, disabled = classify_files(top_level_yaml)
        lines.append("### Top-level package files")
        for p in active:
            rel = p.relative_to(ROOT).as_posix()
            lines.append(f"- [{rel}]({rel})")
        if disabled:
            lines.append("")
            lines.append("### Top-level package files (disabled / historical)")
            for p in disabled:
                rel = p.relative_to(ROOT).as_posix()
                lines.append(f"- [{rel}]({rel})")
        lines.append("")

    if folders:
        lines.append("### Package folders")
        for d in folders:
            # rglob: some folders (lights/, scripts/) nest files one level deeper (helpers/, lights/)
            yaml_files = sorted(p for p in d.rglob("*.yaml") if not p.name.startswith("."))
            if not yaml_files:
                continue
            active, disabled = classify_files(yaml_files)
            d_rel = d.relative_to(ROOT).as_posix() + "/"
            lines.append(f"- **{d_rel}**")
            # Keep lists compact: show active first, then disabled.
            for p in active:
                rel = p.relative_to(ROOT).as_posix()
                lines.append(f"  - [{rel}]({rel})")
            if disabled:
                lines.append(f"  - _(disabled / historical)_")
                for p in disabled:
                    rel = p.relative_to(ROOT).as_posix()
                    lines.append(f"    - [{rel}]({rel})")
        lines.append("")

    lines.append(END)
    lines.append("")
    return "\n".join(lines)


def replace_block(text: str, new_block: str) -> str:
    if START not in text or END not in text:
        raise RuntimeError(
            f"Missing markers in {TARGET.name}. Add both {START} and {END} to enable auto-sync."
        )

    before = text.split(START, 1)[0]
    after = text.split(END, 1)[1]

    # Preserve surrounding whitespace nicely.
    before = before.rstrip() + "\n\n"
    after = after.lstrip("\n")

    return before + new_block.strip() + "\n\n" + after


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync/validate GitHub docs for this HA repo.")
    parser.add_argument("--check", action="store_true", help="Do not write files; exit 1 if changes would occur.")
    args = parser.parse_args()

    current = TARGET.read_text(encoding="utf-8")
    new_block = generate_inventory_md()
    updated = replace_block(current, new_block)

    if updated == current:
        print("SYSTEM_OVERVIEW.md is up-to-date.")
        return 0

    if args.check:
        print("SYSTEM_OVERVIEW.md is NOT up-to-date.\nRun: py extra/ha_docs_sync.py")
        return 1

    TARGET.write_text(updated, encoding="utf-8")
    print("Updated SYSTEM_OVERVIEW.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
