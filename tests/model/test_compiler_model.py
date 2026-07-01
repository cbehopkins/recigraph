"""Tests for GraphState, StepExecutionRecord, and CompilerOutput."""

import pytest
from pydantic import ValidationError

from recigraph.model import (
    CompilerOutput,
    EntityReference,
    GraphState,
    ReferenceBinding,
    StepExecutionRecord,
)


def test_graph_state_is_immutable_and_snapshotted() -> None:
    graph = GraphState(
        snapshot_id="g0",
        entities=(EntityReference(domain="ingredient", identifier="whole_milk"),),
        metadata=(("source", "seed"),),
    )

    with pytest.raises(ValidationError):
        graph.snapshot_id = "g1"  # type: ignore[misc]


def test_step_execution_record_tracks_step_local_bindings() -> None:
    binding = ReferenceBinding(
        target=EntityReference(domain="ingredient", identifier="whole_milk"),
    )
    record = StepExecutionRecord(
        step_id="mix_base",
        input_graph_snapshot_ref="g0",
        applied_bindings=(binding,),
        output_graph_snapshot_ref="g1",
        transformation_summary="action=procedure.mix; bindings=1; outputs=none; transformations=1",
        transformations_applied=("substitute whole milk",),
    )

    assert record.applied_bindings == (binding,)


def test_compiler_output_wraps_final_graph_and_trace() -> None:
    output = CompilerOutput(
        final_graph=GraphState(snapshot_id="g1"),
        trace=(
            StepExecutionRecord(
                step_id="mix_base",
                input_graph_snapshot_ref="g0",
                applied_bindings=(),
                output_graph_snapshot_ref="g1",
                transformation_summary=(
                    "action=procedure.mix; bindings=0; outputs=none; transformations=0"
                ),
                transformations_applied=(),
            ),
        ),
    )

    assert output.final_graph.snapshot_id == "g1"
    assert len(output.trace) == 1
