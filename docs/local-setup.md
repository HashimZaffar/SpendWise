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

## 5. Run Services

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

## 6. Verify Services

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

## 7. Manual App Test

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

## 8. Developer Check

```bash
make test
```
