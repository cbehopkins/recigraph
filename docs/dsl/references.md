# Entity References

## Purpose

Entity references define stable identity links between entities in the ReciGraph DSL.

A reference is primarily a **pointer to an entity definition**.

References may be used inside Steps where they can be combined with **local bindings**.

Bindings are strictly local to the Step in which they are defined and do not propagate.

---

# EntityReference

EntityReference :=
    Domain "." Identifier ( "@" Version )?

Where:

Domain :=
    "ingredient"
  | "procedure"
  | "equipment"
  | "container"

Identifier := string matching /^[a-z0-9_]+$/

Version := string | integer (optional, compiler-defined semantics)

---

## Example

ingredient.whole_milk
procedure.vanilla_base
equipment.blender
procedure.vanilla_base@1

---

# Core Rules

## 1. Identity is immutable

An EntityReference always identifies the same entity within its domain.

Entities are never modified through references.

---

## 2. References are passive outside Steps

Outside of a Step:

- references are static pointers
- no transformation occurs
- no bindings are applied

---

## 3. Bindings only exist inside Steps

Contextual modifications (overrides, substitutions) are:

- defined in ReferenceBinding structures
- applied ONLY within a Step
- discarded after Step evaluation

There is:

> NO global binding state
> NO cross-Step propagation

---

# Reference Binding (Step-local only)

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

Substitution defines a local replacement of an entity within a Step context.

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

Adjustment modifies composition behavior within a Step-local context.

Adjustment :=
{
    type: "add" | "remove" | "scale",
    target: EntityReference,
    value?: float | integer
}

---

# YAML Examples

## Basic reference

```yaml
target: ingredient.whole_milk
```

---

## Procedure inheritance (static reference only)

```yaml
extends: procedure.classic_vanilla_base
```

---

## Procedure composition (static structure only)

```yaml
includes:
  - procedure.coffee_base
  - procedure.chocolate_finish
```

---

## Step-local substitution example

```yaml
action: procedure.mix

inputs:
  - target: ingredient.whole_milk
    override:
      substitutions:
        - from: ingredient.whole_milk
          to:
            ingredients:
              - ingredient.oat_milk
              - ingredient.sugar
```

---

# Reference Resolution

References are resolved during the compiler's resolution phase.

Resolution is deterministic and stateless.

---

## Resolution Rules

1. The Domain determines which registry is queried:
   - ingredient → Ingredient registry
   - procedure  → Procedure registry
   - equipment  → Equipment registry
   - container   → Container registry

2. Identifier must exist within its domain.

3. Resolution is global and stateless.

4. Version suffix (if present) is handled by the compiler.

---

# Existence Constraint

For every EntityReference:

- Domain must exist in registry
- Identifier must exist within that domain
- Unresolved references are invalid at compile time

---

# Step-local Binding Rule (CRITICAL)

All override and substitution logic:

- applies ONLY within a single Step
- is evaluated during Step transformation
- does NOT persist beyond Step completion
- does NOT affect other Steps
- does NOT modify entity definitions

---

# No Cross-Step State

The system guarantees:

- no propagation of substitutions between Steps
- no shared mutable context
- each Step receives only the current graph state Gₙ

---

# Stability

The dotted reference syntax is part of the public DSL contract.

Compiler implementations may use richer internal representations, but:

- external syntax remains stable
- binding semantics remain Step-local

---

# Design Principle

EntityReferences define identity.

ReferenceBindings define local transformation behavior.

Together they form a **deterministic, scoped rewrite system inside Steps only**.

---

# Future Extensions

The reference system is designed to allow new domains without modification:

ingredient.whole_milk
procedure.vanilla_base
equipment.blender
container.creami_pint
mixture.chocolate_sauce

New entity types do not require changes to the reference grammar.

---

## Versioning

EntityReference may optionally include a version suffix:

EntityReference :=
    Domain "." Identifier ( "@" Version )?

Example:

procedure.vanilla_base@1
