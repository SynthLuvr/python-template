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


def _extract_archive(archive_path: str, dest: Path) -> None:
    opener = zipfile.ZipFile if archive_path.endswith(".zip") else tarfile.open
    with opener(archive_path) as archive:
        archive.extractall(dest)


def _download_binary(target: Path) -> None:
    asset = _asset_name()
    url = f"{_BASE_URL}/v{DUPLO_VERSION}/{asset}"
    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading lucidshark-duplo v{DUPLO_VERSION} ({asset})...", file=sys.stderr)
    archive, _ = urllib.request.urlretrieve(url)
    try:
        _extract_archive(archive, target.parent)
    finally:
        Path(archive).unlink(missing_ok=True)
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
    args = parser.parse_args()

    binary = _resolve_binary()
    result = subprocess.run(
        [str(binary), "--git", "-m", str(args.min_lines), "-p", "100"],
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
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
