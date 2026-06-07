# Deployment

This guide describes the production deployment shape for SpendWise.

## Production Runtime

Use Gunicorn instead of the Flask development server.

```bash
make prod
```

Equivalent command:

```bash
gunicorn --bind 0.0.0.0:${APP_PORT:-5000} app:app
```

## Required Environment Variables

Production must set:

```env
DATABASE_URL=postgresql://user:password@host:5432/database_name
SECRET_KEY=replace-with-a-long-random-secret
APP_ENV=production
APP_PORT=5000
LOG_LEVEL=INFO
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

Optional:

```env
REDIS_URL=redis://host:6379/0
JWT_SECRET=replace-if-jwt-is-added
CORS_ORIGINS=https://your-domain.example
```

## Health Checks

Use these endpoints in load balancers, platforms, or uptime checks:

```text
/health
/ready
```

Use `/health` for liveness.

Use `/ready` for traffic readiness because it checks database connectivity and Redis connectivity if `REDIS_URL` is configured.

## Database

Current state:

- Local development can use `make init-db`.
- Production skips `db.create_all()`.
- Database migrations are not implemented yet.

Before real production deployment, add:

```text
Flask-Migrate / Alembic
```

Then production startup should run migrations before serving traffic.

## Logging

SpendWise writes structured JSON logs to stdout.

Example:

```json
{
  "level": "info",
  "message": "Request completed",
  "timestamp": "2026-06-07T10:00:00+00:00",
  "request_id": "abc123",
  "method": "GET",
  "path": "/ready",
  "status_code": 200,
  "duration_ms": 12.4
}
```

Platforms should collect stdout/stderr logs.

## Security Checklist

- Use HTTPS.
- Set `SESSION_COOKIE_SECURE=true`.
- Use a strong `SECRET_KEY`.
- Never commit `.env`.
- Rotate secrets if exposed.
- Add database migrations before production.
- Add automated tests before production.
- Add backups for PostgreSQL.
