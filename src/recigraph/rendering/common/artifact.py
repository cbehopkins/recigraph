"""Models describing artifacts emitted by renderer implementations."""

from pathlib import Path

from pydantic import ConfigDict, Field

from recigraph.rendering.common.view_model import ViewModel


class RenderArtifact(ViewModel):
    """Single generated artifact emitted by a renderer."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    relative_path: Path
    media_type: str = Field(min_length=1)
