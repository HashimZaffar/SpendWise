import json
import logging
import os
import secrets
from datetime import datetime, timezone
from uuid import uuid4

import requests
from dotenv import load_dotenv
from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

load_dotenv()

VALID_APP_ENVS = {"development", "testing", "production"}
VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
VALID_SAMESITE_VALUES = {"Lax", "Strict", "None"}


def parse_bool_env(name, default=False):
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_port(value):
    try:
        port = int(value)
    except (TypeError, ValueError):
        raise RuntimeError("WEB_APP_PORT must be a valid integer.")

    if port < 1 or port > 65535:
        raise RuntimeError("WEB_APP_PORT must be between 1 and 65535.")

    return port


APP_ENV = os.getenv("APP_ENV", "development").lower()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
SECRET_KEY = os.getenv("SECRET_KEY")
WEB_APP_PORT = parse_port(os.getenv("WEB_APP_PORT", os.getenv("APP_PORT", "5000")))
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:5001").rstrip("/")
TRANSACTION_SERVICE_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://127.0.0.1:5002").rstrip("/")
SESSION_COOKIE_SECURE = parse_bool_env("SESSION_COOKIE_SECURE", APP_ENV == "production")
SESSION_COOKIE_HTTPONLY = parse_bool_env("SESSION_COOKIE_HTTPONLY", True)
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
SERVICE_TIMEOUT_SECONDS = float(os.getenv("SERVICE_TIMEOUT_SECONDS", "5"))

if APP_ENV not in VALID_APP_ENVS:
    raise RuntimeError("APP_ENV must be one of: development, testing, production.")

if LOG_LEVEL not in VALID_LOG_LEVELS:
    raise RuntimeError("LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL.")

if SESSION_COOKIE_SAMESITE not in VALID_SAMESITE_VALUES:
    raise RuntimeError("SESSION_COOKIE_SAMESITE must be one of: Lax, Strict, None.")

if SESSION_COOKIE_SAMESITE == "None" and not SESSION_COOKIE_SECURE:
    raise RuntimeError("SESSION_COOKIE_SECURE must be true when SESSION_COOKIE_SAMESITE is None.")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is required.")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "web-app",
            "request_id": getattr(record, "request_id", None),
        }

        for key in ["method", "path", "status_code", "user_id", "duration_ms"]:
            value = getattr(record, key, None)
            if value is not None:
                log_data[key] = value

        return json.dumps(log_data)


logger = logging.getLogger("web-app")
logger.setLevel(getattr(logging, LOG_LEVEL))
logger.handlers.clear()

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.propagate = False

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_COOKIE_SECURE"] = SESSION_COOKIE_SECURE
app.config["SESSION_COOKIE_HTTPONLY"] = SESSION_COOKIE_HTTPONLY
app.config["SESSION_COOKIE_SAMESITE"] = SESSION_COOKIE_SAMESITE


def auth_headers():
    token = session.get("access_token")

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}",
        "X-Request-ID": g.get("request_id", ""),
    }


def service_request(method, url, **kwargs):
    headers = kwargs.pop("headers", {})
    headers.setdefault("X-Request-ID", g.get("request_id", ""))

    response = requests.request(
        method,
        url,
        headers=headers,
        timeout=SERVICE_TIMEOUT_SECONDS,
        **kwargs,
    )

    try:
        data = response.json()
    except ValueError:
        data = {}

    return response, data


def current_user():
    return session.get("user")


def require_login():
    if not session.get("access_token") or not current_user():
        flash("Please login to access SpendWise.", "error")
        return redirect(url_for("login"))

    return None


def build_empty_dashboard_state():
    return {
        "transactions": [],
        "summary": {
            "total_income": 0,
            "total_expense": 0,
            "balance": 0,
        },
        "filter": "all",
        "search": "",
    }


@app.before_request
def start_request_context():
    g.request_id = request.headers.get("X-Request-ID", str(uuid4()))
    g.request_started_at = datetime.now(timezone.utc)

    if request.method == "POST":
        form_token = request.form.get("csrf_token")
        session_token = session.get("csrf_token")

        if not form_token or not session_token or not secrets.compare_digest(form_token, session_token):
            logger.warning(
                "CSRF validation failed",
                extra={
                    "request_id": g.request_id,
                    "method": request.method,
                    "path": request.path,
                },
            )
            abort(400)


@app.context_processor
def inject_csrf_token():
    def csrf_token():
        token = session.get("csrf_token")

        if not token:
            token = secrets.token_urlsafe(32)
            session["csrf_token"] = token

        return token

    return {"csrf_token": csrf_token}


@app.after_request
def log_request(response):
    response.headers["X-Request-ID"] = g.get("request_id", "")

    started_at = g.get("request_started_at")
    duration_ms = None

    if started_at:
        duration = datetime.now(timezone.utc) - started_at
        duration_ms = round(duration.total_seconds() * 1000, 2)

    logger.info(
        "Request completed",
        extra={
            "request_id": g.get("request_id"),
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )

    return response


@app.route("/health")
def health():
    return {"status": "ok", "service": "web-app", "check": "health"}, 200


@app.route("/ready")
def ready():
    checks = {
        "auth_service": "unknown",
        "transaction_service": "unknown",
    }
    status_code = 200

    for key, service_url in {
        "auth_service": AUTH_SERVICE_URL,
        "transaction_service": TRANSACTION_SERVICE_URL,
    }.items():
        try:
            response, _ = service_request("GET", f"{service_url}/ready")
            checks[key] = "ok" if response.ok else "error"
            if not response.ok:
                status_code = 503
        except requests.RequestException as error:
            checks[key] = "error"
            status_code = 503
            logger.error(
                f"Readiness check failed for {key}: {error}",
                extra={"request_id": g.get("request_id")},
            )

    return {
        "status": "ready" if status_code == 200 else "not_ready",
        "service": "web-app",
        "check": "ready",
        "checks": checks,
    }, status_code


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("access_token"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        payload = {
            "email": request.form.get("email", "").strip().lower(),
            "password": request.form.get("password", ""),
        }

        try:
            response, data = service_request("POST", f"{AUTH_SERVICE_URL}/login", json=payload)
        except requests.RequestException:
            flash("Auth service is not available right now.", "error")
            return redirect(url_for("login"))

        if not response.ok:
            flash(data.get("error", "Invalid email or password."), "error")
            return redirect(url_for("login"))

        session["access_token"] = data["access_token"]
        session["user"] = data["user"]
        flash("Logged in successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("signup"))

        payload = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip().lower(),
            "password": password,
        }

        try:
            response, data = service_request("POST", f"{AUTH_SERVICE_URL}/signup", json=payload)
        except requests.RequestException:
            flash("Auth service is not available right now.", "error")
            return redirect(url_for("signup"))

        if not response.ok:
            flash(data.get("error", "Could not create account."), "error")
            return redirect(url_for("signup"))

        flash("Account created successfully. Please login now.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    login_redirect = require_login()

    if login_redirect:
        return login_redirect

    edit_id = request.args.get("edit_id")
    transaction_to_edit = None

    if request.method == "POST":
        transaction_id = request.form.get("transaction_id")
        payload = {
            "title": request.form.get("title", "").strip(),
            "amount": request.form.get("amount", ""),
            "type": request.form.get("type", "").strip().lower(),
            "category": request.form.get("category", "").strip(),
        }

        try:
            if transaction_id:
                response, data = service_request(
                    "PUT",
                    f"{TRANSACTION_SERVICE_URL}/transactions/{transaction_id}",
                    headers=auth_headers(),
                    json=payload,
                )
                success_message = "Transaction updated successfully."
            else:
                response, data = service_request(
                    "POST",
                    f"{TRANSACTION_SERVICE_URL}/transactions",
                    headers=auth_headers(),
                    json=payload,
                )
                success_message = "Transaction added successfully."
        except requests.RequestException:
            flash("Transaction service is not available right now.", "error")
            return redirect(url_for("dashboard"))

        if not response.ok:
            flash(data.get("error", "Could not save transaction."), "error")
            return redirect(url_for("dashboard"))

        flash(success_message, "success")
        return redirect(url_for("dashboard"))

    selected_filter = request.args.get("filter", "all")
    search_text = request.args.get("search", "").strip()
    params = {"filter": selected_filter, "search": search_text}

    try:
        response, dashboard_data = service_request(
            "GET",
            f"{TRANSACTION_SERVICE_URL}/transactions",
            headers=auth_headers(),
            params=params,
        )
    except requests.RequestException:
        flash("Transaction service is not available right now.", "error")
        dashboard_data = build_empty_dashboard_state()
    else:
        if not response.ok:
            session.clear()
            flash("Please login again.", "error")
            return redirect(url_for("login"))

    if edit_id:
        try:
            response, data = service_request(
                "GET",
                f"{TRANSACTION_SERVICE_URL}/transactions/{edit_id}",
                headers=auth_headers(),
            )
            if response.ok:
                transaction_to_edit = data["transaction"]
        except requests.RequestException:
            flash("Could not load transaction for editing.", "error")

    summary = dashboard_data.get("summary", {})

    return render_template(
        "index.html",
        transactions=dashboard_data.get("transactions", []),
        total_income=summary.get("total_income", 0),
        total_expense=summary.get("total_expense", 0),
        balance=summary.get("balance", 0),
        transaction_to_edit=transaction_to_edit,
        selected_filter=dashboard_data.get("filter", selected_filter),
        search_text=dashboard_data.get("search", search_text),
        current_user=current_user(),
    )


@app.route("/delete/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
    login_redirect = require_login()

    if login_redirect:
        return login_redirect

    try:
        response, data = service_request(
            "DELETE",
            f"{TRANSACTION_SERVICE_URL}/transactions/{transaction_id}",
            headers=auth_headers(),
        )
    except requests.RequestException:
        flash("Transaction service is not available right now.", "error")
        return redirect(url_for("dashboard"))

    if not response.ok:
        flash(data.get("error", "Could not delete transaction."), "error")
        return redirect(url_for("dashboard"))

    flash("Transaction deleted successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=WEB_APP_PORT, debug=APP_ENV == "development")
