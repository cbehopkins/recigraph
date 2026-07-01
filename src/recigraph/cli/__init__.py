"""Command line interface for ReciGraph."""

from collections.abc import Sequence
from pathlib import Path
from typing import cast

import click

from recigraph.build import build_site
from recigraph.build.discovery import discover_recipe_sources
from recigraph.compiler import compile_procedure
from recigraph.loader import (
    load_yaml_file,
    parse_entity_reference,
    parse_procedure,
    parse_procedure_yaml_file,
)
from recigraph.model import EntityReference, Procedure, Step
from recigraph.registry import (
    ContainerRegistry,
    EquipmentRegistry,
    IngredientRegistry,
    ProcedureRegistry,
)
from recigraph.rendering.text import render_procedure_text
from recigraph.resolver import ReferenceResolutionError, RegistrySet


def _ensure_mapping(value: object, *, field_name: str) -> dict[str, object]:
    if isinstance(value, dict):
        return cast("dict[str, object]", value)
    raise click.ClickException(f"{field_name} must be a mapping")


def _ensure_sequence(value: object, *, field_name: str) -> Sequence[object]:
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return cast("Sequence[object]", value)
    raise click.ClickException(f"{field_name} must be a list")


def _normalize_procedure_id(value: str) -> str:
    if value.startswith("procedure."):
        return value
    return f"procedure.{value}"


def _load_ingredients(path: Path) -> dict[str, str]:
    payload = load_yaml_file(path)
    ingredients_raw = _ensure_sequence(payload.get("ingredients", ()), field_name="ingredients")

    ingredients: dict[str, str] = {}
    for index, item in enumerate(ingredients_raw):
        ingredient = _ensure_mapping(item, field_name=f"ingredients[{index}]")
        ingredient_id = ingredient.get("id")
        ingredient_name = ingredient.get("name")
        if not isinstance(ingredient_id, str) or not ingredient_id:
            raise click.ClickException(f"ingredients[{index}].id must be a non-empty string")
        if not isinstance(ingredient_name, str) or not ingredient_name:
            raise click.ClickException(f"ingredients[{index}].name must be a non-empty string")
        ingredients[ingredient_id] = ingredient_name
    return ingredients


def _load_procedures(path: Path) -> list[dict[str, object]]:
    payload = load_yaml_file(path)
    procedures_raw = _ensure_sequence(payload.get("procedures", ()), field_name="procedures")
    procedures: list[dict[str, object]] = []
    for index, item in enumerate(procedures_raw):
        procedure = _ensure_mapping(item, field_name=f"procedures[{index}]")
        procedures.append(procedure)
    return procedures


def _load_equipment(path: Path) -> dict[str, str]:
    payload = load_yaml_file(path)
    equipment_raw = _ensure_sequence(payload.get("equipment", ()), field_name="equipment")

    equipment: dict[str, str] = {}
    for index, item in enumerate(equipment_raw):
        equipment_item = _ensure_mapping(item, field_name=f"equipment[{index}]")
        equipment_id = equipment_item.get("id")
        equipment_name = equipment_item.get("name")
        if not isinstance(equipment_id, str) or not equipment_id:
            raise click.ClickException(f"equipment[{index}].id must be a non-empty string")
        if not isinstance(equipment_name, str) or not equipment_name:
            raise click.ClickException(f"equipment[{index}].name must be a non-empty string")
        equipment[equipment_id] = equipment_name
    return equipment


def _infer_entrypoint_procedure_payload(procedures: list[dict[str, object]]) -> dict[str, object]:
    payload_by_id: dict[str, dict[str, object]] = {}
    incoming_edge_count: dict[str, int] = {}

    for index, procedure in enumerate(procedures):
        raw_id = procedure.get("id")
        if not isinstance(raw_id, str) or not raw_id:
            raise click.ClickException(f"procedures[{index}].id must be a non-empty string")

        normalized_id = _normalize_procedure_id(raw_id)
        if normalized_id in payload_by_id:
            raise click.ClickException(
                f"Duplicate procedure id '{raw_id}' found in procedures.yaml"
            )

        payload_by_id[normalized_id] = procedure
        incoming_edge_count[normalized_id] = 0

    for index, procedure in enumerate(procedures):
        steps_raw = _ensure_sequence(
            procedure.get("steps", ()),
            field_name=f"procedures[{index}].steps",
        )
        for step_index, step_obj in enumerate(steps_raw):
            step = _ensure_mapping(step_obj, field_name=f"procedures[{index}].steps[{step_index}]")
            action_raw = step.get("action")
            action_reference = parse_entity_reference(action_raw)
            if action_reference.domain != "procedure":
                raise click.ClickException(
                    f"procedures[{index}].steps[{step_index}].action must be a procedure reference"
                )

            referenced_id = _normalize_procedure_id(action_reference.identifier)
            if referenced_id in incoming_edge_count:
                incoming_edge_count[referenced_id] += 1

    entrypoint_ids = sorted(
        procedure_id
        for procedure_id, incoming_count in incoming_edge_count.items()
        if incoming_count == 0
    )
    if len(entrypoint_ids) == 1:
        return payload_by_id[entrypoint_ids[0]]
    if not entrypoint_ids:
        raise click.ClickException(
            "Could not infer a procedure entrypoint. Use --procedure-id to select one."
        )

    entrypoint_labels = ", ".join(
        procedure_id.removeprefix("procedure.") for procedure_id in entrypoint_ids
    )
    raise click.ClickException(
        f"Multiple entrypoint procedures found: {entrypoint_labels}. "
        "Use --procedure-id to select one."
    )


def _select_procedure_payload(
    procedures: list[dict[str, object]],
    *,
    procedure_id: str | None,
) -> dict[str, object]:
    if not procedures:
        raise click.ClickException("procedures must include at least one procedure")

    if procedure_id is None:
        if len(procedures) == 1:
            return procedures[0]
        return _infer_entrypoint_procedure_payload(procedures)

    target_id = _normalize_procedure_id(procedure_id)
    for procedure in procedures:
        raw_id = procedure.get("id")
        if isinstance(raw_id, str) and _normalize_procedure_id(raw_id) == target_id:
            return procedure

    raise click.ClickException(f"Procedure '{procedure_id}' was not found in procedures.yaml")


def _build_procedure_registry_ids(procedures: list[dict[str, object]]) -> set[str]:
    procedure_ids: set[str] = set()

    for index, procedure in enumerate(procedures):
        raw_id = procedure.get("id")
        if not isinstance(raw_id, str) or not raw_id:
            raise click.ClickException(f"procedures[{index}].id must be a non-empty string")
        procedure_ids.add(_normalize_procedure_id(raw_id).removeprefix("procedure."))

        steps_raw = _ensure_sequence(
            procedure.get("steps", ()),
            field_name=f"procedures[{index}].steps",
        )
        for step_index, step_obj in enumerate(steps_raw):
            step = _ensure_mapping(step_obj, field_name=f"procedures[{index}].steps[{step_index}]")
            action_raw = step.get("action")
            action_reference = parse_entity_reference(action_raw)
            if action_reference.domain != "procedure":
                raise click.ClickException(
                    f"procedures[{index}].steps[{step_index}].action must be a procedure reference"
                )
            procedure_ids.add(action_reference.identifier)

    return procedure_ids


def _build_registry_set(
    ingredient_ids: Sequence[str],
    procedure_ids: Sequence[str],
    *,
    equipment_ids: Sequence[str] = (),
    container_ids: Sequence[str] = (),
) -> RegistrySet:
    ingredient_registry = IngredientRegistry()
    for ingredient_id in ingredient_ids:
        ingredient_registry.add(ingredient_id, f"ingredient:{ingredient_id}")

    procedure_registry = ProcedureRegistry()
    for procedure_id in procedure_ids:
        procedure_registry.add(procedure_id, f"procedure:{procedure_id}")

    equipment_registry = EquipmentRegistry()
    for equipment_id in equipment_ids:
        equipment_registry.add(equipment_id, f"equipment:{equipment_id}")

    container_registry = ContainerRegistry()
    for container_id in container_ids:
        container_registry.add(container_id, f"container:{container_id}")

    return RegistrySet(
        ingredient=ingredient_registry,
        procedure=procedure_registry,
        equipment=equipment_registry,
        container=container_registry,
    )


def _parse_procedure_map(procedures: list[dict[str, object]]) -> dict[str, Procedure]:
    procedure_map: dict[str, Procedure] = {}
    for index, payload in enumerate(procedures):
        normalized = dict(payload)
        raw_id = normalized.get("id")
        if not isinstance(raw_id, str) or not raw_id:
            raise click.ClickException(f"procedures[{index}].id must be a non-empty string")
        normalized_id = _normalize_procedure_id(raw_id)
        normalized["id"] = normalized_id
        procedure_map[normalized_id] = parse_procedure(normalized)
    return procedure_map


def _dedupe_references(references: list[EntityReference]) -> tuple[EntityReference, ...]:
    seen: set[str] = set()
    deduped: list[EntityReference] = []
    for reference in references:
        if reference.reference_text in seen:
            continue
        seen.add(reference.reference_text)
        deduped.append(reference)
    return tuple(deduped)


def _expand_shared_procedures(
    procedure: Procedure,
    *,
    procedure_map: dict[str, Procedure],
    visiting: tuple[str, ...] = (),
) -> Procedure:
    if procedure.id in visiting:
        chain = " -> ".join((*visiting, procedure.id))
        raise click.ClickException(f"Circular shared-procedure reference detected: {chain}")

    expanded_inputs: list[EntityReference] = list(procedure.inputs)
    expanded_outputs: list[EntityReference] = list(procedure.outputs)
    expanded_steps: list[Step] = []
    next_visiting = (*visiting, procedure.id)

    for step in procedure.steps:
        referenced_id = _normalize_procedure_id(step.action.identifier)
        referenced_procedure = procedure_map.get(referenced_id)

        if (
            referenced_procedure is not None
            and not step.inputs
            and not step.outputs
            and step.context is None
            and referenced_id != procedure.id
        ):
            resolved = _expand_shared_procedures(
                referenced_procedure,
                procedure_map=procedure_map,
                visiting=next_visiting,
            )
            expanded_inputs.extend(resolved.inputs)
            expanded_outputs.extend(resolved.outputs)
            expanded_steps.extend(resolved.steps)
            continue

        expanded_steps.append(step)

    return procedure.model_copy(
        update={
            "inputs": _dedupe_references(expanded_inputs),
            "outputs": _dedupe_references(expanded_outputs),
            "steps": tuple(expanded_steps),
        }
    )


def _load_compilation_inputs(
    example_dir: Path,
    *,
    procedure_id: str | None,
    ingredients_file: str,
    procedures_file: str,
    equipment_file: str,
) -> tuple[Procedure, dict[str, str], dict[str, str], str, RegistrySet]:
    ingredients_path = example_dir / ingredients_file
    procedures_path = example_dir / procedures_file
    fallback_procedure_path = example_dir / "procedure.yaml"
    equipment_path = example_dir / equipment_file

    if not ingredients_path.exists():
        raise click.ClickException(f"Ingredients file not found: {ingredients_path}")
    if (
        not procedures_path.exists()
        and procedures_file == "procedures.yaml"
        and fallback_procedure_path.exists()
    ):
        procedures_path = fallback_procedure_path
    if not procedures_path.exists():
        raise click.ClickException(f"Procedures file not found: {procedures_path}")

    ingredients = _load_ingredients(ingredients_path)
    procedures = _load_procedures(procedures_path)
    equipment = _load_equipment(equipment_path) if equipment_path.exists() else {}
    selected_payload = _select_procedure_payload(procedures, procedure_id=procedure_id)
    selected_payload = dict(selected_payload)

    selected_id = selected_payload.get("id")
    if not isinstance(selected_id, str) or not selected_id:
        raise click.ClickException("Selected procedure id must be a non-empty string")
    normalized_id = _normalize_procedure_id(selected_id)
    selected_payload["id"] = normalized_id

    procedure_map = _parse_procedure_map(procedures)
    selected_procedure = procedure_map.get(normalized_id)
    if selected_procedure is None:
        raise click.ClickException(f"Procedure '{normalized_id}' was not found in procedures data")
    procedure = _expand_shared_procedures(selected_procedure, procedure_map=procedure_map)
    registries = _build_registry_set(
        ingredient_ids=tuple(ingredients.keys()),
        procedure_ids=tuple(sorted(_build_procedure_registry_ids(procedures))),
        equipment_ids=tuple(equipment.keys()),
    )
    return procedure, ingredients, equipment, normalized_id, registries


def _collect_references_for_registry(procedure: Procedure) -> tuple[EntityReference, ...]:
    references: list[EntityReference] = [*procedure.inputs, *procedure.outputs]
    for step in procedure.steps:
        references.append(step.action)
        references.extend(step.outputs)
        for binding in step.inputs:
            references.append(binding.target)
            if binding.override is None:
                continue
            for substitution in binding.override.substitutions:
                references.append(substitution.from_)
                if isinstance(substitution.to, EntityReference):
                    references.append(substitution.to)
                    continue
                references.extend(substitution.to.ingredients)
                references.extend(adjustment.target for adjustment in substitution.to.adjustments)
    return tuple(references)


def _build_registry_set_for_source_dir(source_dir: Path) -> RegistrySet:
    source_files = discover_recipe_sources(source_dir)
    ingredient_ids: set[str] = set()
    procedure_ids: set[str] = set()
    equipment_ids: set[str] = set()
    container_ids: set[str] = set()

    for source_file in source_files:
        procedure = parse_procedure_yaml_file(source_file)
        procedure_ids.add(procedure.id.removeprefix("procedure."))
        for reference in _collect_references_for_registry(procedure):
            if reference.domain == "ingredient":
                ingredient_ids.add(reference.identifier)
            elif reference.domain == "procedure":
                procedure_ids.add(reference.identifier)
            elif reference.domain == "equipment":
                equipment_ids.add(reference.identifier)
            elif reference.domain == "container":
                container_ids.add(reference.identifier)

    ingredient_registry = IngredientRegistry()
    for ingredient_id in sorted(ingredient_ids):
        ingredient_registry.add(ingredient_id, f"ingredient:{ingredient_id}")

    procedure_registry = ProcedureRegistry()
    for procedure_id in sorted(procedure_ids):
        procedure_registry.add(procedure_id, f"procedure:{procedure_id}")

    equipment_registry = EquipmentRegistry()
    for equipment_id in sorted(equipment_ids):
        equipment_registry.add(equipment_id, f"equipment:{equipment_id}")

    container_registry = ContainerRegistry()
    for container_id in sorted(container_ids):
        container_registry.add(container_id, f"container:{container_id}")

    return RegistrySet(
        ingredient=ingredient_registry,
        procedure=procedure_registry,
        equipment=equipment_registry,
        container=container_registry,
    )


@click.group()
def main() -> None:
    """Run the ReciGraph command-line interface."""


@main.command("render")
@click.argument("example_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--procedure-id", type=str, help="Procedure id to render when multiple exist.")
@click.option(
    "--ingredients-file",
    type=str,
    default="ingredients.yaml",
    show_default=True,
    help="Ingredient file relative to EXAMPLE_DIR.",
)
@click.option(
    "--procedures-file",
    type=str,
    default="procedures.yaml",
    show_default=True,
    help="Procedure file relative to EXAMPLE_DIR.",
)
@click.option(
    "--equipment-file",
    type=str,
    default="equipment.yaml",
    show_default=True,
    help="Optional equipment file relative to EXAMPLE_DIR.",
)
@click.option(
    "--output-file",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    default=None,
    help="Optional file path to save rendered text.",
)
def render_command(
    example_dir: Path,
    procedure_id: str | None,
    ingredients_file: str,
    procedures_file: str,
    equipment_file: str,
    output_file: Path | None,
) -> None:
    """Compile and render a two-file recipe example as plain text."""

    try:
        procedure, ingredients, equipment, _, registries = _load_compilation_inputs(
            example_dir,
            procedure_id=procedure_id,
            ingredients_file=ingredients_file,
            procedures_file=procedures_file,
            equipment_file=equipment_file,
        )

        compile_procedure(procedure, registries=registries)
        rendered_text = render_procedure_text(
            procedure,
            ingredient_names=ingredients,
            equipment_names=equipment,
        )
    except ReferenceResolutionError as error:
        raise click.ClickException(str(error)) from error
    except (TypeError, ValueError) as error:
        raise click.ClickException(str(error)) from error

    click.echo(rendered_text, nl=False)

    if output_file is not None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(rendered_text, encoding="utf-8")


@main.command("compile")
@click.argument("example_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--procedure-id", type=str, help="Procedure id to compile when multiple exist.")
@click.option(
    "--ingredients-file",
    type=str,
    default="ingredients.yaml",
    show_default=True,
    help="Ingredient file relative to EXAMPLE_DIR.",
)
@click.option(
    "--procedures-file",
    type=str,
    default="procedures.yaml",
    show_default=True,
    help="Procedure file relative to EXAMPLE_DIR.",
)
@click.option(
    "--equipment-file",
    type=str,
    default="equipment.yaml",
    show_default=True,
    help="Optional equipment file relative to EXAMPLE_DIR.",
)
@click.option(
    "--output-file",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    default=None,
    help="Optional file path to save compiled graph JSON.",
)
def compile_command(
    example_dir: Path,
    procedure_id: str | None,
    ingredients_file: str,
    procedures_file: str,
    equipment_file: str,
    output_file: Path | None,
) -> None:
    """Compile a two-file recipe example and emit graph metadata."""

    try:
        procedure, _, _, normalized_procedure_id, registries = _load_compilation_inputs(
            example_dir,
            procedure_id=procedure_id,
            ingredients_file=ingredients_file,
            procedures_file=procedures_file,
            equipment_file=equipment_file,
        )
        output = compile_procedure(procedure, registries=registries)
    except ReferenceResolutionError as error:
        raise click.ClickException(str(error)) from error
    except (TypeError, ValueError) as error:
        raise click.ClickException(str(error)) from error

    click.echo(f"Procedure: {normalized_procedure_id}")
    click.echo(f"Final graph snapshot: {output.final_graph.snapshot_id}")
    click.echo(f"Trace length: {len(output.trace)}")

    if output_file is not None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(output.model_dump_json(indent=2), encoding="utf-8")


@main.command("build")
@click.argument("source_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("output_dir", type=click.Path(file_okay=False, path_type=Path))
def build_command(source_dir: Path, output_dir: Path) -> None:
    """Build static HTML output for a directory of procedure YAML files."""

    try:
        registries = _build_registry_set_for_source_dir(source_dir)
        result = build_site(source_dir, output_dir, registries=registries)
    except ReferenceResolutionError as error:
        raise click.ClickException(str(error)) from error
    except (FileNotFoundError, NotADirectoryError, ValueError) as error:
        raise click.ClickException(str(error)) from error

    click.echo(f"Built {result.output_dir}")
    click.echo(f"Compiled recipes: {len(result.compiled_recipes)}")
    click.echo(f"Artifacts: {len(result.render_result.artifacts)}")
