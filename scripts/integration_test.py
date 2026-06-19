#!/usr/bin/env python3
"""Run SpendWise Docker Compose integration smoke tests.

By default this script is destructive for the local Compose stack: it starts the
stack and always finishes with ``docker compose down -v`` so CI gets a clean
database on every run.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TIMEOUT_SECONDS = 120
REQUEST_TIMEOUT_SECONDS = 5


class IntegrationError(RuntimeError):
    """Raised when the integration smoke test fails."""


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


def merged_environment() -> dict[str, str]:
    values = load_env_file(PROJECT_ROOT / ".env.example")
    values.update(load_env_file(PROJECT_ROOT / ".env"))
    values.update(os.environ)
    return values


def run_command(command: list[str]) -> int:
    print(f"$ {' '.join(command)}", flush=True)

    try:
        completed = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    except FileNotFoundError:
        print(f"{command[0]} was not found. Install Docker and Docker Compose first.", file=sys.stderr)
        return 127

    return completed.returncode


def request_json(
    method: str,
    url: str,
    payload: dict | None = None,
    token: str | None = None,
) -> tuple[int, dict]:
    headers = {"Accept": "application/json"}
    body = None

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            return response.status, json.loads(response_body or "{}")
    except urllib.error.HTTPError as error:
        response_body = error.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(response_body or "{}")
        except json.JSONDecodeError:
            data = {"error": response_body or str(error)}
        return error.code, data
    except urllib.error.URLError as error:
        raise IntegrationError(f"{method} {url} failed: {error.reason}") from error
    except TimeoutError as error:
        raise IntegrationError(f"{method} {url} timed out") from error
    except OSError as error:
        raise IntegrationError(f"{method} {url} failed: {error}") from error
    except json.JSONDecodeError as error:
        raise IntegrationError(f"{method} {url} returned invalid JSON") from error


def expect_status(
    method: str,
    url: str,
    expected_status: int,
    payload: dict | None = None,
    token: str | None = None,
) -> dict:
    status, data = request_json(method, url, payload=payload, token=token)

    if status != expected_status:
        raise IntegrationError(
            f"{method} {url} expected HTTP {expected_status}, got {status}: {json.dumps(data, sort_keys=True)}"
        )

    return data


def assert_equal(label: str, actual, expected) -> None:
    if actual != expected:
        raise IntegrationError(f"{label} expected {expected!r}, got {actual!r}")


def assert_true(label: str, value) -> None:
    if not value:
        raise IntegrationError(f"{label} expected a truthy value, got {value!r}")


def wait_for_ready(base_url: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> None:
    deadline = time.monotonic() + timeout_seconds
    ready_url = f"{base_url}/ready"
    last_error = "not checked yet"

    while time.monotonic() < deadline:
        try:
            status, data = request_json("GET", ready_url)

            if status == 200 and data.get("status") == "ready":
                print(f"[PASS] {ready_url} is ready", flush=True)
                return

            last_error = f"HTTP {status}: {json.dumps(data, sort_keys=True)}"
        except IntegrationError as error:
            last_error = str(error)

        print(f"Waiting for {ready_url}: {last_error}", flush=True)
        time.sleep(3)

    raise IntegrationError(f"{ready_url} did not become ready within {timeout_seconds} seconds: {last_error}")


def run_in_network_tests() -> None:
    wait_for_ready("http://web-app:5000")

    auth_url = "http://auth-service:5001"
    transaction_url = "http://transaction-service:5002"
    unique_id = uuid4().hex
    email = f"integration-{unique_id}@example.com"
    password = "SpendWise123"

    signup_data = expect_status(
        "POST",
        f"{auth_url}/signup",
        201,
        payload={"name": "Integration Test", "email": email, "password": password},
    )
    assert_equal("signup user email", signup_data.get("user", {}).get("email"), email)

    login_data = expect_status(
        "POST",
        f"{auth_url}/login",
        200,
        payload={"email": email, "password": password},
    )
    token = login_data.get("access_token")
    assert_true("login access_token", token)
    assert_equal("login token_type", login_data.get("token_type"), "Bearer")

    me_data = expect_status("GET", f"{auth_url}/me", 200, token=token)
    user_id = me_data.get("user", {}).get("id")
    assert_true("current user id", user_id)
    assert_equal("current user email", me_data.get("user", {}).get("email"), email)

    income_data = expect_status(
        "POST",
        f"{transaction_url}/transactions",
        201,
        payload={
            "title": "Integration Salary",
            "amount": 1000,
            "type": "income",
            "category": "Salary",
        },
        token=token,
    )
    income_transaction = income_data.get("transaction", {})
    assert_equal("income transaction amount", income_transaction.get("amount"), 1000.0)

    expense_data = expect_status(
        "POST",
        f"{transaction_url}/transactions",
        201,
        payload={
            "title": "Integration Groceries",
            "amount": 125.5,
            "type": "expense",
            "category": "Food",
        },
        token=token,
    )
    expense_transaction = expense_data.get("transaction", {})
    assert_equal("expense transaction amount", expense_transaction.get("amount"), 125.5)

    transactions_data = expect_status("GET", f"{transaction_url}/transactions", 200, token=token)
    transactions = transactions_data.get("transactions", [])
    titles = {transaction.get("title") for transaction in transactions}
    assert_true("created income transaction in list", "Integration Salary" in titles)
    assert_true("created expense transaction in list", "Integration Groceries" in titles)

    summary = transactions_data.get("summary", {})
    assert_equal("summary total_income", summary.get("total_income"), 1000.0)
    assert_equal("summary total_expense", summary.get("total_expense"), 125.5)
    assert_equal("summary balance", summary.get("balance"), 874.5)

    charts = transactions_data.get("charts", {})
    assert_true("charts has income and expense data", charts.get("has_income_expense"))
    assert_true("charts has expense category data", charts.get("has_expense_by_category"))
    assert_true("charts income_expense list", charts.get("income_expense"))

    search_data = expect_status("GET", f"{transaction_url}/transactions?search=groceries", 200, token=token)
    search_titles = {transaction.get("title") for transaction in search_data.get("transactions", [])}
    assert_equal("search result titles", search_titles, {"Integration Groceries"})

    print("Integration smoke test passed.", flush=True)


def run_host_orchestration() -> int:
    env = merged_environment()
    port = env.get("WEB_APP_HOST_PORT", "8000")
    stack_started = False
    result = 1

    try:
        result = run_command(["docker", "compose", "up", "--build", "-d"])

        if result != 0:
            return result

        stack_started = True
        wait_for_ready(f"http://localhost:{port}")

        result = run_command(["docker", "compose", "--profile", "test", "run", "--rm", "integration-tests"])
    except IntegrationError as error:
        print(f"[FAIL] {error}", file=sys.stderr, flush=True)
        result = 1
    finally:
        if stack_started:
            cleanup_result = run_command(["docker", "compose", "down", "-v"])

            if result == 0 and cleanup_result != 0:
                result = cleanup_result

    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run SpendWise integration smoke tests. Default mode starts the Compose stack and removes volumes "
            "afterwards; use --in-network only from inside the Compose network."
        )
    )
    parser.add_argument(
        "--in-network",
        action="store_true",
        help="Run HTTP assertions against Compose service names without starting or stopping the stack.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.in_network:
        try:
            run_in_network_tests()
        except IntegrationError as error:
            print(f"[FAIL] {error}", file=sys.stderr, flush=True)
            return 1

        return 0

    return run_host_orchestration()


if __name__ == "__main__":
    raise SystemExit(main())
