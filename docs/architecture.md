# Architecture

SpendWise is a server-rendered Flask application.

It uses:

- Flask for routing and request handling
- Jinja templates for HTML rendering
- PostgreSQL for persistent data
- SQLAlchemy as the ORM
- Flask sessions for login state
- Werkzeug for password hashing
- Environment variables for runtime configuration
- JSON logs for request and application events
- CSRF tokens for POST form protection

## High-Level Flow

```text
Browser
  -> Flask route in app.py
  -> SQLAlchemy model/query
  -> PostgreSQL database
  -> Flask renders Jinja template
  -> HTML/CSS response in browser
```

## Main Files

```text
app.py
templates/
  login.html
  signup.html
  index.html
static/
  style.css
```

## `app.py`

`app.py` contains the application setup, database models, and routes.

Responsibilities:

- Load environment variables
- Configure Flask
- Configure SQLAlchemy
- Define `User` and `Transaction` models
- Create database tables for local development
- Handle authentication
- Protect dashboard routes
- Handle transaction CRUD
- Handle search and filters

## Models

### User

Represents an account.

Relationship:

```text
One User -> Many Transactions
```

Important fields:

- `email` is unique.
- `password_hash` stores the hashed password.

### Transaction

Represents an income or expense record.

Important fields:

- `user_id` links a transaction to a user.
- `type` is either `income` or `expense`.
- `amount` stores the money value.

## Authentication Flow

### Signup

```text
User submits signup form
  -> validate fields
  -> check duplicate email
  -> hash password
  -> save user
  -> redirect to login
```

### Login

```text
User submits login form
  -> find user by email
  -> verify password hash
  -> store user_id in session
  -> redirect to dashboard
```

### Logout

```text
User opens /logout
  -> remove user_id from session
  -> redirect to login
```

## Dashboard Flow

The dashboard is protected by `login_required`.

```text
Request /dashboard
  -> check session
  -> get current user
  -> query only that user's transactions
  -> apply filter/search
  -> calculate totals
  -> render dashboard
```

## Health and Readiness

SpendWise exposes two operational endpoints:

```text
/health
/ready
```

### `/health`

Liveness check.

Purpose:

```text
Confirms the Flask process is running.
```

It does not check database connectivity.

### `/ready`

Readiness check.

Purpose:

```text
Confirms the app can connect to required dependencies before receiving traffic.
```

Current checks:

- PostgreSQL database connection
- Redis connectivity, if `REDIS_URL` is set

## Structured Logging

SpendWise writes JSON logs to stdout.

Example:

```json
{
  "level": "info",
  "message": "User login successful",
  "timestamp": "2026-06-07T10:00:00+00:00",
  "request_id": "abc123",
  "user_id": 1
}
```

Every response includes:

```text
X-Request-ID
```

If the request includes an `X-Request-ID` header, SpendWise reuses it. Otherwise, it generates a new request id.

## Data Access Rules

Every transaction query is scoped by:

```python
user_id=current_user.id
```

This prevents one user from viewing, editing, or deleting another user's transactions.

## Styling

All styling lives in:

```text
static/style.css
```

The CSS uses theme variables in `:root` for consistent colors, borders, shadows, and surfaces.

## Current Limitations

- No automated tests yet.
- No database migrations yet.
- No pagination yet.
- Local table creation is available through `initialize_local_database()` / `make init-db` and is skipped in production.
