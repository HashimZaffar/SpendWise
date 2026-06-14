# Architecture

SpendWise is a small service-oriented Flask application. The browser UI is intentionally separate from the authentication and transaction APIs so each responsibility stays narrow and each service can be built, scanned, and operated independently.

## Runtime Topology

```text
Browser
  |
  | HTTP forms and session cookie
  v
web-app :5000
  | \
  |  \ JSON over Docker network
  |   \
  v    v
auth-service :5001       transaction-service :5002
  |                       |
  v                       v
spendwise_auth_db         spendwise_transaction_db
  \                       /
   \                     /
        postgres :5432
```

Docker Compose publishes only the web app to the host by default:

```text
http://localhost:8000
```

The auth and transaction APIs are reachable by service name inside the Compose network.

## Service Responsibilities

### `web-app`

The web app owns browser-facing behavior:

- Renders login, signup, and dashboard pages with Jinja templates.
- Stores the logged-in user and access token in the Flask session.
- Adds CSRF tokens to browser forms and validates them on POST requests.
- Calls `auth-service` for login and signup.
- Calls `transaction-service` for dashboard data and transaction changes.
- Exposes `/health` and `/ready`.

Important files:

- `services/web-app/app.py`
- `services/web-app/templates/`
- `services/web-app/static/style.css`

### `auth-service`

The auth service owns identities and token issuance:

- Creates users.
- Stores password hashes.
- Validates login credentials.
- Issues HS256 JWT access tokens.
- Looks up the current user from a bearer token.
- Exposes `/health` and `/ready`.

Important files:

- `services/auth-service/app.py`
- `services/auth-service/requirements.txt`

### `transaction-service`

The transaction service owns per-user financial records:

- Requires a valid bearer token for transaction routes.
- Creates, reads, updates, and deletes transactions.
- Filters by transaction type.
- Searches title and category.
- Returns all-time income, expense, and balance summaries.
- Returns chart-ready dashboard data.
- Exposes `/health` and `/ready`.

Important files:

- `services/transaction-service/app.py`
- `services/transaction-service/requirements.txt`

### `postgres`

PostgreSQL stores the app data in two databases:

- `spendwise_auth_db`
- `spendwise_transaction_db`

The initialization script creates the databases, tables, and indexes:

- `database/init/01-create-spendwise-databases.sql`

## Data Model

### `users`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `SERIAL PRIMARY KEY` | User identifier used as the JWT subject |
| `name` | `VARCHAR(100)` | Display name |
| `email` | `VARCHAR(120)` | Unique, indexed login email |
| `password_hash` | `VARCHAR(255)` | Werkzeug-generated password hash |
| `created_at` | `TIMESTAMP` | Defaults to current timestamp |

### `transactions`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | `SERIAL PRIMARY KEY` | Transaction identifier |
| `user_id` | `INTEGER` | JWT subject owner; indexed |
| `title` | `VARCHAR(100)` | Human-readable title |
| `amount` | `DOUBLE PRECISION` | Must be greater than zero |
| `type` | `VARCHAR(20)` | `income` or `expense` |
| `category` | `VARCHAR(50)` | User-provided category |
| `created_at` | `TIMESTAMP` | Defaults to current timestamp |

## Request Flow

### Login

1. The browser posts the login form to `web-app`.
2. `web-app` validates the CSRF token.
3. `web-app` sends JSON credentials to `auth-service`.
4. `auth-service` validates the password hash.
5. `auth-service` returns a JWT and serialized user.
6. `web-app` stores the JWT and user in the Flask session.
7. The browser is redirected to `/dashboard`.

### Dashboard Load

1. The browser requests `/dashboard`.
2. `web-app` sends the session JWT as a bearer token to `transaction-service`.
3. `transaction-service` validates the JWT and issuer.
4. `transaction-service` returns transactions, summary totals, selected filters, search text, and chart data.
5. `web-app` renders the dashboard.

### Transaction Change

1. The browser submits a transaction form or delete form.
2. `web-app` validates the CSRF token.
3. `web-app` forwards the operation to `transaction-service` with the bearer token.
4. `transaction-service` validates ownership by filtering records with both `id` and `user_id`.
5. `web-app` flashes a result message and redirects back to `/dashboard`.

## Security Boundaries

- Browser clients do not call backend service containers directly in the local Compose setup.
- Browser form POSTs are CSRF-protected by `web-app`.
- Transaction data is isolated by the JWT subject.
- Passwords are stored as hashes only.
- Request IDs are propagated through service calls for traceability.
- Session cookie settings are configurable through environment variables.

See [Security](SECURITY.md) for hardening guidance.

## Containers

Each app service image:

- Uses `python:3.12-slim`.
- Builds wheels in a separate builder stage.
- Runs as a non-root `appuser`.
- Exposes only the container port required by that service.
- Defines a service-local health check.

The Compose file adds service dependencies and readiness health checks so the web app starts after its backend dependencies are healthy.
