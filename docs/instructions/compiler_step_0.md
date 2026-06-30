# ReciGraph Compiler Implementation Plan (v1)

## Overview

This plan describes the step-by-step implementation of the ReciGraph compiler based on:

- DSL grammar
- Step semantics
- Procedure model
- Pydantic AST
- Single-pass compiler architecture

The goal is to reach a **working end-to-end compiler MVP** as quickly as possible.

The repository already contains the `src/recigraph/` package layout, including `model/`, `loader/`, `validation/`, `resolver/`, `renderer/`, and `cli/`.
Use the DSL and architecture docs under `docs/` as the source of truth, especially `docs/dsl/*.md`, `docs/architecture.md`, `docs/dsl/compiler_spec.md`, and the ADRs in `docs/decisions/`.



---

# Guiding Principle

Build in this order:

> Parse → Validate → Resolve → Transform → Trace → Output

Do NOT optimise.

Do NOT generalise.

Do NOT add features outside the minimal compiler loop.

---

# Target Output (v1 MVP)

The compiler must accept YAML and produce:

```python
CompilerOutput(final_graph=GraphState, trace=[StepExecutionRecord])
```

---

# Implementation Scope

```
recigraph/
│
├── src/recigraph/
│   ├── model/
│   ├── loader/
│   ├── validation/
│   ├── resolver/
│   ├── renderer/
│   └── cli/
│
└── tests/
    ├── model/
    ├── loader/
    ├── validation/
    ├── resolver/
    ├── renderer/
    └── fixtures/
```

---

# Phase 1 — Core Models (Pydantic Layer)

## Goal

Implement all structural models described across `docs/dsl/grammar.md`, `docs/dsl/references.md`, `docs/dsl/procedure.md`, `docs/dsl/step.md`, and `docs/dsl/step_semantics.md`, plus the supporting decisions in `docs/decisions/adr-003.md`, `docs/decisions/adr-004.md`, `docs/decisions/adr-005.md`, `docs/decisions/adr-006.md`, and `docs/decisions/adr-008.md`.

## Tasks

- [ ] EntityReference model
- [ ] Step model
- [ ] Procedure model
- [ ] ReferenceBinding system
- [ ] GraphState model
- [ ] CompilerOutput model
- [ ] StepExecutionRecord model

## Notes

- No logic
- No compiler code
- Only validation + structure
- Keep the models immutable and scoped to the DSL surface already documented in `docs/`

---

# Phase 2 — Registry Layer

## Goal

Provide lookup systems for EntityReferences.

## Tasks

- [ ] Ingredient registry
- [ ] Procedure registry
- [ ] Equipment registry
- [ ] Container registry

## Responsibilities

Each registry must support:

```python
get(identifier: str) -> Entity | None
exists(identifier: str) -> bool
```

## Notes

- Static in v1 (in-memory dictionaries)
- No database
- No persistence layer
- Registry lookups should match the dotted reference syntax in `docs/dsl/references.md`

---

# Phase 3 — YAML Loader + Parser

## Goal

Convert YAML → Pydantic AST

## Tasks

- [ ] YAML loader
- [ ] YAML → Procedure parsing
- [ ] YAML → Step parsing
- [ ] YAML → EntityReference parsing

## Output

```python
Procedure (Pydantic AST)
```

## Notes

- No validation beyond schema correctness
- No reference resolution yet
- Keep parsing separate from semantic analysis

---

# Phase 4 — Validation Layer

## Goal

Validate structural correctness of AST

## Tasks

- [ ] Required fields validation
- [ ] Identifier format validation
- [ ] Domain validation
- [ ] Step structure validation

## Notes

- Still no resolution
- No graph building
- Cross-entity and graph validation stay here, not in the parser

---

# Phase 5 — Reference Resolver

## Goal

Convert EntityReference → actual registry entity

## Tasks

- [ ] Domain routing (ingredient/procedure/etc.)
- [ ] Identifier lookup
- [ ] Version handling (stub for v1)
- [ ] Error handling for missing references

## Output

Resolved references attached to AST or intermediate structures

---

# Phase 6 — Graph State Initialiser

## Goal

Create initial GraphState G₀

## Tasks

- [ ] Build GraphState from Procedure.inputs
- [ ] Initialise entity map
- [ ] Prepare derived_entities container

## Output

```python
G0: GraphState
```

---

# Phase 7 — Step Execution Engine (CORE)

## Goal

Implement:

> apply_step(Gₙ, Step) → Gₙ₊₁

## Tasks

- [ ] Snapshot input graph
- [ ] Resolve Step.action
- [ ] Apply ReferenceBindings (LOCAL ONLY)
- [ ] Apply substitutions
- [ ] Generate transformed GraphState
- [ ] Record StepExecutionRecord

## Critical Rules

- No mutation of input graph
- No shared state
- No cross-step binding propagation
- Bindings remain Step-local and are discarded after each Step

---

# Phase 8 — Procedure Compiler Loop

## Goal

Execute full Procedure pipeline

## Logic

```python
G = G0
trace = []

for step in procedure.steps:
    G, record = apply_step(G, step)
    trace.append(record)
```

## Output

Final GraphState + trace

---

# Phase 9 — Compiler Orchestrator

## Goal

Single entry point

```python
compile(yaml_input) -> CompilerOutput
```

## Responsibilities

- load YAML
- parse → AST
- validate
- resolve references
- initialise graph
- run step engine
- return output
- Keep the API deterministic and single-pass

---

# Phase 10 — Trace System

## Goal

Make transformations observable

Each StepExecutionRecord must include:

- step_id
- input snapshot reference
- output snapshot reference
- bindings applied
- transformation summary

---

# Phase 11 — Test Suite (Critical)

## Required tests

### Parser tests
- valid YAML → AST

### Reference tests
- valid EntityReference resolves
- invalid reference fails

### Step tests
- substitution applies correctly
- bindings remain local
- graph immutability holds

### Compiler tests
- full procedure compilation
- deterministic output

### Model tests
- immutable model construction
- field-level validation on identifiers and references

---

# Phase 12 — Example Pipeline (MVP validation)

Implement at least:

## Example 1: Vanilla base

- ingredient.whole_milk
- ingredient.sugar
- procedure.mix
- procedure.heat

## Example 2: Substitution

- whole milk → oat milk + sugar

---

# Implementation Order (STRICT)

1. Models
2. Registry
3. Parser
4. Validation
5. Resolver
6. GraphState init
7. Step engine
8. Procedure loop
9. Compiler orchestrator
10. Trace system
11. Tests
12. Examples

---

# Agent Hand-off

## Scope

Start with Phase 1 only.

Do not implement parsing, resolution, graph execution, or renderer logic in this step.

## Checklist

- [ ] Inspect the existing `src/recigraph/model/` package.
- [ ] Implement or refine the immutable Pydantic models for:
    - [ ] `EntityReference`
    - [ ] `ReferenceBinding`
    - [ ] `Step`
    - [ ] `Procedure`
    - [ ] `GraphState`
    - [ ] `StepExecutionRecord`
    - [ ] `CompilerOutput`
- [ ] Keep the model surface aligned with `docs/dsl/grammar.md`, `docs/dsl/references.md`, `docs/dsl/procedure.md`, `docs/dsl/step.md`, and `docs/dsl/step_semantics.md`.
- [ ] Preserve immutability and strict validation.
- [ ] Add the smallest tests needed to prove the model layer behaves as specified.

## Acceptance Criteria

- Models are frozen and reject invalid shapes.
- Dotted entity references validate according to the DSL spec.
- Step-local binding structures remain separate from procedure inputs.
- The model test suite passes cleanly.

## Stop Condition

Once the model layer and its tests are green, stop and report back.

Do not move on to parser, resolver, step execution, or compiler orchestration in this task.

---

# Non-Goals (v1)

Do NOT implement:

- optimisation passes
- Step-to-Step composition
- runtime execution engine
- async processing
- persistence layer
- plugin system

---

# Success Criteria

You have a working v1 compiler when:

- YAML → GraphState + Trace works end-to-end
- substitutions apply correctly
- bindings are strictly local
- Step transformations are deterministic
- full Procedure compiles without manual intervention

---

# Summary

This implementation plan produces a:

deterministic, single-pass, compile-time graph transformation engine with full traceability

It is intentionally minimal, testable, and extendable.
