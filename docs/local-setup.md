# Local Setup

This guide explains how to clone, configure, and run SpendWise locally.

## Prerequisites

Install these before starting:

- Python 3.10 or newer
- PostgreSQL
- Git
- `pip`

Optional but useful:

- pgAdmin
- VS Code

## 1. Clone the Repository

```bash
git clone REPLACE_WITH_YOUR_REPOSITORY_URL
cd expense-tracker
```

If the repository is already cloned, open the project folder:

```bash
cd expense-tracker
```

## 2. Create a Virtual Environment

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal.

## 3. Install Dependencies

```bash
make install
```

## 4. Create the Database

Recommended command:

```bash
createdb expense_tracker_db
```

Alternative with `psql`:

```bash
psql -U postgres
```

Then:

```sql
CREATE DATABASE expense_tracker_db;
```

Exit `psql`:

```sql
\q
```

## 5. Create Environment File

Copy the example file:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/expense_tracker_db
SECRET_KEY=change-this-to-a-long-random-secret
```

Replace `your_password` with your PostgreSQL password.

## 6. Run the App

```bash
make run
```

Open:

```text
http://127.0.0.1:5000/
```

## 7. Manual Test Flow

Use this flow to confirm the app works:

1. Open `/signup`.
2. Create a new account.
3. Login at `/`.
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

Run a Python syntax check:

```bash
make check
```

Run the current test command:

```bash
make test
```

Run the build command:

```bash
make build
```

There is no build artifact because this is a server-rendered Flask app.

Automated tests are not available yet.
