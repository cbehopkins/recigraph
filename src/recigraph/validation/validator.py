"""Structural AST validation for ReciGraph procedures."""

import re
from dataclasses import dataclass

from recigraph.model import Procedure

_STEP_ID_PATTERN = re.compile(r"^[a-z0-9_]+$")
_ALLOWED_DOMAINS = frozenset({"ingredient", "procedure", "equipment", "container"})


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Single structural validation diagnostic."""

    code: str
    path: str
    message: str


class ProcedureValidationError(ValueError):
    """Raised when a procedure fails structural validation."""

    def __init__(self, issues: tuple[ValidationIssue, ...]) -> None:
        self.issues = issues
        issue_lines = [f"- {issue.path}: {issue.code} - {issue.message}" for issue in issues]
        super().__init__("Procedure validation failed:\n" + "\n".join(issue_lines))


def _validate_reference_domain(*, domain: str, path: str) -> ValidationIssue | None:
    if domain in _ALLOWED_DOMAINS:
        return None
    return ValidationIssue(
        code="INVALID_DOMAIN",
        path=path,
        message=f"domain '{domain}' is not one of {sorted(_ALLOWED_DOMAINS)}",
    )


def validate_procedure_structure(procedure: Procedure) -> tuple[ValidationIssue, ...]:
    """Validate structural Procedure AST rules for Phase 4."""

    issues: list[ValidationIssue] = []

    if not procedure.steps:
        issues.append(
            ValidationIssue(
                code="REQUIRED_STEPS",
                path="procedure.steps",
                message="procedure must include at least one step",
            )
        )

    if not procedure.id.startswith("procedure."):
        issues.append(
            ValidationIssue(
                code="PROCEDURE_ID_FORMAT",
                path="procedure.id",
                message="procedure.id must begin with 'procedure.'",
            )
        )

    seen_step_ids: set[str] = set()

    for step_index, step in enumerate(procedure.steps):
        step_path = f"procedure.steps[{step_index}]"

        if step.action.domain != "procedure":
            issues.append(
                ValidationIssue(
                    code="STEP_ACTION_DOMAIN",
                    path=f"{step_path}.action.domain",
                    message="step action must reference the procedure domain",
                )
            )

        if domain_issue := _validate_reference_domain(
            domain=step.action.domain,
            path=f"{step_path}.action.domain",
        ):
            issues.append(domain_issue)

        if step.id is not None:
            if not _STEP_ID_PATTERN.fullmatch(step.id):
                issues.append(
                    ValidationIssue(
                        code="STEP_ID_FORMAT",
                        path=f"{step_path}.id",
                        message="step.id must match ^[a-z0-9_]+$ when provided",
                    )
                )
            if step.id in seen_step_ids:
                issues.append(
                    ValidationIssue(
                        code="DUPLICATE_STEP_ID",
                        path=f"{step_path}.id",
                        message=f"duplicate step.id '{step.id}'",
                    )
                )
            seen_step_ids.add(step.id)

        for input_index, binding in enumerate(step.inputs):
            if domain_issue := _validate_reference_domain(
                domain=binding.target.domain,
                path=f"{step_path}.inputs[{input_index}].target.domain",
            ):
                issues.append(domain_issue)

            if binding.override is None:
                continue

            for substitution_index, substitution in enumerate(binding.override.substitutions):
                if domain_issue := _validate_reference_domain(
                    domain=substitution.from_.domain,
                    path=(
                        f"{step_path}.inputs[{input_index}].override"
                        f".substitutions[{substitution_index}].from.domain"
                    ),
                ):
                    issues.append(domain_issue)

        for output_index, output in enumerate(step.outputs):
            if domain_issue := _validate_reference_domain(
                domain=output.domain,
                path=f"{step_path}.outputs[{output_index}].domain",
            ):
                issues.append(domain_issue)

    for input_index, ref in enumerate(procedure.inputs):
        if domain_issue := _validate_reference_domain(
            domain=ref.domain,
            path=f"procedure.inputs[{input_index}].domain",
        ):
            issues.append(domain_issue)

    for output_index, ref in enumerate(procedure.outputs):
        if domain_issue := _validate_reference_domain(
            domain=ref.domain,
            path=f"procedure.outputs[{output_index}].domain",
        ):
            issues.append(domain_issue)

    return tuple(issues)


def assert_valid_procedure_structure(procedure: Procedure) -> None:
    """Raise ProcedureValidationError if the Procedure AST is structurally invalid."""

    issues = validate_procedure_structure(procedure)
    if issues:
        raise ProcedureValidationError(issues)
