# Deployment

This guide describes the production deployment shape for SpendWise with separately managed Python services.

## Production Services

Run these services separately:

```text
web-app
auth-service
transaction-service
```

Each service can run as a systemd service, process manager service, or platform web process.

## Gunicorn Commands

From the project root:

```bash
make prod-auth
make prod-transactions
make prod-web
```

In production, run each command as a separate managed process.

## Required Environment Variables

Common:

```env
APP_ENV=production
LOG_LEVEL=INFO
SECRET_KEY=replace-with-a-long-random-secret
JWT_SECRET=replace-with-a-different-long-random-secret
```

`web-app`:

```env
WEB_APP_PORT=5000
AUTH_SERVICE_URL=http://127.0.0.1:5001
TRANSACTION_SERVICE_URL=http://127.0.0.1:5002
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

`auth-service`:

```env
AUTH_SERVICE_PORT=5001
AUTH_DATABASE_URL=postgresql://user:password@host:5432/spendwise_auth_db
JWT_EXPIRES_MINUTES=120
```

`transaction-service`:

```env
TRANSACTION_SERVICE_PORT=5002
TRANSACTION_DATABASE_URL=postgresql://user:password@host:5432/spendwise_transaction_db
```

## Health Checks

Use `/health` for liveness:

```text
http://127.0.0.1:5000/health
http://127.0.0.1:5001/health
http://127.0.0.1:5002/health
```

Use `/ready` for readiness:

```text
http://127.0.0.1:5000/ready
http://127.0.0.1:5001/ready
http://127.0.0.1:5002/ready
```

## Database

Development startup creates tables automatically for learning convenience.

Before real production deployment, add migrations:

```text
Flask-Migrate / Alembic
```

Production startup should run migrations before serving traffic.

## Logging

All services write structured JSON logs to stdout.

Platforms should collect stdout/stderr logs and index by:

- `service`
- `request_id`
- `level`
- `path`
- `status_code`

## Security Checklist

- Use HTTPS.
- Set `SESSION_COOKIE_SECURE=true`.
- Use strong and different `SECRET_KEY` and `JWT_SECRET` values.
- Never commit `.env`.
- Rotate secrets if exposed.
- Add database migrations before production.
- Add automated tests before production.
- Add backups for both PostgreSQL databases.
- Put services behind a reverse proxy.
