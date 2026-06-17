#!/usr/bin/env python3
"""Run local SpendWise CI checks: lint, tests, Docker build, and integration smoke tests."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON_FILES = [
    "services/auth-service/app.py",
    "services/transaction-service/app.py",
    "services/web-app/app.py",
    "scripts/docker_tools.py",
    "scripts/ci_check.py",
    "scripts/integration_test.py",
]


def command_to_string(command: list[str]) -> str:
    return " ".join(command)


def run_step(name: str, command: list[str], env: dict[str, str] | None = None) -> int:
    print(f"\n==> {name}", flush=True)
    print(f"$ {command_to_string(command)}", flush=True)

    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=env,
        check=False,
    )

    if completed.returncode == 0:
        print(f"[PASS] {name}", flush=True)
    else:
        print(f"[FAIL] {name}", flush=True)

    return completed.returncode


def ruff_command() -> list[str]:
    local_ruff = PROJECT_ROOT / ".venv" / "bin" / "ruff"

    if local_ruff.exists():
        return [str(local_ruff), "check", "services", "scripts"]

    system_ruff = shutil.which("ruff")

    if system_ruff:
        return [system_ruff, "check", "services", "scripts"]

    return [sys.executable, "-m", "ruff", "check", "services", "scripts"]


def base_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONPYCACHEPREFIX", "/tmp/spendwise-pycache")
    env.setdefault("RUFF_CACHE_DIR", "/tmp/spendwise-ruff-cache")
    return env


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local SpendWise CI checks.")
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Run lint and syntax checks only; skip Docker Compose config/build and integration checks.",
    )
    parser.add_argument(
        "--skip-integration",
        action="store_true",
        help="Run lint, syntax, and Docker build checks; skip the destructive integration smoke test.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    env = base_env()
    steps = [
        ("Lint", ruff_command()),
        ("Python syntax tests", [sys.executable, "-m", "py_compile", *PYTHON_FILES]),
    ]

    if not args.skip_build:
        steps.extend(
            [
                ("Docker Compose config", ["docker", "compose", "config"]),
                ("Docker image build", ["docker", "compose", "build"]),
            ]
        )

        if not args.skip_integration:
            steps.append(("Integration smoke test", [sys.executable, "scripts/integration_test.py"]))

    for name, command in steps:
        result = run_step(name, command, env=env)

        if result != 0:
            return result

    print("\nAll local CI checks passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
