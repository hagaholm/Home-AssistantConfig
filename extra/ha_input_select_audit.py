import os
import re
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKIP_DIRS = {".git", "__pycache__", ".storage"}

TOP_KEY_RE = re.compile(r"^([a-zA-Z0-9_]+):\s*(#.*)?$")
ENTITY_KEY_RE = re.compile(r"^\s{2}([a-zA-Z0-9_]+):\s*(#.*)?$")
OPTIONS_RE = re.compile(r"^(\s+)options:\s*(#.*)?$")
LIST_ITEM_RE = re.compile(r"^\s*-\s*(.*?)\s*(#.*)?$")

INPUT_SELECT_ENTITY_RE = re.compile(r"\binput_select\.([a-zA-Z0-9_]+)\b")

SERVICE_SELECT_OPTION_RE = re.compile(r"^\s*service:\s*input_select\.select_option\s*$")
ENTITY_ID_LINE_RE = re.compile(r"^\s*entity_id:\s*input_select\.([a-zA-Z0-9_]+)\s*$")
OPTION_LINE_RE = re.compile(r"^\s*option:\s*(.+?)\s*$")

STATE_LINE_RE = re.compile(r"^\s*state:\s*(.+?)\s*$")


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


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
        value = value[1:-1]
    return value.strip()


def collect_input_select_options(lines):
    """Best-effort extraction of input_select.<key>.options values from YAML.

    This intentionally does NOT fully parse YAML; it follows the repo's common indentation style.
    """
    in_input_select = False
    current_entity = None
    collecting_options = False
    options_indent = None

    options_by_entity: dict[str, list[str]] = defaultdict(list)

    for raw in lines:
        line = raw.rstrip("\n")

        if line.lstrip().startswith("#"):
            continue

        top = TOP_KEY_RE.match(line)
        if top and (len(line) - len(line.lstrip(" ")) == 0):
            key = top.group(1)
            if key == "input_select":
                in_input_select = True
                current_entity = None
                collecting_options = False
                options_indent = None
                continue
            if in_input_select and key != "input_select":
                # leaving input_select section
                in_input_select = False
                current_entity = None
                collecting_options = False
                options_indent = None

        if not in_input_select:
            continue

        ent = ENTITY_KEY_RE.match(line)
        if ent and not line.startswith("    "):
            # entity key at indent 2
            current_entity = ent.group(1)
            collecting_options = False
            options_indent = None
            continue

        if current_entity is None:
            continue

        optm = OPTIONS_RE.match(line)
        if optm:
            collecting_options = True
            options_indent = len(optm.group(1))
            continue

        if collecting_options:
            indent = len(line) - len(line.lstrip(" "))
            if indent <= (options_indent or 0):
                collecting_options = False
                options_indent = None
                continue

            li = LIST_ITEM_RE.match(line)
            if li:
                val = _strip_quotes(li.group(1))
                if val:
                    options_by_entity[current_entity].append(val)
            else:
                # non-list line ends the options block
                collecting_options = False
                options_indent = None

    return dict(options_by_entity)


def collect_input_select_used_values(lines):
    """Collect best-effort used values for input_selects from select_option calls and state conditions."""
    used_options: dict[str, set[str]] = defaultdict(set)
    used_states: dict[str, set[str]] = defaultdict(set)

    # 1) From service: input_select.select_option blocks (scoped by indent)
    for i, raw in enumerate(lines):
        line = raw.rstrip("\n")
        if line.lstrip().startswith("#"):
            continue
        if not SERVICE_SELECT_OPTION_RE.match(line):
            continue

        base_indent = len(line) - len(line.lstrip(" "))
        entity_ids = []
        options = []

        for w in lines[i + 1 : i + 40]:
            s = w.rstrip("\n")
            if s.lstrip().startswith("#"):
                continue

            indent = len(s) - len(s.lstrip(" "))
            if indent <= base_indent:
                break

            em = ENTITY_ID_LINE_RE.match(s)
            if em:
                entity_ids.append(em.group(1))
            om = OPTION_LINE_RE.match(s)
            if om:
                options.append(_strip_quotes(om.group(1)))

        if len(entity_ids) == 1 and len(options) == 1:
            used_options[entity_ids[0]].add(options[0])

    # 2) From conditions: entity_id: input_select.X + state: ... within the same mapping
    for i, raw in enumerate(lines):
        line = raw.rstrip("\n")
        if line.lstrip().startswith("#"):
            continue

        em = ENTITY_ID_LINE_RE.match(line)
        if not em:
            continue

        entity = em.group(1)
        entity_indent = len(line) - len(line.lstrip(" "))

        j = i + 1
        while j < len(lines):
            s = lines[j].rstrip("\n")
            if s.lstrip().startswith("#"):
                j += 1
                continue

            indent = len(s) - len(s.lstrip(" "))
            if indent <= entity_indent:
                break

            sm = STATE_LINE_RE.match(s)
            if sm and (len(s) - len(s.lstrip(" ")) == entity_indent):
                state_raw = sm.group(1).strip()

                # Inline scalar
                if state_raw:
                    used_states[entity].add(_strip_quotes(state_raw))
                    j += 1
                    continue

                # Multi-line list (state: then - 'X')
                state_indent = len(s) - len(s.lstrip(" "))
                k = j + 1
                while k < len(lines):
                    li = lines[k].rstrip("\n")
                    if li.lstrip().startswith("#"):
                        k += 1
                        continue
                    li_indent = len(li) - len(li.lstrip(" "))
                    if li_indent <= state_indent:
                        break
                    lim = LIST_ITEM_RE.match(li)
                    if lim:
                        used_states[entity].add(_strip_quotes(lim.group(1)))
                    k += 1

                j = k
                continue

            j += 1

    return used_options, used_states


def find_suspicious_options(options_by_entity: dict[str, list[str]]):
    findings = []

    for entity, options in sorted(options_by_entity.items()):
        # duplicates
        dupes = {o for o in options if options.count(o) > 1}
        if dupes:
            findings.append((entity, f"Duplicate option values: {sorted(dupes)}"))

        # whitespace
        bad_ws = [o for o in options if o != o.strip() or "  " in o]
        if bad_ws:
            findings.append((entity, f"Suspicious whitespace in options: {bad_ws}"))

        # mixed case patterns
        if any(o and o[0].islower() for o in options):
            findings.append((entity, "Some options start with lowercase (inconsistent with others)"))

    return findings


def main():
    yaml_files = list(iter_yaml_files(ROOT))

    options_by_entity: dict[str, list[str]] = defaultdict(list)
    used_options: dict[str, set[str]] = defaultdict(set)
    used_states: dict[str, set[str]] = defaultdict(set)

    for path in yaml_files:
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        lines = read_lines(path)

        found_opts = collect_input_select_options(lines)
        for entity, options in found_opts.items():
            # Keep a stable order but allow accumulation if defined across files (should be rare)
            for opt in options:
                if opt not in options_by_entity[entity]:
                    options_by_entity[entity].append(opt)

        uo, us = collect_input_select_used_values(lines)
        for entity, vals in uo.items():
            used_options[entity].update(vals)
        for entity, vals in us.items():
            used_states[entity].update(vals)

    print(f"Root: {ROOT}")
    print(f"YAML files scanned: {len(yaml_files)}")
    print(f"\ninput_select helpers found: {len(options_by_entity)}")

    for entity in sorted(options_by_entity):
        opts = options_by_entity[entity]
        print(f"\n- input_select.{entity} options ({len(opts)}):")
        for o in opts:
            print(f"  - {o}")

        # best-effort mismatch detection
        used = set()
        used.update(used_options.get(entity, set()))
        used.update(used_states.get(entity, set()))
        missing = sorted([u for u in used if u not in set(opts)])
        if missing:
            print(f"  ! Used values not in options: {missing}")

    findings = find_suspicious_options(options_by_entity)
    print("\nFindings:")
    if not findings:
        print("- No obvious option-string issues found")
    else:
        for entity, msg in findings:
            print(f"- input_select.{entity}: {msg}")


if __name__ == "__main__":
    main()
