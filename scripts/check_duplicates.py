"""Code-duplication gate powered by LucidShark's `lucidshark-duplo` (Duplo).

On first run the pinned Duplo binary is downloaded for the current platform into
the user cache directory and reused thereafter, so the gate works locally and in
CI with no Rust toolchain or extra Python dependencies (standard library only).
Exits non-zero when the overall duplicated-code percentage exceeds a threshold.
"""

from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

DUPLO_VERSION = "0.2.0"
DEFAULT_THRESHOLD = 5.0
DEFAULT_MIN_LINES = 4
_BASE_URL = "https://github.com/toniantunovi/lucidshark-duplo/releases/download"

_UNAVAILABLE_HELP = """\
  The duplication gate needs to execute a downloaded prebuilt binary.
  On a managed Windows endpoint, policy blocking low-prevalence executables
  commonly refuses to run it.
  Fixes: ask IT for an exclusion for the cached binary, or point
  LUCIDSHARK_DUPLO at an approved copy.
  Do not rename or move the binary to get around the rule."""

_ARCH_BY_MACHINE = {
    "x86_64": "x86_64",
    "amd64": "x86_64",
    "aarch64": "aarch64",
    "arm64": "aarch64",
}


def _cache_dir() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    else:
        base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "lucidshark-duplo"


def _binary_name() -> str:
    return "lucidshark-duplo.exe" if sys.platform == "win32" else "lucidshark-duplo"


def _asset_name() -> str:
    if sys.platform == "win32":
        return "lucidshark-duplo-windows-x86_64.zip"
    os_part = {"linux": "linux", "darwin": "macos"}[sys.platform]
    arch = _ARCH_BY_MACHINE[platform.machine().lower()]
    return f"lucidshark-duplo-{os_part}-{arch}.tar.gz"


def _extract_archive(archive_path: Path, dest: Path) -> None:
    opener = zipfile.ZipFile if archive_path.suffix == ".zip" else tarfile.open
    with opener(archive_path) as archive:
        archive.extractall(dest)


def _download_binary(target: Path) -> None:
    asset = _asset_name()
    url = f"{_BASE_URL}/v{DUPLO_VERSION}/{asset}"
    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading lucidshark-duplo v{DUPLO_VERSION} ({asset})...", file=sys.stderr)
    # Keep the asset's extension in the download path: urlretrieve's
    # auto-generated temp name drops it, defeating the zip-vs-tar detection
    # in _extract_archive.
    archive = target.parent / asset
    urllib.request.urlretrieve(url, archive)
    try:
        _extract_archive(archive, target.parent)
    finally:
        archive.unlink(missing_ok=True)
    if not target.is_file():
        sys.exit(f"error: {target} not found after extraction")
    target.chmod(0o755)


def _resolve_binary() -> Path:
    env_path = os.environ.get("LUCIDSHARK_DUPLO")
    if env_path and Path(env_path).is_file():
        return Path(env_path)
    existing = shutil.which("lucidshark-duplo")
    if existing:
        return Path(existing)

    target = _cache_dir() / f"v{DUPLO_VERSION}" / _binary_name()
    if target.is_file():
        return target

    _download_binary(target)
    return target


def _parse_duplication_percent(output: str) -> float | None:
    match = re.search(r"Duplication:\s*([\d.]+)%", output)
    return float(match.group(1)) if match else None


def _in_ci() -> bool:
    return os.environ.get("CI", "").strip().lower() not in {"", "0", "false"}


def _run_duplo(min_lines: int) -> str:
    """Download Duplo if needed, run it over the git-tracked tree, return its output."""
    binary = _resolve_binary()
    result = subprocess.run(
        [str(binary), "--git", "-m", str(min_lines), "-p", "100"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr


def _report_unavailable(exc: OSError, *, required: bool) -> int:
    """Report that the gate could not run and decide whether that is fatal.

    Endpoint policy blocking low-prevalence executables commonly refuses the
    downloaded binary (surfacing as WinError 5 or 2). Renaming or relocating
    the binary would evade that control, so advise an IT exclusion instead.
    """
    print(f"error: could not run lucidshark-duplo: {exc}", file=sys.stderr)
    print(_UNAVAILABLE_HELP, file=sys.stderr)
    if required:
        print("Duplication gate FAILED: gate could not run.", file=sys.stderr)
        return 1
    print(
        "Duplication gate SKIPPED: binary unavailable on this machine "
        "(not a pass - the gate did not run). Use --require-binary to make this "
        "fatal; it is already fatal in CI.",
        file=sys.stderr,
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="Maximum duplicated-code percent allowed (default: %(default)s)",
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=DEFAULT_MIN_LINES,
        help="Minimum duplicate block size in lines (default: %(default)s)",
    )
    parser.add_argument(
        "--require-binary",
        action="store_true",
        help="Fail if Duplo cannot be downloaded or executed, instead of skipping "
        "(always on in CI)",
    )
    args = parser.parse_args()

    # One handler covers both failure modes: urllib raises URLError (an OSError)
    # when the download fails, and exec of a blocked binary raises OSError too.
    try:
        output = _run_duplo(args.min_lines)
    except OSError as exc:
        return _report_unavailable(exc, required=args.require_binary or _in_ci())
    print(output, end="")

    percent = _parse_duplication_percent(output)
    if percent is None:
        print("Duplication gate FAILED: could not parse duplication summary.", file=sys.stderr)
        return 1
    if percent > args.threshold:
        print(
            f"Duplication gate FAILED: {percent}% > {args.threshold}% threshold.",
            file=sys.stderr,
        )
        return 1

    print(
        f"Duplication gate passed: {percent}% <= {args.threshold}% threshold.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
