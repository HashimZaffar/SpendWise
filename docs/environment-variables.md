# Environment Variables

SpendWise uses environment variables to keep local configuration and secrets out of the source code.

Create a local `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Never commit the real `.env` file. It can contain database passwords and application secrets.

## Variables

| Variable | Required | Example | Purpose |
| --- | --- | --- | --- |
| `DATABASE_URL` | Yes | `postgresql://postgres:password@localhost:5432/expense_tracker_db` | PostgreSQL connection string |
| `SECRET_KEY` | Yes | `change-this-to-a-long-random-secret` | Protects Flask sessions and flash messages |
| `APP_ENV` | Recommended | `development` | Controls app environment and debug mode |
| `APP_PORT` | Recommended | `5000` | Port used by `python3 app.py` |
| `LOG_LEVEL` | Recommended | `INFO` | Python logging level |
| `REDIS_URL` | Optional/reserved | `redis://localhost:6379/0` | Reserved for future Redis-backed features |
| `JWT_SECRET` | Optional/reserved | `change-this-if-you-add-jwt-auth` | Reserved for future JWT/API auth |
| `CORS_ORIGINS` | Optional/reserved | `http://127.0.0.1:5000,http://localhost:5000` | Reserved for future cross-origin/API configuration |

## `DATABASE_URL`

Format:

```text
postgresql://username:password@host:port/database_name
```

Example:

```env
DATABASE_URL=postgresql://postgres:my_password@localhost:5432/expense_tracker_db
```

Parts:

- `postgresql://` tells SQLAlchemy to use PostgreSQL.
- `postgres` is the database username.
- `my_password` is the database password.
- `localhost` means the database runs on your machine.
- `5432` is the default PostgreSQL port.
- `expense_tracker_db` is the database name.

## `SECRET_KEY`

Flask uses `SECRET_KEY` to sign session data.

Generate a stronger value with Python:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Then paste it into `.env`:

```env
SECRET_KEY=your-generated-secret
```

## `APP_ENV`

Use:

```env
APP_ENV=development
```

Current behavior:

- `development` enables Flask debug mode when running `python3 app.py`.
- Any other value disables debug mode.

## `APP_PORT`

Controls the port used by:

```bash
python3 app.py
```

Example:

```env
APP_PORT=5000
```

## `LOG_LEVEL`

Controls Python logging level.

Common values:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Example:

```env
LOG_LEVEL=INFO
```

## Reserved Variables

These are documented now so the project has a clean configuration contract, even though the current Flask app does not actively use Redis, JWT auth, or CORS middleware yet:

```env
REDIS_URL=
JWT_SECRET=change-this-if-you-add-jwt-auth
CORS_ORIGINS=http://127.0.0.1:5000,http://localhost:5000
```

## Security Notes

- Never commit `.env`.
- Keep `.env.example` safe and generic.
- Use different secrets for local development and production.
- Rotate secrets if they are exposed.
- Do not put real passwords, production URLs, or private keys in documentation.
