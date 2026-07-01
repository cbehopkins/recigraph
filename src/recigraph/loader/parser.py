"""YAML payload to model parser for ReciGraph procedures."""

import re
from collections.abc import Sequence
from pathlib import Path
from typing import Literal, cast

from recigraph.loader.loader import load_yaml_file, load_yaml_text
from recigraph.model import (
    Adjustment,
    Composition,
    EntityReference,
    OverrideSet,
    Procedure,
    ReferenceBinding,
    Step,
    StepContext,
    Substitution,
)

_REFERENCE_PATTERN = re.compile(
    r"^(ingredient|procedure|equipment|container)\.([a-z0-9_]+)(?:@([^@\s]+))?$"
)

type Domain = Literal["ingredient", "procedure", "equipment", "container"]
type AdjustmentType = Literal["add", "remove", "scale"]


def _as_mapping(value: object, *, error_message: str) -> dict[str, object]:
    if isinstance(value, dict):
        return cast("dict[str, object]", value)
    raise TypeError(error_message)


def _as_sequence(value: object, *, error_message: str) -> Sequence[object]:
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return cast("Sequence[object]", value)
    raise TypeError(error_message)


def _as_optional_string(value: object, *, error_message: str) -> str | None:
    if value is None or isinstance(value, str):
        return value
    raise TypeError(error_message)


def _as_string(value: object, *, error_message: str) -> str:
    if isinstance(value, str):
        return value
    raise TypeError(error_message)


def _as_adjustment_type(value: object) -> AdjustmentType:
    if value == "add":
        return "add"
    if value == "remove":
        return "remove"
    if value == "scale":
        return "scale"
    raise TypeError("adjustment.type must be one of add/remove/scale")


def _as_adjustment_value(value: object) -> float | int | None:
    if value is None or isinstance(value, int | float):
        return value
    raise TypeError("adjustment.value must be a number when provided")


def _domain_from_text(value: str) -> Domain:
    if value == "ingredient":
        return "ingredient"
    if value == "procedure":
        return "procedure"
    if value == "equipment":
        return "equipment"
    if value == "container":
        return "container"
    raise ValueError(f"invalid entity domain: {value}")


def parse_entity_reference(value: object) -> EntityReference:
    """Parse a single entity reference from dotted text or mapping form."""

    if isinstance(value, str):
        match = _REFERENCE_PATTERN.fullmatch(value)
        if match is None:
            raise ValueError(f"invalid entity reference: {value}")

        version_text = match.group(3)
        version: str | int | None
        if version_text is None:
            version = None
        elif version_text.isdigit():
            version = int(version_text)
        else:
            version = version_text

        return EntityReference(
            domain=_domain_from_text(match.group(1)),
            identifier=match.group(2),
            version=version,
        )

    if isinstance(value, dict):
        return EntityReference.model_validate(value)

    raise TypeError("entity reference must be a dotted string or mapping")


def _parse_adjustment(payload: dict[str, object]) -> Adjustment:
    target = parse_entity_reference(payload["target"])
    value = _as_adjustment_value(payload.get("value"))
    return Adjustment(type=_as_adjustment_type(payload["type"]), target=target, value=value)


def _parse_composition(payload: dict[str, object]) -> Composition:
    raw_ingredients = _as_sequence(
        payload.get("ingredients", ()),
        error_message="composition.ingredients must be a list",
    )
    raw_adjustments = _as_sequence(
        payload.get("adjustments", ()),
        error_message="composition.adjustments must be a list",
    )

    ingredients = tuple(parse_entity_reference(item) for item in raw_ingredients)
    adjustments = tuple(
        _parse_adjustment(
            _as_mapping(item, error_message="composition.adjustments items must be mappings")
        )
        for item in raw_adjustments
    )
    return Composition(ingredients=ingredients, adjustments=adjustments)


def _parse_substitution(payload: dict[str, object]) -> Substitution:
    from_reference = parse_entity_reference(payload["from"])
    to_payload = payload["to"]

    to_value: EntityReference | Composition
    if isinstance(to_payload, dict) and "ingredients" in to_payload:
        to_value = _parse_composition(cast("dict[str, object]", to_payload))
    elif isinstance(to_payload, dict):
        to_value = parse_entity_reference(cast("dict[str, object]", to_payload))
    else:
        to_value = parse_entity_reference(to_payload)

    return Substitution.model_validate({"from": from_reference, "to": to_value})


def _parse_override_set(payload: dict[str, object]) -> OverrideSet:
    raw_substitutions = _as_sequence(
        payload.get("substitutions", ()),
        error_message="override.substitutions must be a list",
    )
    substitutions = tuple(
        _parse_substitution(
            _as_mapping(item, error_message="override.substitutions items must be mappings")
        )
        for item in raw_substitutions
    )
    return OverrideSet(substitutions=substitutions)


def _parse_reference_binding(payload: dict[str, object]) -> ReferenceBinding:
    target = parse_entity_reference(payload["target"])
    raw_override = payload.get("override")

    override: OverrideSet | None
    if raw_override is None:
        override = None
    else:
        override = _parse_override_set(
            _as_mapping(raw_override, error_message="binding.override must be a mapping")
        )

    return ReferenceBinding(target=target, override=override)


def _parse_step_context(payload: dict[str, object]) -> StepContext:
    return StepContext.model_validate(payload)


def _parse_step(payload: dict[str, object]) -> Step:
    raw_inputs = _as_sequence(payload.get("inputs", ()), error_message="step.inputs must be a list")
    raw_outputs = _as_sequence(
        payload.get("outputs", ()),
        error_message="step.outputs must be a list",
    )

    raw_context = payload.get("context")
    context: StepContext | None
    if raw_context is None:
        context = None
    else:
        context = _parse_step_context(
            _as_mapping(raw_context, error_message="step.context must be a mapping")
        )

    return Step(
        id=_as_optional_string(payload.get("id"), error_message="step.id must be a string"),
        action=parse_entity_reference(payload["action"]),
        inputs=tuple(
            _parse_reference_binding(
                _as_mapping(item, error_message="step.inputs items must be mappings")
            )
            for item in raw_inputs
        ),
        outputs=tuple(parse_entity_reference(item) for item in raw_outputs),
        context=context,
    )


def parse_procedure(payload: dict[str, object]) -> Procedure:
    """Parse a Procedure model from a loaded YAML mapping payload."""

    raw_steps = payload.get("steps")
    if raw_steps is None:
        raise ValueError("procedure.steps is required")

    steps_seq = _as_sequence(raw_steps, error_message="procedure.steps must be a list")
    raw_inputs = _as_sequence(
        payload.get("inputs", ()), error_message="procedure.inputs must be a list"
    )
    raw_outputs = _as_sequence(
        payload.get("outputs", ()),
        error_message="procedure.outputs must be a list",
    )
    raw_tags = _as_sequence(payload.get("tags", ()), error_message="procedure.tags must be a list")

    steps = tuple(
        _parse_step(_as_mapping(item, error_message="procedure.steps items must be mappings"))
        for item in steps_seq
    )
    inputs = tuple(parse_entity_reference(item) for item in raw_inputs)
    outputs = tuple(parse_entity_reference(item) for item in raw_outputs)

    procedure_id = payload.get("id")
    if not isinstance(procedure_id, str):
        raise TypeError("procedure.id must be a string")

    name = _as_optional_string(payload.get("name"), error_message="procedure.name must be a string")
    description = _as_optional_string(
        payload.get("description"),
        error_message="procedure.description must be a string",
    )
    tags = tuple(
        _as_string(tag, error_message="procedure.tags items must be strings") for tag in raw_tags
    )

    return Procedure(
        id=procedure_id,
        name=name,
        description=description,
        steps=steps,
        inputs=inputs,
        outputs=outputs,
        tags=tags,
    )


def parse_procedure_yaml_text(text: str) -> Procedure:
    """Parse a Procedure model directly from YAML text."""

    return parse_procedure(load_yaml_text(text))


def parse_procedure_yaml_file(path: str | Path) -> Procedure:
    """Parse a Procedure model directly from a YAML file path."""

    return parse_procedure(load_yaml_file(path))
