"""The gate must reject stale environments even when requirements files match."""

import runpy
import sys
from pathlib import Path

check_pins = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/check-python-pins.py"))["check_pins"]


def test_installed_metadata_must_match_the_requirement(tmp_path, monkeypatch):
    (tmp_path / ".python-version").write_text(".".join(map(str, sys.version_info[:2])))
    requirements = tmp_path / "requirements.txt"
    requirements.write_text("fleet-gate-fixture==1.0 # pinned fixture\n")
    metadata = tmp_path / "fleet_gate_fixture-1.0.dist-info"
    metadata.mkdir()
    (metadata / "METADATA").write_text("Name: fleet-gate-fixture\nVersion: 1.0\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    assert check_pins(tmp_path) == []
    requirements.write_text("fleet-gate-fixture==2.0\n")
    assert check_pins(tmp_path) == ["fleet-gate-fixture: installed 1.0, expected 2.0"]


def test_missing_packages_runtime_drift_and_unsupported_pins_fail(tmp_path):
    (tmp_path / ".python-version").write_text("0.0")
    (tmp_path / "requirements.txt").write_text("fleet-nonexistent-fixture==1.0\nDjango>=6\n")
    failures = check_pins(tmp_path)
    assert len(failures) == 3
    assert "expected 0.0" in failures[0]
    assert "installed missing" in failures[1]
    assert "unsupported non-exact pin" in failures[2]
