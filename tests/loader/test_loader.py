"""Tests for YAML loading helpers."""

from pathlib import Path

import pytest

from recigraph.loader import load_yaml_file, load_yaml_text


def test_load_yaml_text_returns_mapping() -> None:
    payload = load_yaml_text("id: procedure.vanilla_base\nsteps: []\n")

    assert payload["id"] == "procedure.vanilla_base"
    assert payload["steps"] == []


def test_load_yaml_text_rejects_non_mapping_root() -> None:
    with pytest.raises(TypeError, match="root must be a mapping"):
        load_yaml_text("- procedure.vanilla_base\n")


def test_load_yaml_file_reads_utf8_content(tmp_path: Path) -> None:
    file_path = tmp_path / "procedure.yaml"
    file_path.write_text("id: procedure.vanilla_base\nsteps: []\n", encoding="utf-8")

    payload = load_yaml_file(file_path)

    assert payload["id"] == "procedure.vanilla_base"
