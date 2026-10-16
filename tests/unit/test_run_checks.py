"""Wiring guards for scripts/run_checks.py and scripts/check_yaml_schema.py.

These do not re-run the checks (that would recurse); they assert the runner is wired
to the three steps docs/SPEC.md requires, and that both scripts can be imported and
executed without depending on the caller's working directory.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(f"_script_{name}", SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_checks_has_the_three_spec_steps() -> None:
    run_checks = load_script("run_checks")
    assert [name for name, _ in run_checks.STEPS] == ["lint", "tests", "yaml-schema"]


def test_run_checks_resolves_the_repo_root() -> None:
    run_checks = load_script("run_checks")
    assert run_checks.REPO_ROOT == REPO_ROOT
    assert (run_checks.REPO_ROOT / "pyproject.toml").is_file()


def test_run_checks_invokes_tools_with_the_current_interpreter() -> None:
    """Prevents picking up a stray ruff/pytest from PATH on a different Python."""
    run_checks = load_script("run_checks")
    for _, cmd in run_checks.STEPS:
        assert cmd[0] == sys.executable


def test_check_yaml_schema_runs_from_an_unrelated_cwd(tmp_path: Path) -> None:
    """Plain `python scripts/check_yaml_schema.py` must import tanese_nlp from any cwd."""
    completed = subprocess.run(
        [sys.executable, str(SCRIPTS / "check_yaml_schema.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "ok" in completed.stdout
