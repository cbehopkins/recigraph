"""Compiler output and trace models."""

from pydantic import BaseModel, ConfigDict, Field

from recigraph.model.graph import GraphState
from recigraph.model.reference import ReferenceBinding


class StepExecutionRecord(BaseModel):
    """Trace entry for a single Step application."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_id: str = Field(min_length=1)
    input_graph_snapshot_ref: str = Field(min_length=1)
    applied_bindings: tuple[ReferenceBinding, ...] = ()
    output_graph_snapshot_ref: str = Field(min_length=1)
    transformations_applied: tuple[str, ...] = ()


class CompilerOutput(BaseModel):
    """Final result of a compile run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    final_graph: GraphState
    trace: tuple[StepExecutionRecord, ...] = ()
