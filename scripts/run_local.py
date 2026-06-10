#!/usr/bin/env python3
"""Run SpendWise locally in the correct service startup order."""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
PYTHON = PROJECT_ROOT / "venv" / "bin" / "python"

SERVICES = [
    {
        "name": "auth-service",
        "command": [str(PYTHON), "services/auth-service/app.py"],
        "port_env": "AUTH_SERVICE_PORT",
        "default_port": "5001",
    },
    {
        "name": "transaction-service",
        "command": [str(PYTHON), "services/transaction-service/app.py"],
        "port_env": "TRANSACTION_SERVICE_PORT",
        "default_port": "5002",
    },
    {
        "name": "web-app",
        "command": [str(PYTHON), "services/web-app/app.py"],
        "port_env": "WEB_APP_PORT",
        "default_port": "5000",
    },
]


def load_env_file(path):
    values = {}

    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        clean_line = line.strip()

        if not clean_line or clean_line.startswith("#") or "=" not in clean_line:
            continue

        key, value = clean_line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def run_check(script_name):
    command = [sys.executable, str(PROJECT_ROOT / "scripts" / script_name)]
    return subprocess.run(command, cwd=PROJECT_ROOT, check=False).returncode


def wait_for_health(service_name, health_url, timeout_seconds=20):
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        try:
            with urlopen(health_url, timeout=2) as response:
                if response.status == 200:
                    print(f"[OK] {service_name} is healthy: {health_url}")
                    return True
        except URLError:
            time.sleep(1)

    print(f"[FAIL] {service_name} did not become healthy in time: {health_url}")
    return False


def stop_processes(processes):
    for process in processes:
        if process.poll() is None:
            process.terminate()

    for process in processes:
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


def main():
    if not PYTHON.exists():
        print("[FAIL] venv Python was not found.")
        print("Run: python3 -m venv venv && make install && make install-services")
        return 1

    print("Running project audit...")
    if run_check("project_audit.py") != 0:
        return 1

    print("\nChecking environment variables...")
    if run_check("check_env.py") != 0:
        return 1

    env = os.environ.copy()
    env.update(load_env_file(ENV_FILE))

    processes = []

    def handle_shutdown(signum, frame):
        print("\nStopping SpendWise services...")
        stop_processes(processes)
        raise SystemExit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        for service in SERVICES:
            print(f"\nStarting {service['name']}...")
            process = subprocess.Popen(service["command"], cwd=PROJECT_ROOT, env=env)
            processes.append(process)

            port = env.get(service["port_env"], service["default_port"])
            health_url = f"http://127.0.0.1:{port}/health"

            if not wait_for_health(service["name"], health_url):
                stop_processes(processes)
                return 1

        print("\nSpendWise is running.")
        web_port = env.get("WEB_APP_PORT", "5000")
        print(f"Open: http://127.0.0.1:{web_port}/")
        print("Press Ctrl+C to stop all services.\n")

        while True:
            for process in processes:
                if process.poll() is not None:
                    print("A service stopped unexpectedly. Stopping remaining services...")
                    stop_processes(processes)
                    return 1
            time.sleep(2)

    finally:
        stop_processes(processes)


if __name__ == "__main__":
    raise SystemExit(main())
