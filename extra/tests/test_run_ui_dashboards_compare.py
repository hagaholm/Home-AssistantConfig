from pathlib import Path

from extra.run_ui_dashboards_compare import run_server_comparison_export


def test_run_server_comparison_export_writes_dashboard_bundle(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "packages").mkdir()
    (root / "group").mkdir()
    (root / "sensor").mkdir()

    (root / "packages" / "example.yaml").write_text(
        "automation:\n  test_alert:\n    alias: Test alert\n",
        encoding="utf-8",
    )

    output_dir = root / "generated_ui" / "from_ha_server"
    result_dir = run_server_comparison_export(root=root, output_dir=output_dir)

    assert result_dir == output_dir
    assert (result_dir / "ui-generated-flat.yaml").exists()
    assert (result_dir / "ui-generated-grouped.yaml").exists()
    assert (result_dir / "ui-generated-entity-types.yaml").exists()
    assert (result_dir / "comparison_manifest.json").exists()
