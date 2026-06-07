# Deployment

This guide describes the production deployment shape for SpendWise microservices.

## Production Services

Deploy these services separately:

```text
web-app
auth-service
transaction-service
```

Each service has its own Dockerfile.

## Runtime

Each service runs with Gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 app:app
gunicorn --bind 0.0.0.0:5001 app:app
gunicorn --bind 0.0.0.0:5002 app:app
```

In Docker Compose, use:

```bash
make compose-up
```

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
AUTH_SERVICE_URL=http://auth-service:5001
TRANSACTION_SERVICE_URL=http://transaction-service:5002
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
web-app/health
auth-service/health
transaction-service/health
```

Use `/ready` for traffic readiness:

```text
web-app/ready
auth-service/ready
transaction-service/ready
```

## Database

Current Docker startup creates tables automatically for learning convenience.

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
- Put services behind a reverse proxy or API gateway.
