"""Reference resolver for converting EntityReference values into registry entities."""

from dataclasses import dataclass

from recigraph.model import Composition, EntityReference, Procedure
from recigraph.registry import (
    ContainerRegistry,
    EntityRegistry,
    EquipmentRegistry,
    IngredientRegistry,
    ProcedureRegistry,
)


@dataclass(frozen=True, slots=True)
class RegistrySet:
    """Domain-scoped registries used during resolution."""

    ingredient: EntityRegistry[str]
    procedure: EntityRegistry[str]
    equipment: EntityRegistry[str]
    container: EntityRegistry[str]


@dataclass(frozen=True, slots=True)
class ResolvedReference:
    """Resolved reference with source path and registry entity."""

    path: str
    reference: EntityReference
    entity: str
    version: str | int | None


@dataclass(frozen=True, slots=True)
class ResolutionIssue:
    """Single resolution error describing a missing or invalid reference."""

    code: str
    path: str
    reference_text: str
    message: str


@dataclass(frozen=True, slots=True)
class ResolvedProcedureReferences:
    """Intermediate structure containing resolved references for a procedure."""

    procedure: Procedure
    references: tuple[ResolvedReference, ...]


class ReferenceResolutionError(ValueError):
    """Raised when one or more references cannot be resolved."""

    def __init__(self, issues: tuple[ResolutionIssue, ...]) -> None:
        self.issues = issues
        issue_lines = [
            f"- {issue.path}: {issue.code} - {issue.reference_text} ({issue.message})"
            for issue in issues
        ]
        super().__init__("Reference resolution failed:\n" + "\n".join(issue_lines))


_ALLOWED_DOMAINS = frozenset({"ingredient", "procedure", "equipment", "container"})


def default_registry_set() -> RegistrySet:
    """Create an empty in-memory registry set for v1 resolution."""

    return RegistrySet(
        ingredient=IngredientRegistry(),
        procedure=ProcedureRegistry(),
        equipment=EquipmentRegistry(),
        container=ContainerRegistry(),
    )


def _registry_for_domain(domain: str, registries: RegistrySet) -> EntityRegistry[str] | None:
    if domain == "ingredient":
        return registries.ingredient
    if domain == "procedure":
        return registries.procedure
    if domain == "equipment":
        return registries.equipment
    if domain == "container":
        return registries.container
    return None


def resolve_reference(
    reference: EntityReference,
    *,
    path: str,
    registries: RegistrySet,
) -> ResolvedReference:
    """Resolve a single EntityReference using the domain-specific registry."""

    registry = _registry_for_domain(reference.domain, registries)
    if registry is None:
        raise ReferenceResolutionError((
            ResolutionIssue(
                code="UNKNOWN_DOMAIN",
                path=path,
                reference_text=reference.reference_text,
                message=f"domain '{reference.domain}' is not one of {sorted(_ALLOWED_DOMAINS)}",
            ),
        ))

    entity = registry.get(reference.identifier)
    if entity is None:
        raise ReferenceResolutionError((
            ResolutionIssue(
                code="MISSING_REFERENCE",
                path=path,
                reference_text=reference.reference_text,
                message="identifier is not present in registry",
            ),
        ))

    return ResolvedReference(
        path=path,
        reference=reference,
        entity=entity,
        version=reference.version,
    )


def resolve_procedure_references(
    procedure: Procedure,
    *,
    registries: RegistrySet,
) -> ResolvedProcedureReferences:
    """Resolve all references in a Procedure into an intermediate structure."""

    issues: list[ResolutionIssue] = []
    resolved: list[ResolvedReference] = []

    def _resolve(reference: EntityReference, *, path: str) -> None:
        try:
            resolved_reference = resolve_reference(reference, path=path, registries=registries)
        except ReferenceResolutionError as error:
            issues.extend(error.issues)
            return
        resolved.append(resolved_reference)

    for input_index, reference in enumerate(procedure.inputs):
        _resolve(reference, path=f"procedure.inputs[{input_index}]")

    for output_index, reference in enumerate(procedure.outputs):
        _resolve(reference, path=f"procedure.outputs[{output_index}]")

    for step_index, step in enumerate(procedure.steps):
        step_path = f"procedure.steps[{step_index}]"
        _resolve(step.action, path=f"{step_path}.action")

        for binding_index, binding in enumerate(step.inputs):
            binding_path = f"{step_path}.inputs[{binding_index}]"
            _resolve(binding.target, path=f"{binding_path}.target")

            if binding.override is None:
                continue

            for substitution_index, substitution in enumerate(binding.override.substitutions):
                substitution_path = f"{binding_path}.override.substitutions[{substitution_index}]"
                _resolve(substitution.from_, path=f"{substitution_path}.from")

                if isinstance(substitution.to, EntityReference):
                    _resolve(substitution.to, path=f"{substitution_path}.to")
                    continue

                to_composition: Composition = substitution.to
                for ingredient_index, ingredient in enumerate(to_composition.ingredients):
                    _resolve(
                        ingredient,
                        path=f"{substitution_path}.to.ingredients[{ingredient_index}]",
                    )

                for adjustment_index, adjustment in enumerate(to_composition.adjustments):
                    _resolve(
                        adjustment.target,
                        path=f"{substitution_path}.to.adjustments[{adjustment_index}].target",
                    )

        for output_index, output in enumerate(step.outputs):
            _resolve(output, path=f"{step_path}.outputs[{output_index}]")

    if issues:
        raise ReferenceResolutionError(tuple(issues))

    return ResolvedProcedureReferences(procedure=procedure, references=tuple(resolved))
