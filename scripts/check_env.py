#!/usr/bin/env python3
"""Validate required SpendWise environment variables."""

import os
from pathlib import Path
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

REQUIRED_VARIABLES = [
    "APP_ENV",
    "LOG_LEVEL",
    "WEB_APP_PORT",
    "AUTH_SERVICE_PORT",
    "TRANSACTION_SERVICE_PORT",
    "AUTH_SERVICE_URL",
    "TRANSACTION_SERVICE_URL",
    "SERVICE_TIMEOUT_SECONDS",
    "AUTH_DATABASE_URL",
    "TRANSACTION_DATABASE_URL",
    "SECRET_KEY",
    "JWT_SECRET",
    "JWT_EXPIRES_MINUTES",
    "SESSION_COOKIE_SECURE",
    "SESSION_COOKIE_HTTPONLY",
    "SESSION_COOKIE_SAMESITE",
]

VALID_APP_ENVS = {"development", "testing", "production"}
VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
VALID_SAMESITE_VALUES = {"Lax", "Strict", "None"}
PLACEHOLDER_VALUES = {"change-me", "your_password", "password"}


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


def validate_port(name, value, errors):
    try:
        port = int(value)
    except ValueError:
        errors.append(f"{name} must be a number.")
        return

    if port < 1 or port > 65535:
        errors.append(f"{name} must be between 1 and 65535.")


def validate_positive_number(name, value, errors):
    try:
        number = float(value)
    except ValueError:
        errors.append(f"{name} must be a number.")
        return

    if number <= 0:
        errors.append(f"{name} must be greater than zero.")


def validate_database_url(name, value, errors):
    parsed_url = urlparse(value)

    if parsed_url.scheme not in {"postgresql", "postgres"}:
        errors.append(f"{name} must start with postgresql://.")

    if not parsed_url.hostname or not parsed_url.path.strip("/"):
        errors.append(f"{name} must include host and database name.")


def validate_http_url(name, value, errors):
    parsed_url = urlparse(value)

    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        errors.append(f"{name} must be a valid http:// or https:// URL.")


def has_placeholder(value):
    return any(placeholder in value for placeholder in PLACEHOLDER_VALUES)


def main():
    env = load_env_file(ENV_FILE)
    env.update({name: os.getenv(name, "") for name in REQUIRED_VARIABLES if os.getenv(name)})

    if ENV_FILE.exists():
        print("[OK] Loaded environment from .env and process variables.\n")
    else:
        print("[INFO] .env file not found. Using process environment variables.\n")

    errors = []
    warnings = []

    for name in REQUIRED_VARIABLES:
        value = env.get(name)

        if value:
            print(f"[OK] {name} is set.")
        else:
            errors.append(f"{name} is missing or empty.")

    if errors:
        print("\nEnvironment check failed:")
        for error in errors:
            print(f"- {error}")
        print("\nCreate .env with: cp .env.example .env")
        print("Or provide these variables through your shell/Docker environment.")
        return 1

    if env["APP_ENV"] not in VALID_APP_ENVS:
        errors.append("APP_ENV must be one of: development, testing, production.")

    if env["LOG_LEVEL"].upper() not in VALID_LOG_LEVELS:
        errors.append("LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL.")

    if env["SESSION_COOKIE_SAMESITE"] not in VALID_SAMESITE_VALUES:
        errors.append("SESSION_COOKIE_SAMESITE must be one of: Lax, Strict, None.")

    for name in ["WEB_APP_PORT", "AUTH_SERVICE_PORT", "TRANSACTION_SERVICE_PORT"]:
        validate_port(name, env[name], errors)

    for name in ["SERVICE_TIMEOUT_SECONDS", "JWT_EXPIRES_MINUTES"]:
        validate_positive_number(name, env[name], errors)

    for name in ["AUTH_DATABASE_URL", "TRANSACTION_DATABASE_URL"]:
        validate_database_url(name, env[name], errors)

    for name in ["AUTH_SERVICE_URL", "TRANSACTION_SERVICE_URL"]:
        validate_http_url(name, env[name], errors)

    for name in ["AUTH_DATABASE_URL", "TRANSACTION_DATABASE_URL", "SECRET_KEY", "JWT_SECRET"]:
        if has_placeholder(env[name]):
            warnings.append(f"{name} still contains a placeholder value.")

    if errors:
        print("\nEnvironment validation errors:")
        for error in errors:
            print(f"- {error}")
        return 1

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")

    print("\nEnvironment check completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
