"""Configuration models for build-layer orchestration."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict


class BuildConfig(BaseModel):
    """Inputs controlling deterministic site-build orchestration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_dir: Path
    output_dir: Path
    recipe_patterns: tuple[str, ...] = ("*.yaml", "*.yml")
    clean_output_dir: bool = True

    @property
    def normalized_patterns(self) -> tuple[str, ...]:
        """Return a deterministic tuple of non-empty file glob patterns."""

        patterns = tuple(pattern for pattern in self.recipe_patterns if pattern)
        if not patterns:
            raise ValueError("BuildConfig requires at least one recipe discovery pattern")
        return patterns
