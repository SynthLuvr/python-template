"""Dependency vulnerability (SCA) scan for production dependencies.

Exports the production dependency set with `uv export` into a temporary
requirements file, then audits it with `pip-audit --strict`. This runs as a
script (instead of an inline Poe shell task) so it behaves identically on
Linux, macOS, and Windows without depending on POSIX shell features such as
`/tmp` paths, `&&` chaining, or backslash line continuations.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def _run(command: Sequence[str]) -> None:
    """Run a command, echoing it first and propagating a non-zero exit code."""
    print(f"$ {' '.join(command)}", file=sys.stderr)
    completed = subprocess.run(list(command), check=False)
    if completed.returncode != 0:
        sys.exit(completed.returncode)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="python-template-audit-") as tmp_dir:
        requirements = Path(tmp_dir) / "requirements.txt"
        _run(
            [
                "uv",
                "export",
                "--no-dev",
                "--no-emit-project",
                "--format",
                "requirements-txt",
                "-o",
                str(requirements),
            ]
        )
        _run(["pip-audit", "-r", str(requirements), "--strict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
