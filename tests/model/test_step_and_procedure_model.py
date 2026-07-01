"""Tests for Step and Procedure models."""

import pytest
from pydantic import ValidationError

from recigraph.model import (
    EntityReference,
    OverrideSet,
    Procedure,
    ReferenceBinding,
    Step,
    StepContext,
    Substitution,
)


def test_step_accepts_local_reference_bindings_only() -> None:
    step = Step(
        id="mix_base",
        action=EntityReference(domain="procedure", identifier="mix"),
        inputs=(
            ReferenceBinding(
                target=EntityReference(domain="ingredient", identifier="whole_milk"),
                override=OverrideSet(
                    substitutions=(
                        Substitution.model_validate({
                            "from": EntityReference(domain="ingredient", identifier="whole_milk"),
                            "to": EntityReference(domain="ingredient", identifier="oat_milk"),
                        }),
                    )
                ),
            ),
        ),
        outputs=(EntityReference(domain="ingredient", identifier="mixed_base"),),
        context=StepContext(notes="example", tags=("base",), constraints=("cold",)),
    )

    assert isinstance(step.inputs[0], ReferenceBinding)
    assert step.context is not None
    assert step.context.tags == ("base",)


def test_step_rejects_non_procedure_action() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Step(
            action=EntityReference(domain="ingredient", identifier="whole_milk"),
        )

    assert "step action must reference a procedure" in str(exc_info.value)


def test_procedure_inputs_remain_entity_references_not_bindings() -> None:
    procedure = Procedure(
        id="procedure.vanilla_base",
        steps=(Step(action=EntityReference(domain="procedure", identifier="mix")),),
        inputs=(
            EntityReference(domain="ingredient", identifier="whole_milk"),
            EntityReference(domain="ingredient", identifier="sugar"),
        ),
        outputs=(EntityReference(domain="ingredient", identifier="base_mix"),),
    )

    assert all(isinstance(item, EntityReference) for item in procedure.inputs)
    assert procedure.steps[0].inputs == ()


def test_procedure_rejects_binding_shapes_in_inputs() -> None:
    with pytest.raises(ValidationError):
        Procedure.model_validate({
            "id": "procedure.vanilla_base",
            "steps": [
                {"action": {"domain": "procedure", "identifier": "mix"}},
            ],
            "inputs": [
                {"target": {"domain": "ingredient", "identifier": "whole_milk"}},
            ],
        })
