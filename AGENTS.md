# AGENTS.md

Instructions for AI coding agents working in this repository.

## Quick Start

```bash
uv sync
uv run pytest          # run tests
uv run pyright src/    # type-check
uv run ruff check src/     # lint
uv run ruff format --check src/  # format check
```

## Required Workflow

Always run these before considering work complete:

```bash
uv run pyright src/ && uv run ruff check src/ && uv run ruff format --check src/ && uv run pytest
```

All four must pass with zero errors.

## Coding Conventions (Enforced)

These are **not** preferences — the toolchain will fail if you violate them:

### Use `from __future__ import annotations`
Every module must start with this import for consistent type-hint semantics.

```python
# ❌ Wrong
def foo() -> str: ...

# ✅ Right
from __future__ import annotations


def foo() -> str: ...
```

### Strict type checking
Pyright runs in `strict` mode. All function parameters and return types must
have explicit type annotations.

```python
# ❌ Wrong
def add(a, b):
    return a + b

# ✅ Right
def add(a: int, b: int) -> int:
    return a + b
```

### Formatting
- Line length: 100 characters
- Double quotes for strings
- Import sorting via `isort` (ruff's `I` rules)
- Modern Python idioms via `UP` (pyupgrade) rules

## Formatting

If the linter complains about formatting, run:

```bash
uv run ruff format src/
uv run ruff check --fix src/
```

This runs two steps:
1. `ruff format` — formats all files (indentation, quotes, etc.)
2. `ruff check --fix` — applies lint auto-fixes (import sorting, etc.)

## Project Structure

- Source code lives in `src/`
- Tests live in `src/tests/` (filenames start with `test_`)
- Python ≥ 3.11 — managed automatically by uv
- Dependencies declared in `pyproject.toml`
