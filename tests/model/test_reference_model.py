"""Tests for the DSL reference models."""

import pytest
from pydantic import ValidationError

from recigraph.model import (
    Adjustment,
    Composition,
    EntityReference,
    OverrideSet,
    ReferenceBinding,
    Substitution,
)


def test_entity_reference_uses_dotted_syntax() -> None:
    reference = EntityReference(domain="ingredient", identifier="whole_milk")

    assert str(reference) == "ingredient.whole_milk"
    assert reference.reference_text == "ingredient.whole_milk"


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"domain": "mixture", "identifier": "whole_milk"}, "literal_error"),
        ({"domain": "ingredient", "identifier": "WholeMilk"}, "string_pattern_mismatch"),
        ({"domain": "ingredient", "identifier": "whole_milk", "version": ""}, "version"),
    ],
)
def test_entity_reference_rejects_invalid_syntax(payload: dict[str, object], message: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        EntityReference.model_validate(payload)

    assert message in str(exc_info.value)


def test_reference_binding_supports_step_local_composition() -> None:
    binding = ReferenceBinding(
        target=EntityReference(domain="ingredient", identifier="whole_milk"),
        override=OverrideSet(
            substitutions=(
                Substitution.model_validate({
                    "from": EntityReference(domain="ingredient", identifier="whole_milk"),
                    "to": Composition(
                        ingredients=(
                            EntityReference(domain="ingredient", identifier="oat_milk"),
                            EntityReference(domain="ingredient", identifier="sugar"),
                        ),
                        adjustments=(
                            Adjustment(
                                type="add",
                                target=EntityReference(domain="ingredient", identifier="vanilla"),
                            ),
                        ),
                    ),
                }),
            ),
        ),
    )

    assert binding.override is not None
    assert isinstance(binding.override.substitutions[0], Substitution)
    assert isinstance(binding.override.substitutions[0].to, Composition)
    assert isinstance(binding.override.substitutions[0].to.adjustments[0], Adjustment)
