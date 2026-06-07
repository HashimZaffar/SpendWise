# Architecture

SpendWise uses a microservices architecture with a server-rendered frontend.

## High-Level Flow

```text
Browser
  -> web-app
  -> auth-service for signup/login/user identity
  -> transaction-service for transaction CRUD and summaries
  -> separate PostgreSQL databases
```

## Services

| Service | Purpose |
| --- | --- |
| `web-app` | Renders HTML, manages browser session, protects forms with CSRF, calls backend services |
| `auth-service` | Owns users, password hashes, login, JWT issuing, `/me` user lookup |
| `transaction-service` | Owns transaction records, validates JWTs, calculates dashboard summaries |

## Data Ownership

Each service owns its data. This is one of the most important microservices rules.

```text
auth-service
  -> spendwise_auth_db
  -> users table

transaction-service
  -> spendwise_transaction_db
  -> transactions table
```

The `web-app` does not directly connect to the databases. It talks to backend services over HTTP.

## Authentication Flow

```text
Browser submits login form
  -> web-app sends email/password to auth-service
  -> auth-service validates password
  -> auth-service returns JWT
  -> web-app stores JWT in Flask session
  -> web-app sends JWT to transaction-service for protected requests
```

## Transaction Flow

```text
Browser submits transaction form
  -> web-app validates CSRF
  -> web-app sends JSON request to transaction-service
  -> transaction-service validates JWT
  -> transaction-service creates/updates/deletes transaction
  -> web-app redirects back to dashboard
```

## Health and Readiness

Every service exposes:

```text
/health
/ready
```

`/health` means the process is alive.

`/ready` means the service can reach the dependencies it needs for traffic.

## Structured Logging

Each service writes JSON logs to stdout with:

- `level`
- `message`
- `timestamp`
- `service`
- `request_id`
- `method`
- `path`
- `status_code`
- `duration_ms`

## Current Limitations

- Database migrations are not implemented yet.
- Automated tests are still minimal.
- There is no API gateway yet.
- Service URLs are configured through environment variables.
