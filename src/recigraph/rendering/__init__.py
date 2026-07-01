"""Renderer architecture for presentation-focused artifact generation."""

from recigraph.rendering.common.artifact import RenderArtifact
from recigraph.rendering.common.result import RenderResult
from recigraph.rendering.common.view_model import ViewModel
from recigraph.rendering.protocol import Renderer

__all__ = [
    "RenderArtifact",
    "RenderResult",
    "Renderer",
    "ViewModel",
]
