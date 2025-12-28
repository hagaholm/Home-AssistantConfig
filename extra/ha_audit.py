import argparse
import os
import re
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SKIP_DIRS = {".git", "__pycache__", ".storage"}

ID_RE = re.compile(r"^\s*id:\s*['\"]([^'\"]+)['\"]\s*$")
SCRIPT_REF_RE = re.compile(r"\bscript\.([a-zA-Z0-9_]+)\b")
INPUT_SELECT_REF_RE = re.compile(r"\binput_select\.([a-zA-Z0-9_]+)\b")
INPUT_BOOLEAN_REF_RE = re.compile(r"\binput_boolean\.([a-zA-Z0-9_]+)\b")

# Filter out common service names that are not entities.
SCRIPT_SERVICE_NAMES = {"turn_on", "turn_off", "toggle", "reload"}
INPUT_SELECT_SERVICE_NAMES = {"select_option", "select_first", "select_last", "select_next", "select_previous"}
INPUT_BOOLEAN_SERVICE_NAMES = {"turn_on", "turn_off", "toggle"}

SECTIONS = [
    "script",
    "input_select",
    "input_boolean",
    "input_number",
    "input_datetime",
]

SECTION_RE = re.compile(r"^({}):\s*$".format("|".join(SECTIONS)))
KEY_RE = re.compile(r"^\s{2}([a-zA-Z0-9_]+):\s*(#.*)?$")


def iter_yaml_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.lower().endswith(".yaml"):
                yield os.path.join(dirpath, fn)


def read_lines(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    except UnicodeDecodeError:
        with open(path, "r", encoding="latin-1") as f:
            return f.readlines()


def style_audit_package_headers(root: str, *, max_list: int = 50):
    """Best-effort audit for whether package YAMLs appear to follow our header/comment standard.

    This is intentionally heuristic (string checks in the first ~120 lines), since we do not
    fully parse YAML here.
    """

    def normalize_rel(path: str) -> str:
        return os.path.relpath(path, root).replace("\\", "/")

    missing_kallor_beskrivning = []
    missing_metadata = []

    for path in iter_yaml_files(os.path.join(root, "packages")):
        lines = read_lines(path)
        head = "".join(lines[:120])

        # Only apply this check to files that look like they define automation/script/template blocks.
        if not any(token in head for token in ("automation:", "script:", "template:")):
            continue

        if ("Källor:" not in head) and ("BESKRIVNING:" not in head):
            missing_kallor_beskrivning.append(normalize_rel(path))

        if ("METADATA:" not in head) and ("# Skapad:" not in head):
            missing_metadata.append(normalize_rel(path))

    print("\nStyle/header audit (packages/*):")
    print(f"- Missing both 'Källor:' and 'BESKRIVNING:' markers: {len(missing_kallor_beskrivning)}")
    for rel in missing_kallor_beskrivning[:max_list]:
        print(f"  - {rel}")
    if len(missing_kallor_beskrivning) > max_list:
        print("  - ...")

    print(f"- Missing 'METADATA:'/'Skapad' marker: {len(missing_metadata)}")
    for rel in missing_metadata[:max_list]:
        print(f"  - {rel}")
    if len(missing_metadata) > max_list:
        print("  - ...")


def collect_section_keys(lines):
    # indentation-based, but works well for typical HA config.
    active = None
    found = defaultdict(list)  # section -> list of (key, line_no)

    for i, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")

        if line.lstrip().startswith("#"):
            continue

        m = SECTION_RE.match(line)
        if m:
            active = m.group(1)
            continue

        # leave section when we hit another top-level mapping key
        if active and (len(line) - len(line.lstrip(" ")) == 0) and line.strip().endswith(":"):
            active = None

        if active:
            km = KEY_RE.match(line)
            if km:
                key = km.group(1)
                found[active].append((key, i))

    return found


def main():
    parser = argparse.ArgumentParser(description="Audit Home Assistant YAML config for duplicates and missing references.")
    parser.add_argument(
        "--style",
        action="store_true",
        help="Also run a best-effort style/header audit on packages/*.yaml.",
    )
    parser.add_argument(
        "--style-max",
        type=int,
        default=50,
        help="Max files to list per style finding group (default: 50).",
    )
    args = parser.parse_args()

    yaml_files = list(iter_yaml_files(ROOT))

    ids = defaultdict(list)  # id -> list[(relpath, line)]
    section_keys = {s: defaultdict(list) for s in SECTIONS}  # section -> key -> list[(relpath,line)]

    refs_script = defaultdict(list)  # script_name -> list[(relpath,line)]
    refs_in_sel = defaultdict(list)
    refs_in_bool = defaultdict(list)

    for path in yaml_files:
        rel = os.path.relpath(path, ROOT)
        lines = read_lines(path)

        for i, raw in enumerate(lines, 1):
            line = raw.rstrip("\n")

            # Ignore comment-only lines for reference scanning to reduce false positives.
            if line.lstrip().startswith("#"):
                continue

            m = ID_RE.match(line)
            if m:
                ids[m.group(1)].append((rel, i))

            for sm in SCRIPT_REF_RE.finditer(line):
                name = sm.group(1)
                if name not in SCRIPT_SERVICE_NAMES:
                    refs_script[name].append((rel, i))

            for im in INPUT_SELECT_REF_RE.finditer(line):
                name = im.group(1)
                if name not in INPUT_SELECT_SERVICE_NAMES:
                    refs_in_sel[name].append((rel, i))

            for bm in INPUT_BOOLEAN_REF_RE.finditer(line):
                name = bm.group(1)
                if name not in INPUT_BOOLEAN_SERVICE_NAMES:
                    refs_in_bool[name].append((rel, i))

        found = collect_section_keys(lines)
        for section, items in found.items():
            for key, line_no in items:
                section_keys[section][key].append((rel, line_no))

    # Report
    print(f"Root: {ROOT}")
    print(f"YAML files scanned: {len(yaml_files)}")

    dup_ids = {k: v for k, v in ids.items() if len(v) > 1}
    print(f"\nIDs found: {len(ids)}  Duplicate IDs: {len(dup_ids)}")
    if dup_ids:
        for k in sorted(dup_ids):
            print(f"\nDuplicate id '{k}' ({len(dup_ids[k])}x):")
            for rel, line in dup_ids[k]:
                print(f"  - {rel}:{line}")

    for section in SECTIONS:
        dup = {k: v for k, v in section_keys[section].items() if len(v) > 1}
        print(f"\n[{section}] keys: {len(section_keys[section])}  duplicates: {len(dup)}")
        if dup:
            for k in sorted(dup):
                print(f"- {k} ({len(dup[k])}x)")
                for rel, line in dup[k]:
                    print(f"  - {rel}:{line}")

    # Missing references (best-effort)
    defined_scripts = set(section_keys["script"].keys())
    missing_scripts = {k: v for k, v in refs_script.items() if k not in defined_scripts}
    print(f"\nScript references: {len(refs_script)}  Missing script targets: {len(missing_scripts)}")
    if missing_scripts:
        for k in sorted(missing_scripts):
            # show up to 8 locations
            locs = missing_scripts[k][:8]
            print(f"- script.{k} referenced but not defined ({len(missing_scripts[k])}x). Examples:")
            for rel, line in locs:
                print(f"  - {rel}:{line}")

    defined_in_sel = set(section_keys["input_select"].keys())
    missing_in_sel = {k: v for k, v in refs_in_sel.items() if k not in defined_in_sel}
    print(f"\ninput_select references: {len(refs_in_sel)}  Missing targets: {len(missing_in_sel)}")
    if missing_in_sel:
        for k in sorted(missing_in_sel):
            locs = missing_in_sel[k][:8]
            print(f"- input_select.{k} referenced but not defined ({len(missing_in_sel[k])}x). Examples:")
            for rel, line in locs:
                print(f"  - {rel}:{line}")

    defined_in_bool = set(section_keys["input_boolean"].keys())
    missing_in_bool = {k: v for k, v in refs_in_bool.items() if k not in defined_in_bool}
    print(f"\ninput_boolean references: {len(refs_in_bool)}  Missing targets: {len(missing_in_bool)}")
    if missing_in_bool:
        for k in sorted(missing_in_bool):
            locs = missing_in_bool[k][:8]
            print(f"- input_boolean.{k} referenced but not defined ({len(missing_in_bool[k])}x). Examples:")
            for rel, line in locs:
                print(f"  - {rel}:{line}")

    if args.style:
        style_audit_package_headers(ROOT, max_list=args.style_max)


if __name__ == "__main__":
    main()
