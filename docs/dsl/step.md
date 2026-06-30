# Step

## Purpose

A Step is the fundamental execution unit in a ReciGraph procedure.

It represents a single transformation in the recipe graph.

A Step does not directly modify entities.

Instead, it:
- selects entities via references
- applies contextual bindings (overrides/substitutions)
- produces a resolved intermediate state used by subsequent steps

---

## Step Structure

Step :=
{
    id: string?,

    action: EntityReference,

    inputs?: [ReferenceBinding],

    outputs?: [EntityReference],

    context?: StepContext
}

---

## Fields

### id (optional)

A stable identifier for debugging, tracing, and compiler diagnostics.

---

### action

EntityReference pointing to a procedure that defines what the step does.

Example:
procedure.mix
procedure.heat
procedure.combine

---

### inputs

A list of ReferenceBinding objects.

These define:
- which entities are used
- how they are adapted in this step

Inputs are where substitution logic is applied.

---

### outputs (optional)

Entities produced or modified by this step.

Outputs are declarative, not imperative.

They describe the result of the step, not how it is stored.

---

### context (optional)

StepContext :=
{
    notes?: string,
    tags?: [string],
    constraints?: [string]
}

Used for:
- human readability
- compiler hints
- optimisation and validation

---

# Execution Semantics

A Step is executed by the compiler as follows:

1. Resolve action procedure
2. Resolve all input EntityReferences
3. Apply ReferenceBindings (including substitutions)
4. Materialise intermediate graph state
5. Emit outputs as resolved entities
6. Pass state to next Step

---

# Key Principle

Steps are declarative transformations of a graph.

They do not mutate entities directly.

They define how references are resolved and combined in a specific context.

---

# Example

## Basic mixing step

```yaml
id: mix_base

action: procedure.mix

inputs:
  - target: ingredient.whole_milk

  - target: ingredient.sugar
    override:
      substitutions:
        - from: ingredient.sugar
          to: ingredient.honey

outputs:
  - mixture.sweet_base
```

---

## Heating step

```yaml
id: heat_base

action: procedure.heat

inputs:
  - target: mixture.sweet_base

outputs:
  - mixture.heated_base
```

---

# Relationship to Reference System

Step is the first place where:

- ReferenceBinding becomes active
- substitutions are applied
- composition is resolved

Outside of Step:
- references are inert
- no transformation occurs

Inside Step:
- references become contextual and dynamic

---

# Relationship to Procedures

A Procedure is a sequence of Steps.

Procedure :=
{
    id: string,
    steps: [Step]
}

Steps are therefore:
- the atomic unit of execution
- the boundary of contextual transformation

---

# Design Principle

Steps are:

- immutable in definition
- deterministic in execution
- context-driven in interpretation
- purely declarative

They are not scripts.

They are graph transformation nodes.
