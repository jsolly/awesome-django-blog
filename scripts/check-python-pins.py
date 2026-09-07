"""Fail when the active Python environment differs from this repo's exact pins."""

import re
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def check_pins(root):
    errors = []
    wanted_python = (root / ".python-version").read_text().strip()
    running_python = ".".join(map(str, sys.version_info[:2]))
    if wanted_python != running_python:
        errors.append(f"Python {running_python} is active; expected {wanted_python}")
    for number, line in enumerate((root / "requirements.txt").read_text().splitlines(), 1):
        requirement = line.split("#", 1)[0].strip()
        if not requirement:
            continue
        match = re.fullmatch(r"([A-Za-z0-9._-]+)(?:\[[A-Za-z0-9_,.-]+\])?==([A-Za-z0-9.+!-]+)", requirement)
        if not match:
            errors.append(f"requirements.txt:{number}: unsupported non-exact pin {requirement!r}")
            continue
        package, wanted = match.groups()
        try:
            installed = version(package)
        except PackageNotFoundError:
            installed = "missing"
        if installed != wanted:
            errors.append(f"{package}: installed {installed}, expected {wanted}")
    return errors


if __name__ == "__main__":
    failures = check_pins(Path(__file__).resolve().parents[1])
    if failures:
        print("Python dependency drift: " + "; ".join(failures), file=sys.stderr)
        print("Activate the repo .venv and run python -m pip install -r requirements.txt.", file=sys.stderr)
        sys.exit(1)
    print("Python runtime and installed requirements match repo pins")
