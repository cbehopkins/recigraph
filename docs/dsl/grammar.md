# ReciGraph DSL Grammar (Structural Specification)

## Overview

This document defines the **structural grammar** of the ReciGraph DSL.

It describes the abstract shape of valid ReciGraph data, independent of YAML syntax.

The DSL is a **compile-time graph transformation system**.

It is not an execution language.

---

# Core Model

The DSL is composed of:

- Entities
- EntityReferences
- Steps
- Procedures
- Local ReferenceBindings
- Graph transformations

All DSL content is ultimately a **deterministic graph rewrite system**.

---

# Notation

We use the following conventions:

- `{ ... }` → object / record type
- `[T]` → list of T
- `T?` → optional field
- `|` → union type
- `string` → free text
- `integer`, `float`, `boolean` → primitives

---

# Primitive Types

## Identifier

Identifier := string matching /^[a-z0-9_]+$/

---

## EntityReference

EntityReference :=
    Domain "." Identifier ( "@" Version )?

Domain :=
    "ingredient"
  | "procedure"
  | "equipment"
  | "container"

Version := string | integer (optional)

---

# Core Entity Types

## Ingredient

Ingredient :=
{
    id: Identifier,
    name: string,

    family?: string,
    aliases?: [string],
    description?: string,
    default_unit?: string,
    notes?: string,
    tags?: [string]
}

---

# Step (Core Execution Unit)

Step :=
{
    id?: string,

    action: EntityReference,

    inputs?: [ReferenceBinding],

    outputs?: [EntityReference],

    context?: StepContext
}

---

## StepContext

StepContext :=
{
    notes?: string,
    tags?: [string],
    constraints?: [string]
}

---

# Reference Binding (STRICTLY STEP-LOCAL)

ReferenceBinding :=
{
    target: EntityReference,
    override?: OverrideSet
}

---

## OverrideSet

OverrideSet :=
{
    substitutions?: [Substitution]
}

---

## Substitution

Substitution :=
{
    from: EntityReference,
    to: EntityReference | Composition
}

---

## Composition

Composition :=
{
    ingredients: [EntityReference],
    adjustments?: [Adjustment]
}

---

## Adjustment

Adjustment :=
{
    type: "add" | "remove" | "scale",
    target: EntityReference,
    value?: float | integer
}

---

# Procedure (Graph of Steps)

Procedure :=
{
    id: string,

    name?: string,
    description?: string,

    steps: [Step],

    inputs?: [EntityReference],
    outputs?: [EntityReference],

    tags?: [string]
}

---

# Relationship Rules

## 1. Strict locality of bindings

ReferenceBindings:

- exist ONLY inside Steps
- apply ONLY during Step transformation
- do NOT persist beyond Step
- do NOT propagate between Steps

---

## 2. Sequential Step execution (compile-time model)

Steps are applied in order:

G₀ → G₁ → G₂ → ... → Gₙ

Each Step produces a new graph state.

---

## 3. No runtime semantics

The DSL has:

- no execution engine
- no runtime state
- no event system

Only compile-time transformation.

---

## 4. No Step composition (v1 constraint)

Steps:

- do NOT call other Steps
- do NOT dynamically generate Steps
- do NOT recurse

---

## 5. Procedure semantics

A Procedure is:

- a static ordered list of Steps
- a compile-time transformation pipeline
- a deterministic graph rewrite definition

---

# Reference Resolution

EntityReferences are resolved during compilation.

Resolution rules:

1. Domain selects registry
2. Identifier must exist
3. Version (if present) is handled by compiler
4. Resolution is stateless and deterministic

---

# Existence Constraint

For every EntityReference:

- Domain must exist
- Identifier must exist in registry
- Invalid references cause compile-time failure

---

# Graph Transformation Model

The compiler maintains a graph state:

G₀ → G₁ → ... → Gₙ

Each Step applies a pure transformation:

Gₙ → Gₙ₊₁

Rules:

- no mutation of previous states
- no shared mutable context
- deterministic output only

---

# Entity Rules

Entities are:

- immutable definitions
- globally referenced by EntityReference
- never modified by Steps or Procedures

---

# Design Principles

## 1. Determinism

Same input → same output always.

---

## 2. Locality

All transformation context is Step-scoped.

---

## 3. Immutability

Entities are never mutated.

---

## 4. Declarative structure

DSL describes structure, not execution.

---

## 5. Compile-time only system

All evaluation occurs during compilation.

No runtime system exists in v1.

---

# Extensibility

New entity domains may be added without modifying grammar:

Example:

ingredient.whole_milk
procedure.vanilla_base
equipment.blender
container.creami_pint
mixture.chocolate_sauce

---

# Versioning

EntityReference supports optional version suffix:

EntityReference :=
    Domain "." Identifier ( "@" Version )?

Example:

procedure.vanilla_base@1
