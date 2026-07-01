# ReciGraph Compiler Specification (v1)

## Overview

The ReciGraph compiler is a **deterministic, single-pass, compile-time graph transformation system**.

It transforms YAML-defined DSL structures into a fully resolved graph representation.

The compiler does not execute recipes.

It performs **graph rewrites only**.

---

# Core Principle

The compiler evaluates:

YAML → AST → Graph State Transformations → Output

There is no runtime system.

There is no execution engine.

---

# Compiler Pipeline (Single Pass)

The compiler operates in a strict linear pipeline:

## 1. Parse Phase

Input YAML is parsed into an abstract syntax tree (AST).

Output:
- Procedure AST
- Step ASTs
- EntityReference structures

---

## 2. Validation Phase

Structural validation only:

- schema correctness
- required fields present
- syntactic validity of identifiers
- basic type checks

No semantic resolution occurs yet.

---

## 3. Resolution Phase

EntityReferences are resolved:

- Domain → registry selection
- Identifier lookup
- Version resolution (if present)

Result:
- fully linked reference graph

---

## 4. Graph Initialization Phase

Initial graph state is created:

G₀ := materialised representation of input entities

This graph contains:

- resolved ingredients
- initial procedure inputs
- base entity definitions

---

## 5. Step Transformation Phase (Core Compiler Loop)

For each Procedure:

For each Step in order:

Gₙ₊₁ = apply_step(Gₙ, Step)

Where:

- Gₙ is the current graph state
- Step is evaluated in isolation
- result is a new graph state

---

## Step Semantics (Compiler-Level)

Each Step is applied as:

### Step Evaluation Process

1. Resolve Step.action (Procedure reference)
2. Snapshot current graph state Gₙ
3. Apply Step-local ReferenceBindings
4. Apply substitutions within Step scope only
5. Perform graph rewrite transformation
6. Emit new graph state Gₙ₊₁

---

## Binding Rule (CRITICAL)

- ReferenceBindings exist ONLY within Step scope
- Bindings do NOT propagate between Steps
- Bindings do NOT modify global state
- Bindings are discarded after Step evaluation

---

## 6. Output Phase

The compiler produces:

### Final Graph
A fully resolved materialised graph Gₙ

### Execution Trace
A full Step-by-Step transformation log:

- input state per Step
- applied bindings
- resulting output state
- entity transformations

---

# Graph State Model

Graph State (G) is a **materialised representation** of the recipe at a given point.

It includes:

- resolved entities
- derived entities
- substitution results
- intermediate transformations
- structural metadata

Graph State is immutable.

Each Step produces a new Graph State.

---

# Step Execution Model

Each Step behaves as a pure function:

apply_step(Gₙ, Step) → Gₙ₊₁

Properties:

- deterministic
- stateless
- no side effects
- no external access beyond input graph state

---

# Procedure Execution Model

A Procedure is evaluated as:

G₀ → G₁ → G₂ → ... → Gₙ

Where:

- Steps are applied sequentially
- no branching
- no recursion
- no dynamic Step generation

---

# Binding Semantics

ReferenceBindings:

- apply only during Step evaluation
- modify only local graph view
- do not persist
- do not affect future Steps

Substitutions:

- replace or transform entity references
- are resolved within Step scope only

---

# Determinism Guarantee

Given identical input:

- same YAML
- same registry state
- same compiler version

The output is always identical:

- final graph Gₙ
- execution trace

---

# Error Model

Compilation fails on:

- unresolved EntityReference
- invalid Domain
- missing registry entries
- invalid Step structure
- invalid substitution targets

Errors are detected at compile time only.

---

# Output Model

The compiler returns:

{
    final_graph: GraphState,
    trace: [StepExecutionRecord]
}

---

## StepExecutionRecord

Each trace entry contains:

- step_id
- input_graph_snapshot_ref
- applied_bindings
- output_graph_snapshot_ref
- transformations_applied

---

# No Runtime System

The compiler has:

- no execution engine
- no runtime state
- no event loop
- no deferred evaluation

All computation is completed at compile time.

---

# Optimisation (Optional Future Phase)

The current v1 compiler:

- does NOT optimise Steps
- does NOT reorder transformations
- does NOT collapse graph states

Optimisation is explicitly deferred to future versions.

---

# Design Guarantees

## 1. Deterministic

Same input always produces same output.

---

## 2. Isolated Steps

Each Step operates only on its input graph state.

---

## 3. Immutable Graph States

Graph states are never mutated in place.

---

## 4. Local Binding Scope

All contextual transformations are Step-local only.

---

## 5. Single-Pass Compilation

The compiler processes Procedures in one linear pass.

---

# System Summary

The ReciGraph compiler is:

a deterministic, single-pass, compile-time graph rewriting engine with local-scoped transformation rules and full traceability.
