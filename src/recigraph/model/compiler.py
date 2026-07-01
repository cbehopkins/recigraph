"""Compiler output, context, and trace models."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from recigraph.model.graph import GraphState
from recigraph.model.procedure import Procedure
from recigraph.model.reference import ReferenceBinding


class StepExecutionRecord(BaseModel):
    """Trace entry for a single Step application."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_id: str = Field(min_length=1)
    input_graph_snapshot_ref: str = Field(min_length=1)
    applied_bindings: tuple[ReferenceBinding, ...] = ()
    output_graph_snapshot_ref: str = Field(min_length=1)
    transformation_summary: str = Field(min_length=1)
    transformations_applied: tuple[str, ...] = ()


class CompilationContext(BaseModel):
    """Explicit compiler state container shared across compilation passes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    registries: Any
    config: tuple[tuple[str, str], ...] = ()
    diagnostics: tuple[str, ...] = ()
    current_graph: GraphState | None = None
    trace: tuple[StepExecutionRecord, ...] = ()
    procedure: Procedure | None = None
    resolved_reference_count: int = 0


class CompilerOutput(BaseModel):
    """Final result of a compile run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    final_graph: GraphState
    trace: tuple[StepExecutionRecord, ...] = ()
