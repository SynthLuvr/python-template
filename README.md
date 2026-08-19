# Python Template

A minimal Python project template with a complete type-check, format, lint, test,
coverage, and security (SAST/SCA) toolchain. The code does nothing useful — it's a
starting point for new projects. The toolchain runs identically on Linux and
Windows (both exercised in CI), and the duplication gate ships prebuilt binaries
for Linux, macOS, and Windows.

## Tech Stack

| Tool | Purpose |
|------|---------|
| [uv](https://docs.astral.sh/uv/) | Package manager & virtual environment |
| [Python](https://www.python.org) | Language (≥ 3.14, managed by uv) |
| [Pyright](https://github.com/microsoft/pyright) | Static type checking (strict mode) |
| [Ruff](https://docs.astral.sh/ruff/) | Linter, formatter & security (SAST) rules |
| [pytest](https://docs.pytest.org/) + [pytest-cov](https://pytest-cov.readthedocs.io/) | Test runner & coverage gate |
| [pip-audit](https://github.com/pypa/pip-audit) | Dependency vulnerability (SCA) scan |
| [lucidshark-duplo](https://github.com/toniantunovi/lucidshark-duplo) | Code duplication (clone) gate |
| [Poe the Poet](https://poethepoet.natn.io/) | Task runner (single-command `poe lint` / `poe test`) |
| [Hatch](https://hatch.pypa.io/) | Build backend |

## Quick Start

```bash
uv sync --all-extras         # install dependencies (incl. dev tools: ruff, pyright, poethepoet, …)

uv run poe lint              # full static pipeline (type-check + lint + format + audit + dupes)
uv run poe test              # run unit tests (80% coverage gate)
```

## Tasks

Tasks live in `pyproject.toml` under `[tool.poe.tasks]` and run with `uv run poe <task>`.
Poe auto-detects the uv virtualenv, so tools resolve from it without an `uv run` prefix
inside each task.

| Task | Runs |
|------|------|
| `poe lint` | Full static pipeline: type-check, lint (incl. SAST), format check, dep audit, duplication gate |
| `poe test` | Test suite (80% coverage gate) |
| `poe check` | Everything — `poe lint` plus `poe test` |
| `poe format` | Auto-format and auto-fix lint issues (writes changes) |

Granular tasks are also available (`poe typecheck`, `poe lint-check`, `poe format-check`,
`poe audit`, `poe duplicates`). Run `uv run poe` with no arguments to list every task.

## Commands

### Type Check

```bash
uv run pyright src/          # strict type checking
```

### Lint

```bash
uv run ruff check src/       # lint all files
```

### Format

```bash
uv run ruff format src/      # format all files (writes changes)
uv run ruff format --check src/  # check formatting without writing
uv run ruff check --fix src/ # auto-fix lint issues
```

### Test

```bash
uv run pytest                # run all tests (enforces 80% coverage gate)
```

### Audit Dependencies

```bash
uv run poe audit                          # scan production deps for vulnerabilities
# or equivalently:
uv run python scripts/audit_deps.py
```

The audit runs through a portable script (temp-file handling in Python, no POSIX
shell features like `/tmp` paths or `&&` chaining), so it behaves the same on
Linux, macOS, and Windows.

### Check Duplication

```bash
uv run python scripts/check_duplicates.py   # fail if duplicated code exceeds the 5% threshold
```

The `lucidshark-duplo` binary is auto-downloaded (pinned version, cached under the user
cache dir) on first run, so this works locally and in CI with no Rust toolchain.

## Linting Configuration

`ruff check` uses these rule sets (configured in `pyproject.toml`):

| Rule set | Prefix | Catches |
|----------|--------|---------|
| pycodestyle errors | `E` | Style violations |
| Pyflakes | `F` | Undefined names, unused imports/variables |
| pycodestyle warnings | `W` | Style warnings |
| isort | `I` | Import ordering |
| pyupgrade | `UP` | Outdated Python syntax |
| flake8-bugbear | `B` | Common bugs and design problems |
| flake8-comprehensions | `C4` | Unnecessary comprehension/list/dict calls |
| flake8-simplify | `SIM` | Code simplification opportunities |
| flake8-type-checking | `TCH` | Imports only needed for type checking |
| flake8-bandit | `S` | Security issues and code smells (SAST) |

### Import Ordering

First-party imports (`src.*`, set via `known-first-party`) are sorted separately
from third-party packages:

```python
from __future__ import annotations

import sys

from src.index import greet
```

## Coding Conventions

These are **enforced by the toolchain**, not just preferences:

- **`from __future__ import annotations`** in every module
- **Strict type checking** — all functions need explicit type annotations
- **Line length** — 100 characters
- **Import sorting** — handled by ruff's isort integration
- **Modern Python** — pyupgrade rules enforce current idioms

## Project Structure

```
├── .github/workflows/     # CI (Ubuntu + Windows)
├── scripts/
│   ├── audit_deps.py      # Portable SCA audit (uv export + pip-audit)
│   └── check_duplicates.py  # Duplication gate (lucidshark-duplo)
├── src/
│   ├── __init__.py        # Package init (version)
│   ├── index.py           # Trivial module (replace with your code)
│   └── tests/
│       ├── __init__.py
│       └── test_index.py  # Trivial test
├── pyproject.toml         # Project config, deps, tool settings
└── uv.lock               # Lockfile (generated by uv sync)
```

## CI

GitHub Actions runs the full pipeline on every pull request (`.github/workflows/ci.yml`)
on both Ubuntu and Windows:

1. Set up Python 3.14 with uv
2. Install dependencies (`uv sync --all-extras`)
3. Lint — `uv run poe lint` (type-check, lint/SAST, format check, dep audit, duplication)
4. Test — `uv run poe test` (80% coverage gate)

## Extending the Template

### Add a new module

1. Create `src/my_module.py`, starting with `from __future__ import annotations`.
2. Annotate every function's parameters and return type.
3. Add tests in `src/tests/test_my_module.py`.
4. Run the full check pipeline (see [AGENTS.md](AGENTS.md)).

### Add dependencies

The template ships with **zero runtime dependencies**.

```bash
uv add requests              # runtime dependency
uv add --group dev mypy      # dev dependency (optional `dev` group)
```

### Change the Python version

Update `requires-python` in `pyproject.toml`, then match it in `target-version`
(ruff) and `pythonVersion` (pyright).
