"""Deterministic plain-text formatter for compiled procedures."""

from collections.abc import Mapping

from recigraph.model import Composition, EntityReference, Procedure, ReferenceBinding


def render_procedure_text(
    procedure: Procedure,
    *,
    ingredient_names: Mapping[str, str],
    equipment_names: Mapping[str, str] | None = None,
) -> str:
    """Render a Procedure to deterministic plain-text output."""

    title = procedure.name or procedure.id.removeprefix("procedure.").replace("_", " ").title()
    rendered_ingredients = _rendered_ingredients_from_procedure(procedure)

    ingredient_lines = [
        f"• {ingredient_names.get(reference.identifier, reference.identifier)}"
        for reference in rendered_ingredients
    ]
    equipment_lines = [f"• {name}" for name in (equipment_names or {}).values()]

    method_lines: list[str] = []
    for index, step in enumerate(procedure.steps, start=1):
        action_name = step.action.identifier.replace("_", " ").strip().lower()
        verb = action_name.capitalize()
        step_references = [
            reference
            for binding in step.inputs
            for reference in _binding_rewrite_targets(binding)
            if reference.domain == "ingredient"
        ]
        step_ingredients = [
            ingredient_names.get(reference.identifier, reference.identifier).lower()
            for reference in _dedupe_references(step_references)
        ]
        step_has_substitution = any(
            binding.override is not None and binding.override.substitutions
            for binding in step.inputs
        )
        if action_name == "mix" and step_has_substitution:
            method_lines.append(f"{index}. Mix the ingredients.")
            continue
        if action_name == "boil" and step_ingredients:
            method_lines.append(f"{index}. Boil the {step_ingredients[0]}.")
            continue
        if action_name == "infuse" and step_ingredients:
            tea_target = _choose_infusion_target(step_ingredients)
            method_lines.append(f"{index}. Infuse the {tea_target}.")
            continue
        if step_ingredients:
            method_lines.append(f"{index}. {verb} {_join_human_list(step_ingredients)}.")
            continue
        method_lines.append(f"{index}. {verb}.")

    output_lines = [
        title,
        "",
        "Ingredients",
        "",
        *ingredient_lines,
    ]
    if equipment_lines:
        output_lines.extend([
            "",
            "Equipment",
            "",
            *equipment_lines,
        ])
    output_lines.extend([
        "",
        "Method",
        "",
        *method_lines,
        "",
    ])
    return "\n".join(output_lines)


def _join_human_list(values: list[str]) -> str:
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return f"{', '.join(values[:-1])}, and {values[-1]}"


def _choose_infusion_target(values: list[str]) -> str:
    for value in values:
        if "tea" in value:
            return "tea"
    return values[0]


def _binding_rewrite_targets(binding: ReferenceBinding) -> tuple[EntityReference, ...]:
    if binding.override is None or not binding.override.substitutions:
        return (binding.target,)

    current_targets: tuple[EntityReference, ...] = (binding.target,)
    for substitution in binding.override.substitutions:
        updated: list[EntityReference] = []
        for target in current_targets:
            if target != substitution.from_:
                updated.append(target)
                continue

            if isinstance(substitution.to, EntityReference):
                updated.append(substitution.to)
            else:
                composition: Composition = substitution.to
                updated.extend(composition.ingredients)
        current_targets = tuple(updated)
    return current_targets


def _rendered_ingredients_from_procedure(procedure: Procedure) -> tuple[EntityReference, ...]:
    rendered = [reference for reference in procedure.inputs if reference.domain == "ingredient"]
    for step in procedure.steps:
        rewritten: list[EntityReference] = []
        for reference in rendered:
            replacement: tuple[EntityReference, ...] | None = None
            for binding in step.inputs:
                if binding.target == reference:
                    replacement = tuple(
                        target
                        for target in _binding_rewrite_targets(binding)
                        if target.domain == "ingredient"
                    )
                    break
            if replacement is None:
                rewritten.append(reference)
            else:
                rewritten.extend(replacement)
        rendered = rewritten
    return tuple(
        reference
        for _, reference in {reference.reference_text: reference for reference in rendered}.items()
    )


def _dedupe_references(values: list[EntityReference]) -> list[EntityReference]:
    seen: set[str] = set()
    deduped: list[EntityReference] = []
    for value in values:
        if value.reference_text in seen:
            continue
        seen.add(value.reference_text)
        deduped.append(value)
    return deduped
