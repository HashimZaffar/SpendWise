#!/usr/bin/env python3
"""Check that important SpendWise project files and folders exist."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "README.md",
    ".env.example",
    ".gitignore",
    ".dockerignore",
    "docker-compose.yml",
    "Makefile",
    "requirements.txt",
    "database/init/01-create-spendwise-databases.sql",
    "docs/local-setup.md",
    "docs/environment-variables.md",
    "docs/architecture.md",
    "docs/troubleshooting.md",
    "services/auth-service/app.py",
    "services/auth-service/Dockerfile",
    "services/auth-service/requirements.txt",
    "services/transaction-service/app.py",
    "services/transaction-service/Dockerfile",
    "services/transaction-service/requirements.txt",
    "services/web-app/app.py",
    "services/web-app/Dockerfile",
    "services/web-app/requirements.txt",
    "services/web-app/templates/login.html",
    "services/web-app/templates/signup.html",
    "services/web-app/templates/index.html",
    "services/web-app/static/style.css",
    "scripts/check_env.py",
    "scripts/project_audit.py",
    "scripts/run_local.py",
]

OPTIONAL_LOCAL_PATHS = [
    ".env",
    "venv",
]


def main():
    missing_paths = []

    print("SpendWise project audit\n")

    for relative_path in REQUIRED_PATHS:
        path = PROJECT_ROOT / relative_path

        if path.exists():
            print(f"[OK] {relative_path}")
        else:
            print(f"[MISSING] {relative_path}")
            missing_paths.append(relative_path)

    print("\nLocal-only files")
    for relative_path in OPTIONAL_LOCAL_PATHS:
        path = PROJECT_ROOT / relative_path
        status = "OK" if path.exists() else "NOT FOUND"
        print(f"[{status}] {relative_path}")

    if missing_paths:
        print("\nProject audit failed. Missing required paths:")
        for relative_path in missing_paths:
            print(f"- {relative_path}")
        return 1

    print("\nProject audit completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
