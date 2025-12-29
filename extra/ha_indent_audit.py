import argparse
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SKIP_DIRS = {
    ".git",
    ".storage",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
}


def iter_yaml_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            if filename.lower().endswith(".yaml"):
                yield os.path.join(dirpath, filename)


def read_lines(path: str) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.readlines()
    except UnicodeDecodeError:
        with open(path, "r", encoding="latin-1") as file:
            return file.readlines()


BLOCK_SCALAR_RE = re.compile(r"^\s*[^#].*:\s*[>|]\s*(#.*)?$")
OPTIONS_KEY_RE = re.compile(r"^(?P<indent>\s*)options:\s*(#.*)?$")


def audit_file(path: str, *, indent_multiple: int = 2, warn_indent_jumps: bool = False):
    lines = read_lines(path)

    errors: list[tuple[int, str]] = []
    warnings: list[tuple[int, str]] = []

    in_block_scalar = False
    block_scalar_indent = 0
    last_significant_indent: int | None = None

    in_options_list = False
    options_key_indent = 0
    options_item_indent: int | None = None

    for idx, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")

        if not line.strip() or line.lstrip().startswith("#"):
            continue

        leading = line[: len(line) - len(line.lstrip(" \t"))]

        if "\t" in leading:
            errors.append((idx, "Tab character used for indentation"))
            continue

        indent = len(leading)

        # End of an `options:` list block when indentation returns to (or above) the key level.
        if in_options_list:
            stripped = line.lstrip(" ")
            if indent <= options_key_indent and not stripped.startswith("-"):
                in_options_list = False
                options_item_indent = None
            elif stripped.startswith("-"):
                if indent <= options_key_indent:
                    errors.append(
                        (
                            idx,
                            "List item under `options:` must be indented more than the key",
                        )
                    )
                else:
                    if options_item_indent is None:
                        options_item_indent = indent
                    elif indent != options_item_indent:
                        errors.append(
                            (
                                idx,
                                f"Misaligned `options:` item indent (expected {options_item_indent} spaces, got {indent})",
                            )
                        )

        # Track block scalars (| / >). Inside scalars indentation may not follow our conventions.
        if in_block_scalar:
            if indent <= block_scalar_indent:
                in_block_scalar = False
            else:
                continue

        if BLOCK_SCALAR_RE.match(line):
            in_block_scalar = True
            block_scalar_indent = indent

        options_match = OPTIONS_KEY_RE.match(line)
        if options_match:
            in_options_list = True
            options_key_indent = len(options_match.group("indent"))
            options_item_indent = None

        if indent_multiple and indent % indent_multiple != 0:
            errors.append((idx, f"Indentation is not a multiple of {indent_multiple} spaces"))

        if warn_indent_jumps and last_significant_indent is not None:
            if indent > last_significant_indent + indent_multiple:
                warnings.append(
                    (
                        idx,
                        f"Indent jump {last_significant_indent} -> {indent} spaces (unusual)",
                    )
                )

        last_significant_indent = indent

    return errors, warnings


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Heuristic indentation audit for Home Assistant YAML files. "
            "Catches common issues (tabs, odd indentation) that can break YAML." 
            "Does not fully parse YAML."
        )
    )
    parser.add_argument(
        "--root",
        default=ROOT,
        help="Repo root to scan (default: inferred from script location)",
    )
    parser.add_argument(
        "--indent-multiple",
        type=int,
        default=2,
        help="Require indentation to be a multiple of this number of spaces (default: 2)",
    )
    parser.add_argument(
        "--warn-indent-jumps",
        action="store_true",
        help="Also warn on unusually large indentation jumps (can be noisy)",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=200,
        help="Max number of findings to print (default: 200)",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional files/folders (relative to repo root) to scan instead of whole repo",
    )

    args = parser.parse_args()

    root = os.path.abspath(args.root)

    scan_roots: list[str]
    if args.paths:
        scan_roots = [os.path.abspath(os.path.join(root, p)) for p in args.paths]
    else:
        scan_roots = [root]

    yaml_files: list[str] = []
    for scan_root in scan_roots:
        if os.path.isdir(scan_root):
            yaml_files.extend(iter_yaml_files(scan_root))
        elif os.path.isfile(scan_root) and scan_root.lower().endswith(".yaml"):
            yaml_files.append(scan_root)

    yaml_files = sorted(set(yaml_files))

    total_errors = 0
    total_warnings = 0
    printed = 0

    for path in yaml_files:
        errors, warnings = audit_file(
            path,
            indent_multiple=args.indent_multiple,
            warn_indent_jumps=args.warn_indent_jumps,
        )
        if not errors and not warnings:
            continue

        total_errors += len(errors)
        total_warnings += len(warnings)

        for line_no, message in errors:
            if printed >= args.max:
                break
            print(f"ERROR: {rel(path)}:{line_no}: {message}")
            printed += 1

        for line_no, message in warnings:
            if printed >= args.max:
                break
            print(f"WARN : {rel(path)}:{line_no}: {message}")
            printed += 1

        if printed >= args.max:
            break

    print(
        f"\nIndent audit complete. YAML files scanned: {len(yaml_files)}. "
        f"Errors: {total_errors}. Warnings: {total_warnings}."
    )

    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
