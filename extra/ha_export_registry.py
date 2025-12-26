import argparse
import csv
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_STORAGE_DIRS = [
    Path("/config/.storage"),  # typical in HA OS / Container
    Path(r"C:\config\.storage"),
]


def _sha256_short(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:12]


def _redact_any(value: Any, *, salt: str) -> Any:
    """Redact common sensitive fields while preserving stable identity via hashing."""

    if value is None:
        return None

    if isinstance(value, (int, float, bool)):
        return value

    if isinstance(value, str):
        # Keep short, non-sensitive strings as-is, hash the rest.
        # This is intentionally conservative.
        if value.startswith("automation.") or value.startswith("sensor.") or value.startswith("binary_sensor."):
            return value
        if len(value) <= 6:
            return value
        return f"hash:{_sha256_short(salt + value)}"

    if isinstance(value, list):
        return [_redact_any(v, salt=salt) for v in value]

    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            lk = str(k).lower()
            # Known sensitive-ish keys in HA registries
            if lk in {
                "identifiers",
                "connections",
                "mac",
                "ip",
                "host",
                "hostname",
                "serial_number",
                "serial",
                "token",
                "access_token",
                "refresh_token",
                "api_key",
                "webhook_id",
            }:
                out[k] = _redact_any(v, salt=salt)
            else:
                out[k] = _redact_any(v, salt=salt)
        return out

    # Fallback
    return f"hash:{_sha256_short(salt + repr(value))}"


def read_storage_json(path: Path) -> dict[str, Any]:
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


@dataclass(frozen=True)
class ExportConfig:
    storage_dir: Path
    out_dir: Path
    salt: str
    include_raw: bool


def extract_entity_registry(reg: dict[str, Any]) -> list[dict[str, Any]]:
    entities = reg.get("data", {}).get("entities", []) or []
    out: list[dict[str, Any]] = []
    for e in entities:
        out.append(
            {
                "entity_id": e.get("entity_id"),
                "unique_id": e.get("unique_id"),
                "platform": e.get("platform"),
                "original_name": e.get("original_name"),
                "device_id": e.get("device_id"),
                "area_id": e.get("area_id"),
                "disabled_by": e.get("disabled_by"),
                "hidden_by": e.get("hidden_by"),
            }
        )
    return out


def extract_device_registry(reg: dict[str, Any]) -> list[dict[str, Any]]:
    devices = reg.get("data", {}).get("devices", []) or []
    out: list[dict[str, Any]] = []
    for d in devices:
        out.append(
            {
                "id": d.get("id"),
                "name": d.get("name"),
                "name_by_user": d.get("name_by_user"),
                "manufacturer": d.get("manufacturer"),
                "model": d.get("model"),
                "sw_version": d.get("sw_version"),
                "hw_version": d.get("hw_version"),
                "area_id": d.get("area_id"),
                "via_device_id": d.get("via_device_id"),
                "identifiers": d.get("identifiers"),
                "connections": d.get("connections"),
            }
        )
    return out


def extract_area_registry(reg: dict[str, Any]) -> list[dict[str, Any]]:
    areas = reg.get("data", {}).get("areas", []) or []
    out: list[dict[str, Any]] = []
    for a in areas:
        out.append(
            {
                "area_id": a.get("id"),
                "name": a.get("name"),
                "picture": a.get("picture"),
            }
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export a sanitized Home Assistant inventory from /config/.storage registries "
            "(entities/devices/areas). This is useful for mapping the real entity_ids "
            "to YAML files/ids when editing dashboards like ui-automation.yaml."
        )
    )
    parser.add_argument(
        "--storage-dir",
        type=Path,
        default=None,
        help="Path to HA .storage directory (default: auto-detect, e.g. /config/.storage)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("exports/ha_inventory"),
        help="Output directory (default: exports/ha_inventory)",
    )
    parser.add_argument(
        "--salt",
        default=os.environ.get("HA_EXPORT_SALT", ""),
        help="Salt used for hashing/redaction (or set env var HA_EXPORT_SALT)",
    )
    parser.add_argument(
        "--include-raw",
        action="store_true",
        help="Also copy raw registry JSON files (NOT recommended to commit)",
    )
    args = parser.parse_args()

    storage_dir = args.storage_dir
    if storage_dir is None:
        for candidate in DEFAULT_STORAGE_DIRS:
            if candidate.exists():
                storage_dir = candidate
                break

    if storage_dir is None or not storage_dir.exists():
        print(
            "ERROR: Could not find a Home Assistant .storage directory.\n"
            "Pass --storage-dir /config/.storage (on the HA host), or copy the .storage folder\n"
            "to this repo and point --storage-dir to it.",
            flush=True,
        )
        return 2

    salt = args.salt.strip()
    if not salt:
        # Stable default derived from path; not secret, but prevents leaking raw identifiers.
        salt = str(storage_dir)

    cfg = ExportConfig(
        storage_dir=storage_dir,
        out_dir=args.out_dir,
        salt=salt,
        include_raw=args.include_raw,
    )

    entity_path = cfg.storage_dir / "core.entity_registry"
    device_path = cfg.storage_dir / "core.device_registry"
    area_path = cfg.storage_dir / "core.area_registry"

    missing = [p for p in [entity_path, device_path, area_path] if not p.exists()]
    if missing:
        print("ERROR: Missing registry files:")
        for p in missing:
            print(f"- {p}")
        return 2

    entity_reg = read_storage_json(entity_path)
    device_reg = read_storage_json(device_path)
    area_reg = read_storage_json(area_path)

    entities = extract_entity_registry(entity_reg)
    devices = extract_device_registry(device_reg)
    areas = extract_area_registry(area_reg)

    snapshot = {
        "meta": {
            "source_storage_dir": str(cfg.storage_dir),
            "note": "Sanitized export. Values are hashed/redacted.",
        },
        "areas": _redact_any(areas, salt=cfg.salt),
        "devices": _redact_any(devices, salt=cfg.salt),
        "entities": _redact_any(entities, salt=cfg.salt),
    }

    write_json(cfg.out_dir / "ha_inventory.sanitized.json", snapshot)

    # CSVs are handy for quick diff/grep in git
    write_csv(
        cfg.out_dir / "entities.csv",
        entities,
        fieldnames=[
            "entity_id",
            "unique_id",
            "platform",
            "original_name",
            "device_id",
            "area_id",
            "disabled_by",
            "hidden_by",
        ],
    )
    write_csv(
        cfg.out_dir / "devices.csv",
        devices,
        fieldnames=[
            "id",
            "name",
            "name_by_user",
            "manufacturer",
            "model",
            "sw_version",
            "hw_version",
            "area_id",
            "via_device_id",
        ],
    )
    write_csv(cfg.out_dir / "areas.csv", areas, fieldnames=["area_id", "name", "picture"])

    if cfg.include_raw:
        raw_dir = cfg.out_dir / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        (raw_dir / "core.entity_registry").write_text(entity_path.read_text(encoding="utf-8"), encoding="utf-8")
        (raw_dir / "core.device_registry").write_text(device_path.read_text(encoding="utf-8"), encoding="utf-8")
        (raw_dir / "core.area_registry").write_text(area_path.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Wrote: {cfg.out_dir / 'ha_inventory.sanitized.json'}")
    print(f"Wrote: {cfg.out_dir / 'entities.csv'}")
    print(f"Wrote: {cfg.out_dir / 'devices.csv'}")
    print(f"Wrote: {cfg.out_dir / 'areas.csv'}")
    if cfg.include_raw:
        print(f"Wrote raw registries under: {cfg.out_dir / 'raw'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
