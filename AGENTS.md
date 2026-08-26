# AGENTS.md

Instructions for AI coding agents working in this repository.

## Quick Start

```bash
uv sync --all-extras   # install dependencies (incl. dev tools)
uv run poe lint        # full static pipeline (type-check + lint + format + audit + dupes)
uv run poe test        # run tests
```

**If `uv run poe` fails with `Access is denied` (os error 5):** `.venv\Scripts\poe.exe`
is a generated launcher stub, which endpoint policy blocking low-prevalence
executables refuses to run on managed Windows machines. It is not a
filesystem permission problem and not worth debugging — use the equivalent module form,
here and for any other console script (`pyright`, `pytest`, `pip-audit`, ...):

```bash
uv run python -m poethepoet check
```

The Poe tasks already invoke their tools this way internally.

## Required Workflow

Always run these before considering work complete:

```bash
uv run poe check   # type-check + lint + format + audit + duplication + tests
# or, on a restricted Windows endpoint:
uv run python -m poethepoet check
```

All steps must pass with zero errors. `poe check` runs `poe lint` (type-check, lint,
format check, dependency audit, duplication gate) followed by `poe test`.

One caveat: the duplication gate runs a downloaded prebuilt binary, which the same
endpoint policy blocks. Where it cannot run it prints `Duplication gate SKIPPED` and exits 0 (in CI
it fails instead). `SKIPPED` means the gate did **not** run — do not read it as a pass,
and do not move or rename the binary to get around the block.

## Coding Conventions (Enforced)

These are **not** preferences — the toolchain will fail if you violate them:

### Use `from __future__ import annotations`
Every module must start with this import for consistent type-hint semantics. Enforced by
ruff `I002` (`required-imports`), so a missing one fails `poe lint`.

```python
# ❌ Wrong
def foo() -> str: ...

# ✅ Right
from __future__ import annotations


def foo() -> str: ...
```

### Strict type checking
Pyright runs in `strict` mode. All function parameters and return types must
have explicit type annotations. Strict mode also rejects implicit `Any` types
and untyped `dict`/`list` literals where the type can't be inferred.

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
uv run poe format
```

This runs two steps:
1. `ruff format` — formats all files (indentation, quotes, etc.)
2. `ruff check --fix` — applies lint auto-fixes (import sorting, etc.)

## Project Structure

- Source code lives in `src/`
- Tests live in `src/tests/` (filenames start with `test_`), and are excluded from
  coverage measurement so the 80% gate reflects real source coverage
- Toolchain helper scripts live in `scripts/`, and are type-checked and linted too
- Python ≥ 3.14 — managed automatically by uv
- Dependencies declared in `pyproject.toml`
