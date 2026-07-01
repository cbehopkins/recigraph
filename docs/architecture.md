# ReciGraph Architecture

## Introduction

ReciGraph is not a recipe website.

It is not a content management system.

It is not a database.

ReciGraph is a compiler for a declarative recipe language.

The purpose of the compiler is to transform structured recipe definitions into one or more publishable representations while maintaining a single authoritative source of truth.

---

# The Problem

Recipes are traditionally stored as documents.

Documents are excellent for humans to read but poor at representing reusable knowledge.

For example:

* the same base recipe is copied repeatedly
* ingredient substitutions become inconsistent
* searching is limited
* structured analysis is difficult
* updating common techniques requires editing many recipes

As collections grow these problems compound.

---

# The Core Idea

Instead of modelling documents, ReciGraph models **knowledge**.

The knowledge base is represented as a graph of typed entities.

Examples include:

* Ingredients
* Ingredient Families
* Ingredient Choices
* Actions
* Stages
* Procedures
* Containers
* Equipment
* Mixtures

Relationships between those entities are explicit.

For example:

```text
Coffee Base
    extends
Vanilla Base

Espresso Martini
    includes
Coffee Base
```

The compiler resolves these relationships to produce complete recipes.

---

# Build And Compiler Pipeline

ReciGraph now separates build orchestration from compiler internals.

The build layer owns end-to-end output generation.

The compiler remains focused on transforming recipe source into Graph IR.

The end-to-end pipeline is:

```text
Recipe Sources
    │
    ▼
Discovery
    │
    ▼
Compiler
    │
    ▼
Graph IR
    │
    ▼
View Models
    │
    ▼
Renderers
    │
    ▼
Output Artifacts
    │
    ▼
Output Directory
```

Within that flow, compiler execution is still phase-oriented and deterministic.

Each phase performs one task.

Each phase is independently testable.

---

# Domain Model

The DSL is represented using immutable Pydantic models.

The domain model defines the language.

It deliberately contains no file loading, rendering or business logic.

Each compiler phase transforms immutable data into new immutable data.

---

# Compiler Phases

## Build Layer

Responsible for orchestration only.

Examples include:

* deterministic recipe source discovery
* compiler invocation
* Graph IR collection
* view-model construction handoff
* renderer invocation
* output directory and artifact management

The build layer does not perform parsing, validation, graph transformation or presentation templating.

## Loader

Responsible for:

* locating YAML files
* parsing YAML
* constructing domain models

The loader performs no graph validation.

---

## Validation

Responsible for semantic correctness.

Examples include:

* duplicate identifiers
* invalid references
* inheritance cycles
* invalid metadata
* type checking

Validation produces diagnostics.

It does not mutate data.

---

## Resolution

Responsible for transforming the authored model into a fully expanded model.

Examples include:

* inheritance
* composition
* ingredient choices
* generated relationships

The output is a resolved graph suitable for presentation.

---

## View Models

Renderers should not consume domain models directly.

Instead they consume specialised view models designed for presentation.

This keeps presentation concerns separate from the DSL.

---

## Renderers

Renderers transform view models into outputs such as:

* HTML
* PDF
* Shopping lists
* Search indexes
* Future APIs

The compiler is independent of any particular renderer.

---

# Project Principles

## Single Source of Truth

Recipes are authored once.

Everything else is generated.

## Strong Typing

The DSL is defined using modern Python typing and Pydantic models.

## Test-Driven Development

Every compiler increment is introduced through tests before implementation.

## Immutable Domain Objects

Compiler phases do not mutate existing objects.

They produce new ones.

## Small Compiler Increments

Development proceeds one language feature at a time.

Each increment introduces:

* schema
* implementation
* validation
* tests

before moving to the next feature.

---

# Initial Roadmap

The compiler will be implemented incrementally.

1. Ingredient
2. Action
3. Stage
4. Procedure
5. Validation
6. Resolution
7. Rendering
8. Static website generation

Each stage leaves the compiler in a working, testable state.

---

# Long-Term Vision

The initial use case is a high-quality Ninja Creami recipe knowledge base.

However, ReciGraph itself is intentionally generic.

The architecture should support many different culinary domains without changing the underlying compiler.

By modelling recipes as structured knowledge rather than documents, ReciGraph enables reuse, validation and multiple forms of publication from a single source of truth.
