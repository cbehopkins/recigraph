"""Base rendering view-model abstractions."""

from abc import ABC

from pydantic import BaseModel, ConfigDict


class ViewModel(BaseModel, ABC):
    """Abstract base model for renderer input contracts."""

    model_config = ConfigDict(frozen=True, extra="forbid")
