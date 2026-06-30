Each directory in this structure maps to a particular concern

model        → AST (Pydantic domain models)
loader       → YAML → AST
validation   → semantic checks (graph/type rules)
resolver     → inheritance + composition expansion
renderer     → view models → output formats
cli          → entry points

The test directory mirrors this approach
