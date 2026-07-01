"""YAML loading utilities for ReciGraph documents."""

from pathlib import Path
from typing import Any, cast

import yaml


def load_yaml_text(text: str) -> dict[str, Any]:
    """Load YAML text into a mapping payload."""

    loaded_obj: object = yaml.safe_load(text)
    if loaded_obj is None:
        return {}
    if not isinstance(loaded_obj, dict):
        raise TypeError("procedure YAML root must be a mapping")

    payload: dict[str, Any] = {}
    for key, value in cast("dict[object, object]", loaded_obj).items():
        if not isinstance(key, str):
            raise TypeError("procedure YAML root keys must be strings")
        payload[key] = value
    return payload


def load_yaml_file(path: str | Path) -> dict[str, Any]:
    """Load YAML from a file path into a mapping payload."""

    file_path = Path(path)
    return load_yaml_text(file_path.read_text(encoding="utf-8"))
