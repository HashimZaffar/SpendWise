# SpendWise

SpendWise is a microservices-based full-stack personal finance app built with Flask, PostgreSQL, Docker Compose, Jinja templates, and CSS.

The app lets users create an account, log in, manage income and expense transactions, search/filter records, and view dashboard totals.

## Architecture

SpendWise is now split into three services:

| Service | Port | Responsibility |
| --- | --- | --- |
| `web-app` | `5000` | Server-rendered frontend, sessions, CSRF, calls backend APIs |
| `auth-service` | `5001` | Signup, login, user lookup, JWT issuing |
| `transaction-service` | `5002` | Transaction CRUD, search/filter, summary totals |

Each backend service owns its own database:

| Database | Owner |
| --- | --- |
| `spendwise_auth_db` | `auth-service` |
| `spendwise_transaction_db` | `transaction-service` |

The old `app.py` monolith is kept as a learning reference, but the main architecture is now under `services/`.

## Features

- Microservices folder structure
- Docker Compose orchestration
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
  docker-compose.yml
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
      Dockerfile
      requirements.txt
    transaction-service/
      app.py
      Dockerfile
      requirements.txt
    web-app/
      app.py
      Dockerfile
      requirements.txt
      templates/
      static/
```

## Quick Start With Docker

Run from inside `expense-tracker/`:

```bash
cp .env.example .env
make compose-up
```

Open:

```text
http://127.0.0.1:5000/
```

Then:

1. Create an account at `/signup`.
2. Login at `/`.
3. Add income and expense transactions.
4. Search, filter, edit, and delete transactions.

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
make test
make compose-build
make compose-up
make compose-ps
make compose-logs
make compose-down
```

For non-Docker local service runs:

```bash
make run-auth
make run-transactions
make run-web
```

Run each command in a separate terminal.

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
