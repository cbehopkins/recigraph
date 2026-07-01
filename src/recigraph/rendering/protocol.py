"""Renderer protocol abstractions for output artifact generation."""

from pathlib import Path
from typing import Protocol

from recigraph.rendering.common.result import RenderResult
from recigraph.rendering.common.view_model import ViewModel


class Renderer(Protocol):
    """Contract for deterministic renderer implementations."""

    name: str

    def render(self, model: ViewModel, output_dir: Path) -> RenderResult: ...
