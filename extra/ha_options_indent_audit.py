"""Audit YAML indentation under `options:` lists.

Home Assistant configs commonly break when an `options:` list has a misindented
item (e.g. one `- Foo` line has fewer/more spaces than its siblings).

This script performs a lightweight text scan (no YAML parsing) to detect:
- First non-comment line under `options:` is not a list item
- List items under `options:` have inconsistent indentation
- Non-list lines appear at the same indentation level as list items

It intentionally ignores Lovelace dashboards and *_not_used files.

Usage:
  py -3 extra\\ha_options_indent_audit.py

Exit codes:
  0 = no findings
  1 = findings present
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Finding:
    line: int
    message: str
    snippet: str | None = None


_OPTIONS_RE = re.compile(r"^\s*options\s*:\s*(#.*)?$")


def _is_ignored_file(path: Path) -> bool:
    name = path.name
    if name.startswith("ui-") and name.endswith(".yaml"):
        return True
    if name.endswith(".yaml_not_used") or name.endswith("_not_used.yaml"):
        return True
    return False


def _iter_yaml_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.yaml"):
        if any(part in {".git", ".vscode"} for part in path.parts):
            continue
        if _is_ignored_file(path):
            continue
        files.append(path)
    return sorted(files)


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def scan_file(path: Path) -> list[Finding]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    findings: list[Finding] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        if not _OPTIONS_RE.match(line):
            i += 1
            continue

        options_line_no = i + 1
        options_indent = _indent_of(line)

        # find first meaningful line after options:
        j = i + 1
        while j < len(lines) and (lines[j].strip() == "" or lines[j].lstrip().startswith("#")):
            j += 1

        if j >= len(lines):
            findings.append(Finding(options_line_no, "`options:` at EOF"))
            i = j
            continue

        first = lines[j]
        first_indent = _indent_of(first)
        if first_indent <= options_indent:
            findings.append(
                Finding(
                    options_line_no,
                    f"First line under `options:` is not indented (options indent={options_indent}, next indent={first_indent})",
                    first.strip() or None,
                )
            )
            i = j
            continue

        if not first.lstrip().startswith("- "):
            findings.append(
                Finding(
                    options_line_no,
                    "First non-comment line under `options:` is not a list item",
                    first.strip() or None,
                )
            )
            i = j
            continue

        item_indent = first_indent
        bad: list[Finding] = []

        k = j
        while k < len(lines):
            cur = lines[k]
            if cur.strip() == "" or cur.lstrip().startswith("#"):
                k += 1
                continue

            cur_indent = _indent_of(cur)
            if cur_indent <= options_indent:
                break

            # If we hit another mapping key at the same indent as items, list ended.
            if cur_indent == item_indent and re.match(r"^[^\s#-][^:]*:\s*", cur.lstrip()):
                break

            if cur.lstrip().startswith("- "):
                if cur_indent != item_indent:
                    bad.append(
                        Finding(
                            k + 1,
                            f"List item indent differs (expected {item_indent}, got {cur_indent})",
                            cur.strip() or None,
                        )
                    )
            else:
                # Allow multi-line scalar continuations, but they must be more indented than item lines.
                if cur_indent <= item_indent:
                    bad.append(
                        Finding(
                            k + 1,
                            f"Non-item line at item indentation level (expected > {item_indent} for continuation)",
                            cur.strip() or None,
                        )
                    )

            k += 1

        if bad:
            findings.append(
                Finding(
                    options_line_no,
                    f"Inconsistent indentation under `options:` (expected item indent {item_indent})",
                )
            )
            findings.extend(bad)

        i = k

    return findings


def main() -> int:
    yaml_files = _iter_yaml_files(ROOT)
    problems: list[tuple[Path, list[Finding]]] = []

    for path in yaml_files:
        findings = scan_file(path)
        if findings:
            problems.append((path, findings))

    print(f"Root: {ROOT}")
    print(f"YAML files scanned: {len(yaml_files)}")
    print(f"Files with suspicious `options:` indentation: {len(problems)}")

    for path, findings in problems:
        rel = path.relative_to(ROOT).as_posix()
        print(f"\n{rel}")
        for f in findings[:40]:
            if f.snippet:
                print(f"  line {f.line}: {f.message} :: {f.snippet}")
            else:
                print(f"  line {f.line}: {f.message}")
        if len(findings) > 40:
            print("  ...")

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
