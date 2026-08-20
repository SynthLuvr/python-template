"""Dependency vulnerability (SCA) audit for production dependencies.

Exports the production dependency set with `uv export` into a temporary
requirements file, then audits it with `pip-audit --strict`. Implemented as a
script (not a Poe `shell` task) so it runs identically on Linux, macOS, and
Windows with no POSIX shell features (`/tmp` paths, `&&`, line continuations).
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def _run(command: list[str]) -> None:
    """Echo and run `command`, exiting with its status on failure."""
    print(f"$ {' '.join(command)}", file=sys.stderr)
    result = subprocess.run(command)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp_dir:
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
