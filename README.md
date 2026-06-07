# SpendWise

SpendWise is an intermediate-level full-stack personal finance tracker built with Flask, PostgreSQL, SQLAlchemy, Jinja templates, HTML, and CSS.

The app lets users create an account, log in, manage their own income and expense transactions, search and filter records, and view dashboard totals.

## Features

- User signup, login, and logout
- Session-based authentication
- Password hashing with Werkzeug
- User-specific transactions
- Protected dashboard route
- Create, read, update, and delete transactions
- Total income, total expense, and balance summaries
- Search by title or category
- Filter by all, income, or expense
- Flash messages for success and error feedback
- Professional responsive UI theme

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- Jinja2 templates
- HTML/CSS
- python-dotenv
- Werkzeug security helpers

## Project Structure

```text
expense-tracker/
  app.py
  requirements.txt
  README.md
  .env.example
  .gitignore
  Makefile
  docs/
    architecture.md
    environment-variables.md
    local-setup.md
    troubleshooting.md
  static/
    style.css
  templates/
    index.html
    login.html
    signup.html
```

Local-only files such as `.env`, `venv/`, and `__pycache__/` should not be committed.

## Quick Start

Run these commands from inside the `expense-tracker/` folder.

### 1. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 3. Create the PostgreSQL database

```bash
createdb expense_tracker_db
```

If `createdb` is not available, use `psql`:

```bash
psql -U postgres
```

Then run:

```sql
CREATE DATABASE expense_tracker_db;
```

### 4. Create `.env`

```bash
cp .env.example .env
```

Edit `.env` and set your real PostgreSQL password:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/expense_tracker_db
SECRET_KEY=change-this-to-a-long-random-secret
APP_ENV=development
APP_PORT=5000
LOG_LEVEL=INFO
REDIS_URL=
JWT_SECRET=change-this-if-you-add-jwt-auth
CORS_ORIGINS=http://127.0.0.1:5000,http://localhost:5000
```

### 5. Run the app

```bash
python3 app.py
```

Open:

```text
http://127.0.0.1:5000/
```

The login page is the home page. Create an account at `/signup`, then log in to access `/dashboard`.

## Commands

### Install

```bash
make install
```

### Run

```bash
make run
```

### Syntax check

```bash
make check
```

### Tests

```bash
make test
```

Automated tests are not added yet. `make test` currently runs the syntax check and confirms the app can be parsed by Python. Use the manual test flow in `docs/local-setup.md` for functional checks.

### Build

```bash
make build
```

There is no separate build artifact. This is a server-rendered Flask app with static CSS, so the build command documents that no build step is required.

## Documentation

- [Local setup](docs/local-setup.md)
- [Environment variables](docs/environment-variables.md)
- [Architecture](docs/architecture.md)
- [Troubleshooting](docs/troubleshooting.md)

## Main Routes

| Route | Purpose |
| --- | --- |
| `/` | Login page |
| `/login` | Login page |
| `/signup` | Create account |
| `/dashboard` | Protected SpendWise dashboard |
| `/delete/<transaction_id>` | Delete a transaction |
| `/logout` | End the current session |

## Database Models

### User

Stores account data:

- `id`
- `name`
- `email`
- `password_hash`
- `created_at`

### Transaction

Stores income and expense records:

- `id`
- `user_id`
- `title`
- `amount`
- `type`
- `category`
- `created_at`

## New Developer Checklist

Before opening a pull request or handing off the project:

- Dependencies install successfully.
- `.env` is created from `.env.example`.
- PostgreSQL database exists.
- `python3 app.py` starts the server.
- `/signup` creates a user.
- `/` logs in successfully.
- `/dashboard` creates, edits, deletes, searches, and filters transactions.
- `python3 -m py_compile app.py` passes.

## Notes

- `.env` contains secrets and must stay local.
- Existing old transactions without `user_id` may not show after login. This is expected because the app now shows only the logged-in user's transactions.
- `db.create_all()` is used for learning simplicity. A production app should use database migrations, such as Flask-Migrate.
