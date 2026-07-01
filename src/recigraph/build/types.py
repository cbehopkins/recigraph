"""Shared data models used by build orchestration stages."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict

from recigraph.model import CompilerOutput


class CompiledRecipe(BaseModel):
    """Compiled Graph IR and metadata for a single source recipe file."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_path: Path
    output: CompilerOutput
