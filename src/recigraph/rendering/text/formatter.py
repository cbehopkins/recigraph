"""Deterministic plain-text formatter for compiled procedures."""

from collections.abc import Mapping

from recigraph.model import Procedure


def render_procedure_text(
    procedure: Procedure,
    *,
    ingredient_names: Mapping[str, str],
) -> str:
    """Render a Procedure to deterministic plain-text output."""

    title = procedure.name or procedure.id.removeprefix("procedure.").replace("_", " ").title()

    ingredient_lines = [
        f"• {ingredient_names.get(reference.identifier, reference.identifier)}"
        for reference in procedure.inputs
        if reference.domain == "ingredient"
    ]

    method_lines: list[str] = []
    for index, step in enumerate(procedure.steps, start=1):
        verb = step.action.identifier.replace("_", " ").strip().capitalize()
        step_ingredients = [
            ingredient_names.get(binding.target.identifier, binding.target.identifier).lower()
            for binding in step.inputs
            if binding.target.domain == "ingredient"
        ]
        if step_ingredients:
            method_lines.append(f"{index}. {verb} {_join_human_list(step_ingredients)}.")
            continue
        method_lines.append(f"{index}. {verb}.")

    return "\n".join([
        title,
        "",
        "Ingredients",
        "",
        *ingredient_lines,
        "",
        "Method",
        "",
        *method_lines,
        "",
    ])


def _join_human_list(values: list[str]) -> str:
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return f"{', '.join(values[:-1])}, and {values[-1]}"
