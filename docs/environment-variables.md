# Environment Variables

SpendWise uses environment variables so secrets and runtime settings stay outside the source code.

Create a local file:

```bash
cp .env.example .env
```

Never commit the real `.env` file.

## Common Variables

| Variable | Required | Example | Purpose |
| --- | --- | --- | --- |
| `APP_ENV` | Recommended | `development` | Runtime environment |
| `LOG_LEVEL` | Recommended | `INFO` | JSON log level |
| `SECRET_KEY` | Yes for `web-app` | `long-random-secret` | Protects Flask browser sessions |
| `JWT_SECRET` | Yes for APIs | `different-long-random-secret` | Signs and verifies JWT access tokens |

## Web App Variables

| Variable | Required | Example | Purpose |
| --- | --- | --- | --- |
| `WEB_APP_PORT` | Recommended | `5000` | Browser-facing app port |
| `AUTH_SERVICE_URL` | Yes | `http://127.0.0.1:5001` | Auth service URL |
| `TRANSACTION_SERVICE_URL` | Yes | `http://127.0.0.1:5002` | Transaction service URL |
| `SERVICE_TIMEOUT_SECONDS` | Recommended | `5` | HTTP timeout for service calls |
| `SESSION_COOKIE_SECURE` | Recommended | `false` locally, `true` in production | Sends cookies only over HTTPS |
| `SESSION_COOKIE_HTTPONLY` | Recommended | `true` | Blocks JavaScript from reading session cookie |
| `SESSION_COOKIE_SAMESITE` | Recommended | `Lax` | Controls cross-site cookie behavior |

## Auth Service Variables

| Variable | Required | Example | Purpose |
| --- | --- | --- | --- |
| `AUTH_SERVICE_PORT` | Recommended | `5001` | Auth API port |
| `AUTH_DATABASE_URL` | Yes | `postgresql://user:password@host:5432/spendwise_auth_db` | Auth database connection |
| `JWT_EXPIRES_MINUTES` | Recommended | `120` | Access token lifetime |

## Transaction Service Variables

| Variable | Required | Example | Purpose |
| --- | --- | --- | --- |
| `TRANSACTION_SERVICE_PORT` | Recommended | `5002` | Transaction API port |
| `TRANSACTION_DATABASE_URL` | Yes | `postgresql://user:password@host:5432/spendwise_transaction_db` | Transaction database connection |

## Optional / Legacy Variables

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | Kept for the legacy monolith `app.py` |
| `APP_PORT` | Kept for the legacy monolith `app.py` |
| `REDIS_URL` | Optional Redis config for future cache/session work |
| `CORS_ORIGINS` | Reserved for future browser/API CORS configuration |

## Generate Strong Secrets

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Use different values for:

```env
SECRET_KEY=
JWT_SECRET=
```

## Security Notes

- Never commit `.env`.
- Keep `.env.example` generic.
- Use different secrets for local and production.
- Rotate secrets if they are exposed.
- Set `SESSION_COOKIE_SECURE=true` only when HTTPS is enabled.
