# Environment Variables

SpendWise uses environment variables for configuration. The real `.env` file must stay local and must not be committed.

Create it from the example:

```bash
cp .env.example .env
```

## Required Variables

| Variable | Used By | Example | Purpose |
| --- | --- | --- | --- |
| `APP_ENV` | all services | `development` | Runtime environment |
| `LOG_LEVEL` | all services | `INFO` | Structured log level |
| `SECRET_KEY` | `web-app` | `change-me` | Signs Flask sessions |
| `JWT_SECRET` | API services | `change-me` | Signs and verifies JWT tokens |
| `AUTH_DATABASE_URL` | `auth-service` | `postgresql://postgres:password@localhost:5432/spendwise_auth_db` | Auth database connection |
| `TRANSACTION_DATABASE_URL` | `transaction-service` | `postgresql://postgres:password@localhost:5432/spendwise_transaction_db` | Transaction database connection |
| `AUTH_SERVICE_URL` | `web-app` | `http://127.0.0.1:5001` | Auth API base URL |
| `TRANSACTION_SERVICE_URL` | `web-app` | `http://127.0.0.1:5002` | Transaction API base URL |

## Port Variables

| Variable | Default | Service |
| --- | --- | --- |
| `WEB_APP_PORT` | `5000` | `web-app` |
| `AUTH_SERVICE_PORT` | `5001` | `auth-service` |
| `TRANSACTION_SERVICE_PORT` | `5002` | `transaction-service` |

## Service Timeout

| Variable | Default | Purpose |
| --- | --- | --- |
| `SERVICE_TIMEOUT_SECONDS` | `5` | HTTP timeout for calls from `web-app` to backend services |

## Session Cookie Variables

| Variable | Local | Production | Purpose |
| --- | --- | --- | --- |
| `SESSION_COOKIE_SECURE` | `false` | `true` | Sends cookies only over HTTPS |
| `SESSION_COOKIE_HTTPONLY` | `true` | `true` | Blocks JavaScript access to session cookies |
| `SESSION_COOKIE_SAMESITE` | `Lax` | `Lax` | Helps reduce cross-site request risk |

## JWT Lifetime

| Variable | Default | Purpose |
| --- | --- | --- |
| `JWT_EXPIRES_MINUTES` | `120` | Access token lifetime |

## Generate Strong Secrets

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Use different values for:

```env
SECRET_KEY=
JWT_SECRET=
```

## Security Rules

- Never commit `.env`.
- Commit `.env.example` only.
- Do not put production passwords in docs.
- Use different secrets for local and production.
- Rotate secrets if they are exposed.
