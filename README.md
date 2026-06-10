# SpendWise

SpendWise is a Python full-stack personal finance app for tracking income, expenses, and balance. It is built as three local services so it can be used for practical DevOps learning around service startup, environment variables, databases, health checks, and logs.

## Contents

- [Purpose](#purpose)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Run Locally](#run-locally)
- [Run with Docker](#run-with-docker)
- [Tests](#tests)
- [Health and Readiness](#health-and-readiness)
- [Structured Logging](#structured-logging)
- [Automation Scripts](#automation-scripts)
- [Makefile Commands](#makefile-commands)
- [Troubleshooting](#troubleshooting)

## Purpose

SpendWise helps users:

- create an account
- log in securely
- add income and expense transactions
- edit and delete transactions
- search and filter transactions
- view total income, total expense, and balance

For DevOps practice, this app includes:

- multiple services
- PostgreSQL databases
- environment-based configuration
- dependency files
- startup commands
- health and readiness endpoints
- structured JSON logs

## Architecture

SpendWise has three services.

| Service | Default Port | Responsibility |
| --- | --- | --- |
| `web-app` | `5000` | Browser UI, form handling, sessions, CSRF protection |
| `auth-service` | `5001` | Signup, login, password hashing, JWT token creation |
| `transaction-service` | `5002` | Transaction CRUD, search, filters, summary totals |

Request flow:

```text
Browser
  -> web-app
  -> auth-service
  -> transaction-service
  -> PostgreSQL
```

The `web-app` does not directly manage users or transactions. It calls the backend services over HTTP.

## Tech Stack

| Area | Technology |
| --- | --- |
| Language | Python |
| Web framework | Flask |
| Frontend rendering | Jinja2 templates |
| Styling | CSS |
| Database | PostgreSQL |
| ORM | Flask-SQLAlchemy |
| Auth tokens | PyJWT |
| Password hashing | Werkzeug |
| HTTP client | requests |
| Environment loading | python-dotenv |
| Production WSGI server | Gunicorn |
| Container image | Docker |
| Local orchestration | Docker Compose |

## Project Structure

```text
expense-tracker/
  README.md
  .env.example
  .dockerignore
  .gitignore
  docker-compose.yml
  Makefile
  requirements.txt
  database/
    init/
      01-create-spendwise-databases.sql
  docs/
    local-setup.md
    environment-variables.md
    architecture.md
    troubleshooting.md
  scripts/
    check_env.py
    project_audit.py
    run_local.py
  services/
    auth-service/
      Dockerfile
      app.py
      requirements.txt
    transaction-service/
      Dockerfile
      app.py
      requirements.txt
    web-app/
      Dockerfile
      app.py
      requirements.txt
      templates/
      static/
```

## Prerequisites

Install these before running the app:

- Python 3.10 or newer
- PostgreSQL
- Git
- `make`

Check PostgreSQL:

```bash
pg_isready -h localhost -p 5432
```

If PostgreSQL is not running on Ubuntu:

```bash
sudo pg_ctlcluster 16 main start
```

## Installation

From inside the `expense-tracker/` folder:

```bash
python3 -m venv venv
source venv/bin/activate
make install
make install-services
```

What these commands do:

| Command | Purpose |
| --- | --- |
| `python3 -m venv venv` | creates a Python virtual environment |
| `source venv/bin/activate` | activates the virtual environment |
| `make install` | installs root dependencies |
| `make install-services` | installs dependencies for all services |

## Environment Configuration

Create a local `.env` file:

```bash
cp .env.example .env
```

Update the database URLs in `.env` with your PostgreSQL password:

```env
AUTH_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/spendwise_auth_db
TRANSACTION_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/spendwise_transaction_db
```

Important variables:

| Variable | Purpose |
| --- | --- |
| `APP_ENV` | app environment, for example `development` |
| `LOG_LEVEL` | logging level, for example `INFO` |
| `SECRET_KEY` | protects Flask browser sessions |
| `JWT_SECRET` | signs and verifies JWT tokens |
| `AUTH_DATABASE_URL` | PostgreSQL URL for auth data |
| `TRANSACTION_DATABASE_URL` | PostgreSQL URL for transaction data |
| `AUTH_SERVICE_URL` | URL used by `web-app` to call `auth-service` |
| `TRANSACTION_SERVICE_URL` | URL used by `web-app` to call `transaction-service` |
| `WEB_APP_PORT` | web app port |
| `AUTH_SERVICE_PORT` | auth service port |
| `TRANSACTION_SERVICE_PORT` | transaction service port |

More detail is available in [docs/environment-variables.md](docs/environment-variables.md).

## Database Setup

Create both PostgreSQL databases:

```bash
createdb -U postgres -h localhost spendwise_auth_db
createdb -U postgres -h localhost spendwise_transaction_db
```

When PostgreSQL asks for a password, use the same password configured in `.env`.

## Run Locally

Option 1: run all services with the automation script:

```bash
make run-local
```

This command checks the project structure, validates `.env`, starts the services
in the correct order, and stops all services when you press `Ctrl+C`.

Option 2: run each service in a separate terminal.

Terminal 1:

```bash
cd "/home/hashim/DevOps projects/full-stack-basic-project/expense-tracker"
source venv/bin/activate
make run-auth
```

Terminal 2:

```bash
cd "/home/hashim/DevOps projects/full-stack-basic-project/expense-tracker"
source venv/bin/activate
make run-transactions
```

Terminal 3:

```bash
cd "/home/hashim/DevOps projects/full-stack-basic-project/expense-tracker"
source venv/bin/activate
make run-web
```

Open the app:

```text
http://127.0.0.1:5000/
```

## Run with Docker

Recommended Docker option:

```bash
docker compose up --build
```

Open:

```text
http://127.0.0.1:5000/
```

Docker Compose starts:

| Container | Purpose | Port |
| --- | --- | --- |
| `spendwise-postgres` | PostgreSQL database | host `5433` -> container `5432` |
| `spendwise-auth-service` | auth API | `5001` |
| `spendwise-transaction-service` | transaction API | `5002` |
| `spendwise-web-app` | browser app | `5000` |

Compose also includes:

- explicit `spendwise-network` bridge network
- persistent PostgreSQL volume
- health checks for every runtime service
- `restart: unless-stopped`
- `.env` variable support with safe local defaults

Redis is not included because SpendWise does not currently use caching,
background jobs, or Redis-backed sessions.

The PostgreSQL container automatically creates:

- `spendwise_auth_db`
- `spendwise_transaction_db`
- `users` table
- `transactions` table

Stop containers:

```bash
docker compose down
```

SpendWise also supports manual image builds. It uses one Docker image per service.

Each service Dockerfile is production-oriented:

- uses `python:3.12-slim`
- uses a multi-stage build
- builds dependency wheels before copying app code
- runs as a non-root user
- includes a container healthcheck
- keeps secrets out of the image
- copies only the files needed by that service

Build all service images:

```bash
make docker-build
```

Or build them one by one:

```bash
docker build -t spendwise-auth-service -f services/auth-service/Dockerfile .
docker build -t spendwise-transaction-service -f services/transaction-service/Dockerfile .
docker build -t spendwise-web-app -f services/web-app/Dockerfile .
```

Run each service manually in a separate terminal:

```bash
make docker-run-auth
make docker-run-transactions
make docker-run-web
```

Open:

```text
http://127.0.0.1:5000/
```

The Docker images map to services like this:

| Service | Image | Dockerfile | Port |
| --- | --- | --- | --- |
| `auth-service` | `spendwise-auth-service` | `services/auth-service/Dockerfile` | `5001` |
| `transaction-service` | `spendwise-transaction-service` | `services/transaction-service/Dockerfile` | `5002` |
| `web-app` | `spendwise-web-app` | `services/web-app/Dockerfile` | `5000` |

The manual Docker run commands use:

```bash
--network host --env-file .env
```

This is simple for local Linux development because containers can use the same
`localhost` PostgreSQL URLs from `.env`.

Manual examples:

```bash
docker run --rm --network host --env-file .env spendwise-auth-service
docker run --rm --network host --env-file .env spendwise-transaction-service
docker run --rm --network host --env-file .env spendwise-web-app
```

For manual `docker run`, PostgreSQL is still external. For Compose, PostgreSQL
runs as a container.

## Tests

Run:

```bash
make test
```

Current test behavior:

- compiles `services/auth-service/app.py`
- compiles `services/transaction-service/app.py`
- compiles `services/web-app/app.py`

Automated functional tests are not added yet.

## Health and Readiness

Each service exposes two operational endpoints:

| Endpoint | Meaning |
| --- | --- |
| `/health` | service process is alive |
| `/ready` | service dependencies are reachable |

Check all services:

```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/ready
curl http://127.0.0.1:5001/health
curl http://127.0.0.1:5001/ready
curl http://127.0.0.1:5002/health
curl http://127.0.0.1:5002/ready
```

A healthy readiness response includes:

```json
{
  "status": "ready"
}
```

## Manual App Test Flow

After all services are running:

1. Open `http://127.0.0.1:5000/signup`.
2. Create a user account.
3. Log in at `http://127.0.0.1:5000/`.
4. Add an income transaction.
5. Add an expense transaction.
6. Check total income, total expense, and balance.
7. Search transactions.
8. Filter by income and expense.
9. Edit a transaction.
10. Delete a transaction.
11. Log out.

## Structured Logging

All services write structured JSON logs to stdout.

Example:

```json
{
  "level": "info",
  "message": "Request completed",
  "timestamp": "2026-06-09T10:00:00Z",
  "service": "web-app",
  "request_id": "abc123",
  "method": "GET",
  "path": "/ready",
  "status_code": 200,
  "duration_ms": 12.5
}
```

Every response includes:

```text
X-Request-ID
```

This helps trace a request across services.

## Automation Scripts

SpendWise includes small Python automation scripts for DevOps practice.

| Script | Purpose |
| --- | --- |
| `scripts/check_env.py` | checks required `.env` variables and validates common values |
| `scripts/project_audit.py` | checks that important project files and folders exist |
| `scripts/run_local.py` | runs audit checks, validates env, then starts services in order |

Run them directly:

```bash
python scripts/check_env.py
python scripts/project_audit.py
python scripts/run_local.py
```

Or use Makefile shortcuts:

```bash
make check-env
make audit
make run-local
```

## Makefile Commands

| Command | Purpose |
| --- | --- |
| `make install` | install root dependencies |
| `make install-services` | install dependencies for all services |
| `make check-env` | validate required environment variables |
| `make audit` | verify important project files and folders |
| `make run-local` | start all local services in the correct order |
| `make run-auth` | start auth service |
| `make run-transactions` | start transaction service |
| `make run-web` | start web app |
| `make docker-build` | build all service Docker images |
| `make docker-build-auth` | build auth service image |
| `make docker-build-transactions` | build transaction service image |
| `make docker-build-web` | build web app image |
| `make docker-run-auth` | run auth service container |
| `make docker-run-transactions` | run transaction service container |
| `make docker-run-web` | run web app container |
| `make compose-config` | validate Docker Compose configuration |
| `make compose-up` | build and start all Compose services |
| `make compose-down` | stop Compose services |
| `make compose-logs` | follow Compose service logs |
| `make compose-ps` | show Compose service status |
| `make prod-auth` | start auth service with Gunicorn |
| `make prod-transactions` | start transaction service with Gunicorn |
| `make prod-web` | start web app with Gunicorn |
| `make test` | run current checks |
| `make build` | confirm no build step is required |

## Troubleshooting

### PostgreSQL is not running

Symptom:

```text
localhost:5432 - no response
connection refused
```

Fix:

```bash
sudo pg_ctlcluster 16 main start
pg_isready -h localhost -p 5432
```

Expected:

```text
localhost:5432 - accepting connections
```

### Database does not exist

Symptom:

```text
database "spendwise_auth_db" does not exist
database "spendwise_transaction_db" does not exist
```

Fix:

```bash
createdb -U postgres -h localhost spendwise_auth_db
createdb -U postgres -h localhost spendwise_transaction_db
```

### Wrong database password

Symptom:

```text
password authentication failed for user "postgres"
```

Fix:

Update `.env` with the correct PostgreSQL password:

```env
AUTH_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/spendwise_auth_db
TRANSACTION_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/spendwise_transaction_db
```

### Port already in use

Symptom:

```text
Address already in use
```

Fix:

Stop the old process using the port, or change the port values in `.env`:

```env
WEB_APP_PORT=5000
AUTH_SERVICE_PORT=5001
TRANSACTION_SERVICE_PORT=5002
```

### Web app opens but dashboard does not work

Check backend services:

```bash
curl http://127.0.0.1:5001/ready
curl http://127.0.0.1:5002/ready
```

Both should return `ready`.

## Additional Documentation

- [Local setup](docs/local-setup.md)
- [Environment variables](docs/environment-variables.md)
- [Architecture](docs/architecture.md)
- [Troubleshooting](docs/troubleshooting.md)
