# Architecture

SpendWise is a local Python microservices-style full-stack app.

## Services

| Service | Port | Responsibility |
| --- | --- | --- |
| `web-app` | `5000` | Browser UI, sessions, forms, CSRF, calls backend services |
| `auth-service` | `5001` | Signup, login, password hashing, JWT creation |
| `transaction-service` | `5002` | Transaction CRUD, search, filters, summary totals |

## Request Flow

```text
Browser
  -> web-app
  -> auth-service
  -> transaction-service
  -> PostgreSQL
```

The browser talks to `web-app`.

The `web-app` talks to backend services over HTTP.

The backend services talk to PostgreSQL.

## Data Ownership

| Service | Database | Data |
| --- | --- | --- |
| `auth-service` | `spendwise_auth_db` | users and password hashes |
| `transaction-service` | `spendwise_transaction_db` | income and expense transactions |

The `web-app` does not directly connect to PostgreSQL.

## Authentication Flow

```text
User submits login form
  -> web-app sends email/password to auth-service
  -> auth-service verifies password
  -> auth-service returns JWT
  -> web-app stores JWT in session
  -> web-app sends JWT to transaction-service
```

## Transaction Flow

```text
User submits transaction form
  -> web-app validates CSRF token
  -> web-app sends request to transaction-service
  -> transaction-service validates JWT
  -> transaction-service saves or updates data
  -> web-app renders dashboard
```

## Health and Readiness

Each service has:

```text
/health
/ready
```

`/health` means the service process is alive.

`/ready` means the service can reach its required dependencies.

## Logging

All services write structured JSON logs with:

- `level`
- `message`
- `timestamp`
- `service`
- `request_id`
- `method`
- `path`
- `status_code`
- `duration_ms`
