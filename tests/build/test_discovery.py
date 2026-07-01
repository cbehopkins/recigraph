"""Tests for build-layer source discovery."""

from pathlib import Path

from recigraph.build.discovery import discover_recipe_sources


def test_discover_recipe_sources_returns_sorted_yaml_files(tmp_path: Path) -> None:
    source_dir = tmp_path / "recipes"
    source_dir.mkdir()
    (source_dir / "z_last.yaml").write_text("id: procedure.z_last\nsteps: []\n", encoding="utf-8")
    nested_dir = source_dir / "nested"
    nested_dir.mkdir()
    (nested_dir / "a_first.yml").write_text("id: procedure.a_first\nsteps: []\n", encoding="utf-8")
    (source_dir / "ignore.txt").write_text("not yaml", encoding="utf-8")

    discovered = discover_recipe_sources(source_dir)

    assert discovered == (
        nested_dir / "a_first.yml",
        source_dir / "z_last.yaml",
    )


def test_discover_recipe_sources_rejects_missing_directory(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    try:
        discover_recipe_sources(missing)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError for missing recipe source directory")
