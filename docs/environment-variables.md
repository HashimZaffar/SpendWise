# Environment Variables

SpendWise uses environment variables to keep local configuration and secrets out of the source code.

Create a local `.env` file from `.env.example`:

```bash
cp .env.example .env
```

## Required Variables

| Variable | Required | Example | Purpose |
| --- | --- | --- | --- |
| `DATABASE_URL` | Yes | `postgresql://postgres:password@localhost:5432/expense_tracker_db` | PostgreSQL connection string |
| `SECRET_KEY` | Yes | `change-this-to-a-long-random-secret` | Protects Flask sessions and flash messages |

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

## Security Notes

- Never commit `.env`.
- Keep `.env.example` safe and generic.
- Use different secrets for local development and production.
- Rotate secrets if they are exposed.
