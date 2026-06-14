# API Reference

This reference documents the JSON APIs used by the web app. In the default Docker Compose setup, `auth-service` and `transaction-service` are internal services, while the browser talks to `web-app` at `http://localhost:8000`.

## Conventions

- Request and response bodies are JSON for service APIs.
- Browser routes use HTML forms and Flask sessions.
- Transaction routes require `Authorization: Bearer <token>`.
- Services add `X-Request-ID` to responses.
- Clients may send `X-Request-ID`; otherwise a new UUID is generated.
- Amounts are numeric values and are rounded to two decimals in summary responses.

## Browser Routes

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Login page or redirect to dashboard when already logged in |
| `GET` | `/login` | Login page |
| `POST` | `/login` | Submit login form |
| `GET` | `/signup` | Signup page |
| `POST` | `/signup` | Submit signup form |
| `GET` | `/dashboard` | Dashboard with optional `filter`, `search`, and `edit_id` query params |
| `POST` | `/dashboard` | Create or update a transaction |
| `POST` | `/delete/<transaction_id>` | Delete a transaction |
| `GET` | `/logout` | Clear session and redirect to login |
| `GET` | `/health` | Web app liveness |
| `GET` | `/ready` | Web app readiness and backend dependency checks |

Browser POST routes require the hidden `csrf_token` field rendered by the templates.

## Auth Service

Base URL inside Docker Compose:

```text
http://auth-service:5001
```

### `GET /health`

Returns process liveness.

```json
{
  "status": "ok",
  "service": "auth-service",
  "check": "health"
}
```

### `GET /ready`

Checks database connectivity.

Success:

```json
{
  "status": "ready",
  "service": "auth-service",
  "check": "ready",
  "checks": {
    "database": "ok"
  }
}
```

Failure returns `503` with `status: "not_ready"`.

### `POST /signup`

Creates a user.

Request:

```json
{
  "name": "Sam Lee",
  "email": "sam@example.com",
  "password": "secret123"
}
```

Validation:

- `name` is required.
- `email` is required and normalized to lowercase.
- `password` must be at least 6 characters.
- `email` must be unique.

Success response: `201`

```json
{
  "user": {
    "id": 1,
    "name": "Sam Lee",
    "email": "sam@example.com",
    "created_at": "2026-06-14T12:00:00"
  }
}
```

Common errors:

| Status | Meaning |
| ---: | --- |
| `400` | Missing name/email or password shorter than 6 characters |
| `409` | Email already exists |

### `POST /login`

Authenticates a user and returns a JWT.

Request:

```json
{
  "email": "sam@example.com",
  "password": "secret123"
}
```

Success response: `200`

```json
{
  "access_token": "<jwt>",
  "token_type": "Bearer",
  "expires_in": 7200,
  "user": {
    "id": 1,
    "name": "Sam Lee",
    "email": "sam@example.com",
    "created_at": "2026-06-14T12:00:00"
  }
}
```

Error:

| Status | Meaning |
| ---: | --- |
| `401` | Invalid email or password |

### `GET /me`

Returns the current user for a valid bearer token.

Headers:

```text
Authorization: Bearer <jwt>
```

Success response: `200`

```json
{
  "user": {
    "id": 1,
    "name": "Sam Lee",
    "email": "sam@example.com",
    "created_at": "2026-06-14T12:00:00"
  }
}
```

Common errors:

| Status | Meaning |
| ---: | --- |
| `401` | Missing, invalid, or expired token |
| `404` | Token subject no longer maps to a user |

## Transaction Service

Base URL inside Docker Compose:

```text
http://transaction-service:5002
```

All transaction routes require:

```text
Authorization: Bearer <jwt>
```

The JWT must be signed with `JWT_SECRET` and have issuer `spendwise-auth-service`.

### `GET /health`

Returns process liveness.

```json
{
  "status": "ok",
  "service": "transaction-service",
  "check": "health"
}
```

### `GET /ready`

Checks database connectivity.

Success:

```json
{
  "status": "ready",
  "service": "transaction-service",
  "check": "ready",
  "checks": {
    "database": "ok"
  }
}
```

Failure returns `503` with `status: "not_ready"`.

### `GET /transactions`

Returns dashboard data for the current user.

Query parameters:

| Name | Values | Purpose |
| --- | --- | --- |
| `filter` | `all`, `income`, `expense` | Optional transaction type filter. Invalid values fall back to `all`. |
| `search` | text | Optional case-insensitive search against title and category. |

Success response: `200`

```json
{
  "transactions": [
    {
      "id": 10,
      "user_id": 1,
      "title": "Groceries",
      "amount": 45.5,
      "type": "expense",
      "category": "Food",
      "created_at": "2026-06-14T12:00:00"
    }
  ],
  "summary": {
    "total_income": 5000.0,
    "total_expense": 45.5,
    "balance": 4954.5
  },
  "charts": {
    "income_expense": [
      {
        "label": "Income",
        "amount": 5000.0,
        "percent": 100.0
      },
      {
        "label": "Expense",
        "amount": 45.5,
        "percent": 0.91
      }
    ],
    "expense_by_category": [
      {
        "label": "Food",
        "amount": 45.5,
        "percent": 100.0
      }
    ],
    "recent_expense_trend": [
      {
        "label": "Sun",
        "date": "2026-06-14",
        "amount": 45.5,
        "percent": 100.0
      }
    ],
    "has_income_expense": true,
    "has_expense_by_category": true,
    "has_recent_expense_trend": true
  },
  "filter": "all",
  "search": ""
}
```

Notes:

- `summary` and `charts` are based on all transactions for the current user, not the filtered result set.
- `transactions` respects `filter` and `search`.
- `expense_by_category` returns the top five categories plus `Other` when more categories exist.
- `recent_expense_trend` covers the last seven calendar days.

### `GET /transactions/<transaction_id>`

Returns one transaction owned by the current user.

Success response: `200`

```json
{
  "transaction": {
    "id": 10,
    "user_id": 1,
    "title": "Groceries",
    "amount": 45.5,
    "type": "expense",
    "category": "Food",
    "created_at": "2026-06-14T12:00:00"
  }
}
```

Errors:

| Status | Meaning |
| ---: | --- |
| `401` | Missing or invalid bearer token |
| `404` | Transaction does not exist for current user |

### `POST /transactions`

Creates a transaction for the current user.

Request:

```json
{
  "title": "Salary",
  "amount": 5000,
  "type": "income",
  "category": "Job"
}
```

Validation:

- `title` is required.
- `category` is required.
- `amount` must be a number greater than zero.
- `type` must be `income` or `expense`.

Success response: `201`

```json
{
  "transaction": {
    "id": 11,
    "user_id": 1,
    "title": "Salary",
    "amount": 5000.0,
    "type": "income",
    "category": "Job",
    "created_at": "2026-06-14T12:00:00"
  }
}
```

### `PUT /transactions/<transaction_id>`

Updates a transaction owned by the current user.

Request body matches `POST /transactions`.

Success response: `200`

```json
{
  "transaction": {
    "id": 11,
    "user_id": 1,
    "title": "Salary",
    "amount": 5100.0,
    "type": "income",
    "category": "Job",
    "created_at": "2026-06-14T12:00:00"
  }
}
```

Errors:

| Status | Meaning |
| ---: | --- |
| `400` | Invalid transaction payload |
| `401` | Missing or invalid bearer token |
| `404` | Transaction does not exist for current user |

### `DELETE /transactions/<transaction_id>`

Deletes a transaction owned by the current user.

Success response: `200`

```json
{
  "message": "Transaction deleted."
}
```

Errors:

| Status | Meaning |
| ---: | --- |
| `401` | Missing or invalid bearer token |
| `404` | Transaction does not exist for current user |

## Manual API Smoke Test

Expose service ports temporarily only for local debugging. The default Compose file keeps them internal.

Inside the web-app container network, the browser-facing flow is the preferred smoke test:

```bash
docker compose up --build
python3 scripts/docker_tools.py health
```

For direct service testing, use `docker compose exec` and call services by their Compose names.
