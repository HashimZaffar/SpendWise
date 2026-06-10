# Local Setup

This guide explains how to run SpendWise locally with Python and PostgreSQL.

## Prerequisites

Install:

- Python 3.10 or newer
- PostgreSQL
- Git
- `make`

Check PostgreSQL:

```bash
pg_isready -h localhost -p 5432
```

If PostgreSQL is down on Ubuntu:

```bash
sudo pg_ctlcluster 16 main start
```

## 1. Create Virtual Environment

From inside `expense-tracker/`:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Install Dependencies

```bash
make install
make install-services
```

## 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set your local PostgreSQL password:

```env
AUTH_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/spendwise_auth_db
TRANSACTION_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/spendwise_transaction_db
```

## 4. Create Databases

```bash
createdb -U postgres -h localhost spendwise_auth_db
createdb -U postgres -h localhost spendwise_transaction_db
```

Use the same PostgreSQL password that you configured in `.env`.

## 5. Run Preflight Checks

Before starting the app, check the environment and project structure:

```bash
make check-env
make audit
```

What these commands do:

| Command | Purpose |
| --- | --- |
| `make check-env` | checks required `.env` variables |
| `make audit` | checks that important files and folders exist |

## 6. Run Services

Recommended option:

```bash
make run-local
```

This starts services in this order:

1. `auth-service`
2. `transaction-service`
3. `web-app`

It also stops all services when you press `Ctrl+C`.

Manual option:

Open three terminals.

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

Open:

```text
http://127.0.0.1:5000/
```

## 7. Verify Services

```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/ready
curl http://127.0.0.1:5001/health
curl http://127.0.0.1:5001/ready
curl http://127.0.0.1:5002/health
curl http://127.0.0.1:5002/ready
```

All readiness endpoints should return:

```json
{
  "status": "ready"
}
```

## 8. Manual App Test

1. Open `/signup`.
2. Create a user.
3. Login.
4. Add an income transaction.
5. Add an expense transaction.
6. Check dashboard totals.
7. Search and filter transactions.
8. Edit a transaction.
9. Delete a transaction.
10. Logout.

## 9. Developer Check

```bash
make test
```

## 10. Docker Compose Test

Start the full stack with Docker Compose:

```bash
docker compose up --build
```

Open the app:

```text
http://127.0.0.1:5000/
```

Docker Compose starts:

- `postgres`
- `auth-service`
- `transaction-service`
- `web-app`

It also creates:

- `spendwise-network`
- `spendwise_postgres_data` volume
- health checks for the app and database containers

It also initializes:

- `spendwise_auth_db`
- `spendwise_transaction_db`
- `users` table
- `transactions` table

Check services:

```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/ready
curl http://127.0.0.1:5001/ready
curl http://127.0.0.1:5002/ready
```

Stop everything:

```bash
docker compose down
```

## 11. Manual Docker Image Test

Build all service images:

```bash
make docker-build
```

Run each service in a separate terminal:

```bash
make docker-run-auth
make docker-run-transactions
make docker-run-web
```

The Docker run commands use `--network host --env-file .env`. This keeps the
setup simple on Linux because the containers can reach PostgreSQL on
`localhost:5432` using the same database URLs from `.env`.

Manual Docker run examples:

```bash
docker run --rm --network host --env-file .env spendwise-auth-service
docker run --rm --network host --env-file .env spendwise-transaction-service
docker run --rm --network host --env-file .env spendwise-web-app
```

For `/ready`, login, and transaction testing, PostgreSQL must be running and the
two SpendWise databases must exist.
