# Local Setup

This guide explains how to run SpendWise as a microservices app.

## Prerequisites

Install:

- Git
- Docker
- Docker Compose

Optional for non-Docker development:

- Python 3.10 or newer
- PostgreSQL
- `pip`

## Recommended Setup: Docker Compose

From inside `expense-tracker/`:

```bash
cp .env.example .env
make compose-up
```

Open:

```text
http://127.0.0.1:5000/
```

Docker Compose starts:

- `web-app`
- `auth-service`
- `transaction-service`
- `auth-db`
- `transaction-db`
- `redis`

## Health Checks

Run in a new terminal:

```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/ready
curl http://127.0.0.1:5001/health
curl http://127.0.0.1:5001/ready
curl http://127.0.0.1:5002/health
curl http://127.0.0.1:5002/ready
```

## Manual End-to-End Test Flow

1. Open `http://127.0.0.1:5000/signup`.
2. Create a new account.
3. Login at `http://127.0.0.1:5000/`.
4. Add an income transaction.
5. Add an expense transaction.
6. Confirm dashboard totals update.
7. Search by title or category.
8. Filter by income and expense.
9. Edit a transaction.
10. Delete a transaction.
11. Logout.
12. Confirm `/dashboard` redirects to login when logged out.

## Useful Docker Commands

```bash
make compose-ps
make compose-logs
make compose-down
```

## Non-Docker Development

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
make install
make install-services
```

Create local databases:

```bash
createdb spendwise_auth_db
createdb spendwise_transaction_db
```

Copy the environment file:

```bash
cp .env.example .env
```

Edit `.env` and set:

```env
AUTH_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/spendwise_auth_db
TRANSACTION_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/spendwise_transaction_db
AUTH_SERVICE_URL=http://127.0.0.1:5001
TRANSACTION_SERVICE_URL=http://127.0.0.1:5002
```

Run each service in a separate terminal:

```bash
make run-auth
make run-transactions
make run-web
```

Open:

```text
http://127.0.0.1:5000/
```

## Developer Checks

```bash
make test
make build
```

Automated tests are not fully implemented yet. `make test` currently checks Python syntax and import safety.
