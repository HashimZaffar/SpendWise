import json
import logging
import os
from datetime import datetime, timezone
from uuid import uuid4

import jwt
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, text

load_dotenv()

VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
VALID_TRANSACTION_TYPES = {"income", "expense"}


def parse_port(value):
    try:
        port = int(value)
    except (TypeError, ValueError):
        raise RuntimeError("TRANSACTION_SERVICE_PORT must be a valid integer.")

    if port < 1 or port > 65535:
        raise RuntimeError("TRANSACTION_SERVICE_PORT must be between 1 and 65535.")

    return port


APP_ENV = os.getenv("APP_ENV", "development").lower()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
TRANSACTION_DATABASE_URL = os.getenv("TRANSACTION_DATABASE_URL") or os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
TRANSACTION_SERVICE_PORT = parse_port(os.getenv("TRANSACTION_SERVICE_PORT", "5002"))

if LOG_LEVEL not in VALID_LOG_LEVELS:
    raise RuntimeError("LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL.")

if not TRANSACTION_DATABASE_URL:
    raise RuntimeError("TRANSACTION_DATABASE_URL is required.")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is required.")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "transaction-service",
            "request_id": getattr(record, "request_id", None),
        }

        for key in ["method", "path", "status_code", "user_id", "duration_ms"]:
            value = getattr(record, key, None)
            if value is not None:
                log_data[key] = value

        return json.dumps(log_data)


logger = logging.getLogger("transaction-service")
logger.setLevel(getattr(logging, LOG_LEVEL))
logger.handlers.clear()

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.propagate = False

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = TRANSACTION_DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def initialize_database():
    with app.app_context():
        db.create_all()


def get_bearer_token():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    return auth_header.removeprefix("Bearer ").strip()


def get_current_user_id():
    token = get_bearer_token()

    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
            issuer="spendwise-auth-service",
        )
    except jwt.PyJWTError:
        return None

    return int(payload["sub"])


def require_user_id():
    user_id = get_current_user_id()

    if not user_id:
        return None, (jsonify({"error": "Valid bearer token is required."}), 401)

    return user_id, None


def serialize_transaction(transaction):
    return {
        "id": transaction.id,
        "user_id": transaction.user_id,
        "title": transaction.title,
        "amount": transaction.amount,
        "type": transaction.type,
        "category": transaction.category,
        "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
    }


def validate_transaction_payload(data):
    title = data.get("title", "").strip()
    category = data.get("category", "").strip()
    transaction_type = data.get("type", "").strip().lower()

    try:
        amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return None, "Amount must be a valid number."

    if not title or not category:
        return None, "Title and category are required."

    if amount <= 0:
        return None, "Amount must be greater than zero."

    if transaction_type not in VALID_TRANSACTION_TYPES:
        return None, "Type must be income or expense."

    return {
        "title": title,
        "category": category,
        "amount": amount,
        "type": transaction_type,
    }, None


def build_summary(user_id):
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    total_income = sum(item.amount for item in transactions if item.type == "income")
    total_expense = sum(item.amount for item in transactions if item.type == "expense")

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
    }


@app.before_request
def start_request_context():
    g.request_id = request.headers.get("X-Request-ID", str(uuid4()))
    g.request_started_at = datetime.now(timezone.utc)


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
    return jsonify({"status": "ok", "service": "transaction-service", "check": "health"}), 200


@app.route("/ready")
def ready():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({
            "status": "ready",
            "service": "transaction-service",
            "check": "ready",
            "checks": {"database": "ok"},
        }), 200
    except Exception as error:
        db.session.rollback()
        logger.error(
            f"Readiness database check failed: {error}",
            extra={"request_id": g.get("request_id")},
        )
        return jsonify({
            "status": "not_ready",
            "service": "transaction-service",
            "check": "ready",
            "checks": {"database": "error"},
        }), 503


@app.route("/transactions", methods=["GET"])
def list_transactions():
    user_id, error_response = require_user_id()

    if error_response:
        return error_response

    selected_filter = request.args.get("filter", "all")
    search_text = request.args.get("search", "").strip()

    query = Transaction.query.filter_by(user_id=user_id)

    if selected_filter in VALID_TRANSACTION_TYPES:
        query = query.filter_by(type=selected_filter)
    else:
        selected_filter = "all"

    if search_text:
        search_pattern = f"%{search_text}%"
        query = query.filter(
            or_(
                Transaction.title.ilike(search_pattern),
                Transaction.category.ilike(search_pattern),
            )
        )

    transactions = query.order_by(Transaction.created_at.desc()).all()

    return jsonify({
        "transactions": [serialize_transaction(item) for item in transactions],
        "summary": build_summary(user_id),
        "filter": selected_filter,
        "search": search_text,
    }), 200


@app.route("/transactions/<int:transaction_id>", methods=["GET"])
def get_transaction(transaction_id):
    user_id, error_response = require_user_id()

    if error_response:
        return error_response

    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()

    if not transaction:
        return jsonify({"error": "Transaction not found."}), 404

    return jsonify({"transaction": serialize_transaction(transaction)}), 200


@app.route("/transactions", methods=["POST"])
def create_transaction():
    user_id, error_response = require_user_id()

    if error_response:
        return error_response

    payload, error = validate_transaction_payload(request.get_json(silent=True) or {})

    if error:
        return jsonify({"error": error}), 400

    transaction = Transaction(user_id=user_id, **payload)
    db.session.add(transaction)
    db.session.commit()

    logger.info(
        "Transaction created",
        extra={"request_id": g.get("request_id"), "user_id": user_id},
    )

    return jsonify({"transaction": serialize_transaction(transaction)}), 201


@app.route("/transactions/<int:transaction_id>", methods=["PUT"])
def update_transaction(transaction_id):
    user_id, error_response = require_user_id()

    if error_response:
        return error_response

    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()

    if not transaction:
        return jsonify({"error": "Transaction not found."}), 404

    payload, error = validate_transaction_payload(request.get_json(silent=True) or {})

    if error:
        return jsonify({"error": error}), 400

    transaction.title = payload["title"]
    transaction.amount = payload["amount"]
    transaction.type = payload["type"]
    transaction.category = payload["category"]
    db.session.commit()

    logger.info(
        "Transaction updated",
        extra={"request_id": g.get("request_id"), "user_id": user_id},
    )

    return jsonify({"transaction": serialize_transaction(transaction)}), 200


@app.route("/transactions/<int:transaction_id>", methods=["DELETE"])
def delete_transaction(transaction_id):
    user_id, error_response = require_user_id()

    if error_response:
        return error_response

    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()

    if not transaction:
        return jsonify({"error": "Transaction not found."}), 404

    db.session.delete(transaction)
    db.session.commit()

    logger.info(
        "Transaction deleted",
        extra={"request_id": g.get("request_id"), "user_id": user_id},
    )

    return jsonify({"message": "Transaction deleted."}), 200


if __name__ == "__main__":
    if APP_ENV != "production":
        initialize_database()

    app.run(host="0.0.0.0", port=TRANSACTION_SERVICE_PORT, debug=APP_ENV == "development")
