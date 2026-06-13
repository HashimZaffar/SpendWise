#!/usr/bin/env python3
"""Small Docker Compose helper for local SpendWise development."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HEALTH_TIMEOUT_SECONDS = 5


COMPOSE_COMMANDS = {
    "build": ["build"],
    "up": ["up", "--build", "-d"],
    "down": ["down"],
    "logs": ["logs", "--tail", "100"],
    "status": ["ps"],
    "clean": ["down", "-v", "--remove-orphans"],
}


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}

    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()

        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def compose(args: list[str]) -> int:
    command = ["docker", "compose", *args]
    print(f"$ {' '.join(command)}", flush=True)

    try:
        completed = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    except FileNotFoundError:
        print("Docker was not found. Install Docker and Docker Compose first.", file=sys.stderr)
        return 127

    return completed.returncode


def merged_environment() -> dict[str, str]:
    values = load_env_file(PROJECT_ROOT / ".env.example")
    values.update(load_env_file(PROJECT_ROOT / ".env"))
    values.update(os.environ)
    return values


def request_json(url: str) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(url, timeout=DEFAULT_HEALTH_TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8", errors="replace")
            return 200 <= response.status < 300, body
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return False, body or str(error)
    except urllib.error.URLError as error:
        return False, str(error.reason)
    except TimeoutError:
        return False, "request timed out"


def health() -> int:
    env = merged_environment()
    port = env.get("WEB_APP_HOST_PORT", "8000")
    base_url = f"http://localhost:{port}"
    checks = ["health", "ready"]
    failed = False

    for check in checks:
        url = f"{base_url}/{check}"
        ok, body = request_json(url)
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {url}")
        print(body)

        if not ok:
            failed = True

    return 1 if failed else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manage the local SpendWise Docker Compose environment.",
    )
    parser.add_argument(
        "command",
        choices=["build", "up", "down", "logs", "status", "health", "clean"],
        help="Docker helper command to run.",
    )
    parser.add_argument(
        "extra_args",
        nargs=argparse.REMAINDER,
        help="Optional extra arguments passed to docker compose for build/logs/status commands.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.command == "health":
        return health()

    compose_args = COMPOSE_COMMANDS[args.command]

    if args.command in {"build", "logs", "status"}:
        compose_args = [*compose_args, *args.extra_args]
    elif args.extra_args:
        print(f"Extra arguments are not supported for '{args.command}'.", file=sys.stderr)
        return 2

    result = compose(compose_args)

    if result == 0 and args.command == "up":
        port = merged_environment().get("WEB_APP_HOST_PORT", "8000")
        print(f"SpendWise is starting at http://localhost:{port}")

    return result


if __name__ == "__main__":
    raise SystemExit(main())
