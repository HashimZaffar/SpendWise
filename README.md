# SpendWise

SpendWise is a microservices-based full-stack personal finance app built with Flask, PostgreSQL, Jinja templates, and CSS.

The app lets users create an account, log in, manage income and expense transactions, search/filter records, and view dashboard totals.

## Architecture

SpendWise is split into three Python services:

| Service | Port | Responsibility |
| --- | --- | --- |
| `web-app` | `5000` | Server-rendered frontend, sessions, CSRF, calls backend APIs |
| `auth-service` | `5001` | Signup, login, user lookup, JWT issuing |
| `transaction-service` | `5002` | Transaction CRUD, search/filter, summary totals |

Each backend service owns its own PostgreSQL database:

| Database | Owner |
| --- | --- |
| `spendwise_auth_db` | `auth-service` |
| `spendwise_transaction_db` | `transaction-service` |

The old `app.py` monolith is kept as a learning reference, but the main microservices app is under `services/`.

## Features

- Microservices folder structure
- Separate auth and transaction databases
- JWT-based service authentication
- Server-rendered frontend
- CSRF protection for browser forms
- Secure session cookie configuration
- Health and readiness endpoints for every service
- Structured JSON logs with request IDs
- Professional responsive UI theme
- Developer-friendly Makefile commands

## Project Structure

```text
expense-tracker/
  app.py                         # legacy monolith reference
  Makefile
  README.md
  .env.example
  docs/
    architecture.md
    deployment.md
    environment-variables.md
    local-setup.md
    microservices.md
    troubleshooting.md
  services/
    auth-service/
      app.py
      requirements.txt
    transaction-service/
      app.py
      requirements.txt
    web-app/
      app.py
      requirements.txt
      templates/
      static/
```

## Quick Start

Run from inside `expense-tracker/`:

```bash
python3 -m venv venv
source venv/bin/activate
make install
make install-services
cp .env.example .env
```

Create local PostgreSQL databases:

```bash
createdb spendwise_auth_db
createdb spendwise_transaction_db
```

Start each service in a separate terminal:

```bash
make run-auth
```

```bash
make run-transactions
```

```bash
make run-web
```

Open:

```text
http://127.0.0.1:5000/
```

## Health Checks

```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/ready
curl http://127.0.0.1:5001/health
curl http://127.0.0.1:5001/ready
curl http://127.0.0.1:5002/health
curl http://127.0.0.1:5002/ready
```

## Useful Commands

```bash
make install
make install-services
make test
make run-auth
make run-transactions
make run-web
make prod-auth
make prod-transactions
make prod-web
```

## Documentation

- [Local setup](docs/local-setup.md)
- [Environment variables](docs/environment-variables.md)
- [Architecture](docs/architecture.md)
- [Microservices](docs/microservices.md)
- [Deployment](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)

## Production Notes

- Use strong `SECRET_KEY` and `JWT_SECRET` values.
- Keep `.env` out of Git.
- Use HTTPS and `SESSION_COOKIE_SECURE=true`.
- Add database migrations before real production deployment.
- Add automated API tests and frontend flow tests before real production deployment.
