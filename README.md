# ReciGraph

> Recipes as structured knowledge, not documents.

ReciGraph is a compiler and toolkit for representing recipes as structured, reusable data rather than static documents.

Recipes are authored in a declarative YAML-based domain-specific language (DSL). Those source files are validated, resolved and compiled into multiple outputs including static websites, printable cookbooks, shopping lists, ingredient indexes and AI-ready knowledge bases.

The project is intentionally designed using compiler architecture rather than traditional web application architecture.

Note: This project is the latest in my experiments to *better* use AI tools and coding agents. Expect Chaos!

## Why?

Traditional recipe collections duplicate enormous amounts of information.

A vanilla base might appear in dozens of recipes.
A chocolate sauce might be copied into twenty more.

Over time those copies drift apart.

ReciGraph models recipes as reusable components instead.

Rather than authoring documents, authors describe a graph of domain entities and relationships which are compiled into complete recipes.

## Current Status

The project is currently implementing the ReciGraph DSL incrementally using Test-Driven Development.

The first compiler increment implements the `Ingredient` entity.

Future increments will introduce:

* Actions
* Stages
* Procedures
* Inheritance
* Composition
* Static website generation

## Technology

* Python 3.13+
* Pydantic
* PyYAML
* pytest
* Ruff
* Pyright
* MkDocs
* Material for MkDocs

## Project Goals

* Eliminate duplicated recipe information.
* Encourage reuse through composition and inheritance.
* Provide strong validation before publication.
* Generate multiple outputs from a single source.
* Build a maintainable culinary knowledge graph.

## Repository Structure

```text
src/
    recigraph/

tests/

data/

docs/
```

The project is organised around compiler phases rather than application layers.

## Documentation

The project documentation lives in the `docs/` directory.

Recommended reading order:

1. `architecture.md`
2. `formatting.md`
3. `dsl.md` *(future)*
4. `compiler.md` *(future)*

## Licence

TBD.
