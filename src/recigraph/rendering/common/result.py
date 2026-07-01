"""Structured result models returned by renderers."""

from pydantic import ConfigDict, Field

from recigraph.rendering.common.artifact import RenderArtifact
from recigraph.rendering.common.view_model import ViewModel


class RenderResult(ViewModel):
    """Structured output manifest from a single renderer run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    renderer_name: str = Field(min_length=1)
    artifacts: tuple[RenderArtifact, ...] = ()
