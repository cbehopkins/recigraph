"""Tests for the Phase 4 structural validation layer."""

import pytest

from recigraph.model import EntityReference, Procedure, ReferenceBinding, Step
from recigraph.validation import (
    ProcedureValidationError,
    assert_valid_procedure_structure,
    validate_procedure_structure,
)


def _valid_procedure() -> Procedure:
    return Procedure(
        id="procedure.vanilla_base",
        steps=(
            Step(
                id="mix_base",
                action=EntityReference(domain="procedure", identifier="mix"),
                inputs=(
                    ReferenceBinding(
                        target=EntityReference(domain="ingredient", identifier="whole_milk")
                    ),
                ),
                outputs=(EntityReference(domain="ingredient", identifier="base_mix"),),
            ),
        ),
        inputs=(EntityReference(domain="ingredient", identifier="whole_milk"),),
        outputs=(EntityReference(domain="ingredient", identifier="base_mix"),),
    )


def test_validate_procedure_structure_accepts_valid_procedure() -> None:
    issues = validate_procedure_structure(_valid_procedure())

    assert issues == ()


def test_validate_procedure_structure_requires_at_least_one_step() -> None:
    procedure = Procedure(id="procedure.vanilla_base", steps=())

    issues = validate_procedure_structure(procedure)

    assert any(issue.code == "REQUIRED_STEPS" for issue in issues)


def test_validate_procedure_structure_rejects_duplicate_step_ids() -> None:
    procedure = Procedure(
        id="procedure.vanilla_base",
        steps=(
            Step(id="mix_base", action=EntityReference(domain="procedure", identifier="mix")),
            Step(id="mix_base", action=EntityReference(domain="procedure", identifier="heat")),
        ),
    )

    issues = validate_procedure_structure(procedure)

    assert any(issue.code == "DUPLICATE_STEP_ID" for issue in issues)


def test_validate_procedure_structure_rejects_invalid_step_id_format() -> None:
    procedure = Procedure(
        id="procedure.vanilla_base",
        steps=(Step(id="Mix Base", action=EntityReference(domain="procedure", identifier="mix")),),
    )

    issues = validate_procedure_structure(procedure)

    assert any(issue.code == "STEP_ID_FORMAT" for issue in issues)


def test_assert_valid_procedure_structure_raises_with_diagnostics() -> None:
    procedure = Procedure(id="procedure.vanilla_base", steps=())

    with pytest.raises(ProcedureValidationError, match="REQUIRED_STEPS"):
        assert_valid_procedure_structure(procedure)
