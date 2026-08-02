import json
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extra.generate_ui_dashboards import generate_dashboards


def run_server_comparison_export(*, root: Optional[Path] = None, output_dir: Optional[Path] = None) -> Path:
    """Generate a stable dashboard bundle for server-vs-windows comparison."""
    root_path = (root or Path(__file__).resolve().parent.parent).resolve()
    export_dir = (output_dir or (root_path / "generated_ui" / "from_ha_server")).resolve()
    export_dir.mkdir(parents=True, exist_ok=True)

    generated_files = generate_dashboards(root=root_path, output_dir=export_dir, include_entity_type_dashboard=True)

    manifest = {
        "root": str(root_path),
        "generated_files": [path.name for path in generated_files],
        "output_dir": str(export_dir),
    }
    (export_dir / "comparison_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return export_dir


if __name__ == "__main__":
    run_server_comparison_export()
