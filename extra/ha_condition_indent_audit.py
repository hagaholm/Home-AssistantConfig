"""Home Assistant YAML audit: catch common condition indentation/key issues.

Motivation:
- Home Assistant config validation errors like:
  "extra keys not allowed ... ['choose'][...]['state']. Got 'Hemma'"
  often come from YAML indentation mistakes where a key (e.g. state:) ends up
  at the wrong level.

This script scans YAML files as plain text (no YAML parsing needed) and flags:
- `condition: state` blocks missing `entity_id`.
- `condition: state` blocks missing `state`/`state_not`.
- `condition: state` blocks where `state:` is present but not indented to the
  same level as `entity_id:`.

Similarly for `condition: numeric_state` blocks (expects entity_id and at least
one of `above:`/`below:` and indentation consistency).

Usage (Windows):
  py -3 extra/ha_condition_indent_audit.py
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Finding:
    file: Path
    line: int  # 1-based
    kind: str
    message: str

    def format(self) -> str:
        rel = self.file.relative_to(ROOT)
        return f"{rel}:{self.line}: {self.kind}: {self.message}"


_CONDITION_RE = re.compile(r"^(?P<indent>\s*)-\s+condition:\s*(?P<type>state|numeric_state)\s*$")
_KEY_RE = re.compile(r"^(?P<indent>\s*)(?P<key>[a-zA-Z_][a-zA-Z0-9_]*):\s*(?P<value>.*)$")


def iter_yaml_files(root: Path) -> Iterator[Path]:
    """Yield YAML files likely to contain HA automations/scripts.

    We intentionally avoid Lovelace UI YAML (e.g. ui-*.yaml) because it has
    concepts like `entity:` and `numeric_state` cards that don't follow HA
    automation condition schemas and would generate noise.
    """

    include_roots = {"packages", "automations"}

    for include_root in include_roots:
        base = root / include_root
        if not base.exists():
            continue
        for pattern in ("*.yaml", "*.yml"):
            for path in base.rglob(pattern):
                if any(part in {".git", "node_modules", "__pycache__"} for part in path.parts):
                    continue
                yield path


def leading_spaces(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def is_blank_or_comment(line: str) -> bool:
    stripped = line.strip()
    return stripped == "" or stripped.startswith("#")


def scan_condition_block(lines: list[str], start_idx: int) -> tuple[int, dict[str, tuple[int, int, str]]]:
    """Scan forward from a `- condition: X` line.

    Returns:
      end_idx (exclusive), keys dict: key -> (line_index, indent, raw_value)
    """
    match = _CONDITION_RE.match(lines[start_idx])
    assert match

    base_indent = leading_spaces(lines[start_idx])
    keys: dict[str, tuple[int, int, str]] = {}

    idx = start_idx + 1
    while idx < len(lines):
        line = lines[idx]
        if is_blank_or_comment(line):
            idx += 1
            continue

        indent = leading_spaces(line)
        # If we hit a new list item at the same or lower level, we're out.
        if indent <= base_indent and line.lstrip().startswith("-"):
            break
        if indent < base_indent:
            break

        m_key = _KEY_RE.match(line)
        if m_key:
            key = m_key.group("key")
            value = m_key.group("value").strip()
            keys.setdefault(key, (idx, indent, value))

        idx += 1

    return idx, keys


def audit_file(path: Path) -> list[Finding]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8-sig")

    lines = text.splitlines()
    findings: list[Finding] = []

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        m = _CONDITION_RE.match(line)
        if not m:
            idx += 1
            continue

        cond_type = m.group("type")
        end_idx, keys = scan_condition_block(lines, idx)

        def add(kind: str, msg: str) -> None:
            findings.append(Finding(file=path, line=idx + 1, kind=kind, message=msg))

        if cond_type == "state":
            entity = keys.get("entity_id")
            state = keys.get("state")
            state_not = keys.get("state_not")

            if entity is None:
                add("state_condition", "Missing required key `entity_id:`")
            if state is None and state_not is None:
                add("state_condition", "Missing `state:` or `state_not:`")

            if entity is not None and (state is not None or state_not is not None):
                entity_indent = entity[1]
                chosen = state if state is not None else state_not
                assert chosen is not None
                state_key = "state" if state is not None else "state_not"
                if chosen[1] != entity_indent:
                    add(
                        "state_condition",
                        f"Indent mismatch: `{state_key}:` at {chosen[1]} spaces, `entity_id:` at {entity_indent} spaces",
                    )

        elif cond_type == "numeric_state":
            entity = keys.get("entity_id")
            above = keys.get("above")
            below = keys.get("below")

            if entity is None:
                add("numeric_state_condition", "Missing required key `entity_id:`")
            if above is None and below is None:
                add("numeric_state_condition", "Missing `above:` and `below:` (need at least one)")

            # If both present, ensure they match entity indentation.
            if entity is not None:
                entity_indent = entity[1]
                for k, v in (("above", above), ("below", below)):
                    if v is not None and v[1] != entity_indent:
                        add(
                            "numeric_state_condition",
                            f"Indent mismatch: `{k}:` at {v[1]} spaces, `entity_id:` at {entity_indent} spaces",
                        )

        idx = end_idx

    return findings


def main() -> int:
    yaml_files = sorted(set(iter_yaml_files(ROOT)))
    all_findings: list[Finding] = []

    for path in yaml_files:
        all_findings.extend(audit_file(path))

    print(f"Root: {ROOT}")
    print(f"YAML files scanned: {len(yaml_files)}")
    print("")

    if not all_findings:
        print("Findings: none")
        return 0

    print(f"Findings: {len(all_findings)}")
    for finding in all_findings:
        print(finding.format())

    # Non-zero exit so it can be used in CI/tasks.
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
