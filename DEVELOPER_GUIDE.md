# Python Template — Developer Guide

> **TL;DR:** Minimal Python project template with a complete type-check,
> format, lint, and test toolchain. The code does nothing useful — it's
> a starting point for new projects.

## 1. Project Overview

A boilerplate repository that wires up a full, opinionated Python
toolchain so you can start writing code immediately without configuring
anything.

- **Type checking** — Pyright in strict mode
- **Formatting** — Ruff
- **Linting** — Ruff (E, F, W, I, UP, B, C4, SIM, TCH rule sets)
- **Testing** — pytest
- **CI** — GitHub Actions (type-check → lint → test on every PR)

The template code is intentionally trivial: a single `greet()` function
and one test.

## 2. Tech Stack

| Category | Technology | Notes |
|----|----|----|
| **Runtime** | Python ≥ 3.11 | Required (`requires-python` in `pyproject.toml`) |
| **Package Manager** | uv | Fast dependency management & virtual environments |
| **Build Backend** | Hatchling | Wheel building (`[build-system]`) |
| **Type Checker** | Pyright (strict) | Static type analysis |
| **Formatter** | Ruff | Fast, unified formatting |
| **Linter** | Ruff | Multi-rule linting (see §7 for details) |
| **Testing** | pytest 8 | Test runner configured in `pyproject.toml` |
| **CI** | GitHub Actions | type-check → lint → test on PRs |

## 3. Prerequisites & Setup

### Installation

```bash
uv sync
```

This creates a `.venv/` virtual environment and installs all
dependencies (including dev dependencies from the optional `dev` group).

### Run Commands

```bash
uv run pyright src/             # type-check
uv run pytest                   # run tests
uv run ruff check src/          # lint
uv run ruff format --check src/ # verify formatting
```

### Required Workflow

Before considering work complete, always run:

```bash
uv run pyright src/ && uv run ruff check src/ && uv run ruff format --check src/ && uv run pytest
```

All four must pass with zero errors.

## 4. Project Structure

```
python-template/
├── .github/
│   └── workflows/
│       ├── ci.yml                        # type-check → lint → test on PR
│       └── copilot-setup-steps.yml       # Copilot agent environment
├── src/
│   ├── __init__.py                       # Package init (version)
│   ├── index.py                          # Trivial module (replace with your code)
│   └── tests/
│       ├── __init__.py
│       └── test_index.py                 # Trivial test
├── .gitignore                            # Python + virtualenv patterns
├── AGENTS.md                             # Instructions for AI agents
├── README.md                             # User-facing docs
├── DEVELOPER_GUIDE.md                    # This file
└── pyproject.toml                        # Project config, deps, tool settings
```

## 5. Coding Conventions

These are **enforced by the toolchain**, not preferences. The linter
will fail if you violate them.

### 5.1 `from __future__ import annotations`

Every module must start with this import. It enables PEP 604 style
unions (`X | Y`) and deferred annotation evaluation on Python 3.11.

```python
# ❌ Missing import
def foo(x: int | None) -> str: ...

# ✅ Correct
from __future__ import annotations


def foo(x: int | None) -> str: ...
```

### 5.2 Strict Type Annotations

Pyright runs in `strict` mode. Every function parameter and return type
must have an explicit annotation.

```python
# ❌ Will fail type checking
def add(a, b):
    return a + b

# ✅ Correct
def add(a: int, b: int) -> int:
    return a + b
```

### 5.3 Formatting Rules

| Setting | Value |
|---------|-------|
| Line length | 100 characters |
| Quote style | Double quotes |
| Import sorting | `isort` (ruff `I` rules) |
| Target version | Python 3.11 |

## 6. Formatting Pipeline

If the linter complains about formatting, run:

```bash
uv run ruff format src/
uv run ruff check --fix src/
```

| Step | Command | What it does |
|------|---------|-------------|
| Format | `ruff format src/` | Formats all files (indentation, quotes, line width) |
| Lint fix | `ruff check --fix src/` | Applies auto-fixable lint rules (import sorting, etc.) |

## 7. Linting Configuration

`ruff check` uses these rule sets (configured in `pyproject.toml`):

| Rule Set | Prefix | What it catches |
|----------|--------|-----------------|
| pycodestyle errors | `E` | Style violations |
| Pyflakes | `F` | Undefined names, unused imports/variables |
| pycodestyle warnings | `W` | Style warnings |
| isort | `I` | Import ordering |
| pyupgrade | `UP` | Outdated Python syntax |
| flake8-bugbear | `B` | Common bugs and design problems |
| flake8-comprehensions | `C4` | Unnecessary comprehension/list/dict calls |
| flake8-simplify | `SIM` | Code simplification opportunities |
| flake8-type-checking | `TCH` | Imports only needed for type checking |

### Import Sorting

First-party imports (`src.*`) are sorted separately from third-party
packages:

```python
# ✅ Correct order
from __future__ import annotations

import sys

from src.index import greet
```

## 8. Testing

Tests live in `src/tests/` with filenames starting with `test_`.

```bash
uv run pytest        # run all tests
uv run pytest -v     # verbose output
uv run pytest -x     # stop on first failure
```

The pytest config in `pyproject.toml` sets:
- `testpaths = ["src/tests"]`
- `python_files = ["test_*.py"]`

## 9. CI/CD

### `ci.yml`

Runs on every pull request:

1. **Checkout** code
2. **Setup** uv
3. **Install** Python 3.11
4. **Sync** dependencies (`uv sync --all-extras`)
5. **Type-check** (`uv run pyright src/`)
6. **Lint** (`uv run ruff check src/`)
7. **Format check** (`uv run ruff format --check src/`)
8. **Test** (`uv run pytest`)

### `copilot-setup-steps.yml`

Provisions the environment for GitHub Copilot's coding agent:

1. **Checkout** code
2. **Setup** uv
3. **Install** Python 3.11
4. **Sync** dependencies (`uv sync --all-extras`)

Runs when the workflow file itself changes, or via manual dispatch.

## 10. Pyright Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| `pythonVersion` | `"3.11"` | Target Python version |
| `typeCheckingMode` | `"strict"` | Full strict type analysis |

In strict mode, Pyright enforces:
- All function parameters have type annotations
- All function return types are annotated
- No implicit `Any` types
- No untyped dict/list literals where types can't be inferred

## 11. Extending the Template

### Add a New Module

1. Create `src/my_module.py`.
2. Start with `from __future__ import annotations`.
3. Add type annotations to all functions.
4. Add tests in `src/tests/test_my_module.py`.
5. Run the full check pipeline.

### Add Runtime Dependencies

The template has zero runtime dependencies. Add what you need in
`pyproject.toml`:

```bash
uv add requests beautifulsoup4
```

### Add Dev Dependencies

```bash
uv add --group dev mypy
```

Or manually edit the `[project.optional-dependencies]` section.

### Change Python Version

Update `requires-python` in `pyproject.toml` and
`target-version`/`pythonVersion` in the ruff/pyright sections.
