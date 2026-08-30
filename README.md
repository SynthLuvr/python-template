# Python Template

A minimal Python project template with a complete type-check, format, lint, test,
coverage, and security (SAST/SCA) toolchain. The code does nothing useful — it's a
starting point for new projects.

The toolchain lives in [canonist](https://github.com/SynthLuvr/canonist): one dev
dependency that bundles Ruff, Pyright (strict), pytest + pytest-cov, pip-audit, and
the lucidshark-duplo duplication gate, and ships the canonical ruff, pyright, and
pytest/coverage presets. This repo keeps only Poe the Poet as a direct dev
dependency. The toolchain runs identically on Linux and Windows (both exercised in
CI), and every tool is invoked as `python -m <module>` rather than through generated
console-script `.exe` stubs, so it also works on managed Windows endpoints that block
low-prevalence executables (see [Quick Start](#quick-start)).

## Tech Stack

| Tool | Purpose |
|------|---------|
| [uv](https://docs.astral.sh/uv/) | Package manager & virtual environment |
| [Python](https://www.python.org) | Language (≥ 3.14, managed by uv) |
| [canonist](https://github.com/SynthLuvr/canonist) | The shared lint/format/test/doctor toolchain |
| [Poe the Poet](https://poethepoet.natn.io/) | Task runner (single-command `poe lint` / `poe test`) |
| [Hatch](https://hatch.pypa.io/) | Build backend |

Bundled inside canonist: Ruff (formatter + linter + SAST rules), Pyright (strict type
checking), pytest + pytest-cov (test runner and 80% coverage gate), pip-audit
(dependency vulnerability scan), and lucidshark-duplo (code-duplication detection).

## Quick Start

```bash
uv sync --all-extras         # install dependencies (canonist + poethepoet)

uv run poe lint              # full static pipeline (format check, lint, typecheck, lock, audit, dupes)
uv run poe test              # run unit tests (80% coverage gate)
```

> **Restricted Windows endpoints.** `uv run poe` resolves to `.venv\Scripts\poe.exe`, a
> generated launcher stub, which endpoint policy blocking low-prevalence executables
> refuses to run — reporting a misleading
> `Access is denied` / `The system cannot find the file specified`. Use the module form
> instead; it works on every platform:
>
> ```bash
> uv run python -m poethepoet lint
> uv run python -m poethepoet test
> ```
>
> Only the entry point needs this: canonist itself has no console script (invoke it as
> `python -m canonist`), and it runs every bundled tool as `python -m <module>`.

## Tasks

Tasks live in `pyproject.toml` under `[tool.poe.tasks]` and run with `uv run poe <task>`
(or `uv run python -m poethepoet <task>` — see the note above).

| Task | Runs |
|------|------|
| `poe lint` | Full static pipeline via `canonist lint` (see below) |
| `poe test` | Test suite via `canonist test` (80% coverage gate) |
| `poe format` | Auto-format and auto-fix lint issues via `canonist format` (writes changes) |
| `poe doctor` | Environment diagnostics via `canonist doctor` |
| `poe check` | Everything — `poe lint` plus `poe test` |

Run `uv run poe` with no arguments to list every task. The canonist commands also run
directly (`uv run python -m canonist lint src/`) and accept path arguments plus
`--fast` on `lint` to skip the slow pip-audit and duplication steps.

## Commands

### Lint

`poe lint` runs `python -m canonist lint`, a fail-fast pipeline where each step's exit
code propagates:

1. Ruff format check
2. Ruff check (incl. the bandit/SAST rule set)
3. Pyright — strict type checking
4. `uv lock --check` — lockfile freshness (skipped without `uv.lock` locally, fatal in CI)
5. pip-audit — dependency vulnerability (SCA) scan of the production dependency set
6. lucidshark-duplo — duplication gate, 5% threshold

Steps 5 and 6 are skipped by `--fast`. The duplication gate uses a pinned prebuilt
binary that is auto-downloaded (cached under the user cache dir) on first run, so it
works locally and in CI with no Rust toolchain. Because it is a freshly downloaded
binary, a managed endpoint may refuse to execute it; when the binary cannot be
downloaded or run, the gate prints the reason and **fails in CI** (`CI` env var set)
so it can never silently vanish from a build, while locally it reports `SKIPPED` and
exits 0 — a loud non-pass, not a silent one. Set `LUCIDSHARK_DUPLO` to point at an
approved copy.

### Format

```bash
uv run poe format   # ruff format, then ruff check --fix (writes changes)
```

### Test

```bash
uv run poe test     # pytest with the canonical coverage gate
```

Tests live under `src/tests/` and are omitted from coverage measurement, so the 80%
gate reflects real source coverage.

### Doctor

```bash
uv run poe doctor   # diagnose the environment, bundled tools, and generated configs
```

Checks Python (≥ 3.14), uv, the bundled tools, the presets, the `[tool.canonist]`
overrides, and duplo availability.

## Tool Configuration

The canonical ruff, pyright, and pytest/coverage configurations ship inside canonist.
At invocation time canonist writes the **effective config** — preset deep-merged with
your `[tool.canonist.*]` overrides (later keys win, lists replace, tables merge
recursively) — into `.canonist/` at the project root and points each tool at it, then
removes the directory afterwards (keep it with `--keep-config`; it is gitignored).

This repo has no local deltas: the `[tool.canonist.ruff.lint.per-file-ignores]` table
in `pyproject.toml` marks where repo-specific overrides would go, e.g.

```toml
[tool.canonist.ruff.lint.per-file-ignores]
"scripts/*" = ["S"]   # add back if the repo grows helper scripts
```

Rule, threshold, and preset changes happen in canonist, not here: bump the canonist
version and the whole toolchain moves together.

## Coding Conventions

These are **enforced by the toolchain**, not just preferences:

- **`from __future__ import annotations`** in every module (ruff `I002`, via
  `required-imports` — a missing one is a lint error, not a style nit)
- **Strict type checking** — all functions need explicit parameter and return type
  annotations (Pyright strict mode; implicit `Any` is rejected)
- **Line length** — 100 characters
- **Double quotes** for strings
- **Import sorting** — ruff's isort integration, with `src.*` as first-party
- **Modern Python** — pyupgrade rules enforce current idioms

## Project Structure

```
├── .github/workflows/     # CI (Ubuntu + Windows)
├── src/
│   ├── __init__.py        # Package init (version)
│   ├── index.py           # Trivial module (replace with your code)
│   └── tests/
│       ├── __init__.py
│       └── test_index.py  # Trivial test
├── pyproject.toml         # Project config, deps, Poe tasks, canonist overrides
└── uv.lock                # Lockfile (generated by uv sync)
```

## CI

GitHub Actions runs the full pipeline on every pull request
(`.github/workflows/ci.yml`) on both Ubuntu and Windows:

1. Set up Python 3.14 with uv
2. Install dependencies (`uv sync --all-extras --locked`)
3. Lint — `uv run python -m poethepoet lint`
4. Test — `uv run python -m poethepoet test` (80% coverage gate)

## Extending the Template

### Add a new module

1. Create `src/my_module.py`, starting with `from __future__ import annotations`.
2. Annotate every function's parameters and return type.
3. Add tests in `src/tests/test_my_module.py`.
4. Run the full check pipeline (see [AGENTS.md](AGENTS.md)).

### Add dependencies

The template ships with **zero runtime dependencies**.

```bash
uv add requests                        # runtime dependency
uv add --optional dev mypy             # dev dependency (the `dev` extra)
```

### Change the Python version

Update `requires-python` in `pyproject.toml`. If you move off 3.14, also override the
preset's language pins via `[tool.canonist.ruff]` (`target-version`) and
`[tool.canonist.pyright]` (`pythonVersion`) so the bundled tools follow along.
