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

## Container Model

Each service has its own Dockerfile and should be built as a separate image.

| Service | Dockerfile | Image |
| --- | --- | --- |
| `auth-service` | `services/auth-service/Dockerfile` | `spendwise-auth-service` |
| `transaction-service` | `services/transaction-service/Dockerfile` | `spendwise-transaction-service` |
| `web-app` | `services/web-app/Dockerfile` | `spendwise-web-app` |

This keeps the Docker setup closer to real microservices practice: one service,
one image, one container.

The service Dockerfiles use production-friendly patterns:

- small `python:3.12-slim` base image
- multi-stage dependency build
- dependency wheel caching
- non-root runtime user
- runtime healthcheck
- no secrets baked into the image
- only service files copied into the image

Docker Compose starts all runtime containers together:

```text
web-app container
auth-service container
transaction-service container
postgres container
```

All containers join the explicit `spendwise-network` bridge network. The app
containers use service names like `postgres`, `auth-service`, and
`transaction-service` for internal communication.

The PostgreSQL container runs the SQL files in `database/init/` the first time
the database volume is created.

Redis is not part of the Compose stack yet because there is no current Redis
use case in the app.

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
- `timestamp` in UTC `Z` format
- `service`
- `request_id`
- `method`
- `path`
- `status_code`
- `duration_ms`

The same `request_id` is passed between services with the `X-Request-ID` header.
This makes it easier to trace one user request across the web app, auth service,
and transaction service.
