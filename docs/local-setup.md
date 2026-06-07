# Local Setup

This guide explains how to run SpendWise locally with Python and PostgreSQL.

## Prerequisites

Install:

- Python 3.10 or newer
- PostgreSQL
- Git
- `pip`

Optional:

- pgAdmin
- VS Code

## 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Install Dependencies

```bash
make install
make install-services
```

## 3. Create Databases

```bash
createdb spendwise_auth_db
createdb spendwise_transaction_db
```

If `createdb` is not available:

```bash
psql -U postgres
```

Then:

```sql
CREATE DATABASE spendwise_auth_db;
CREATE DATABASE spendwise_transaction_db;
\q
```

## 4. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and set your real PostgreSQL password:

```env
AUTH_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/spendwise_auth_db
TRANSACTION_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/spendwise_transaction_db
AUTH_SERVICE_URL=http://127.0.0.1:5001
TRANSACTION_SERVICE_URL=http://127.0.0.1:5002
```

## 5. Start Services

Open three terminals inside `expense-tracker/`.

Terminal 1:

```bash
source venv/bin/activate
make run-auth
```

Terminal 2:

```bash
source venv/bin/activate
make run-transactions
```

Terminal 3:

```bash
source venv/bin/activate
make run-web
```

Open:

```text
http://127.0.0.1:5000/
```

## 6. Health Checks

```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/ready
curl http://127.0.0.1:5001/health
curl http://127.0.0.1:5001/ready
curl http://127.0.0.1:5002/health
curl http://127.0.0.1:5002/ready
```

## 7. Manual End-to-End Test Flow

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

## 8. Developer Checks

```bash
make test
make build
```
