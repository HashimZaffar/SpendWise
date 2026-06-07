# Troubleshooting

This guide covers common local setup and runtime issues.

## `ModuleNotFoundError: No module named 'flask'`

Dependencies are not installed or the virtual environment is not active.

Fix:

```bash
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## `ModuleNotFoundError: No module named 'psycopg2'`

PostgreSQL driver is missing.

Fix:

```bash
python3 -m pip install -r requirements.txt
```

## `DATABASE_URL` Is Missing

The `.env` file may not exist.

Fix:

```bash
cp .env.example .env
```

Then edit `.env`.

## `SECRET_KEY` Is Missing

Flask needs `SECRET_KEY` for session and flash-message security.

Fix:

```bash
cp .env.example .env
```

Then set:

```env
SECRET_KEY=your-generated-secret
```

Generate a strong value:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## `password authentication failed for user "postgres"`

The password in `DATABASE_URL` is wrong.

Fix:

1. Confirm your PostgreSQL password.
2. Update `.env`.
3. Restart the Flask app.

## `database "expense_tracker_db" does not exist`

The database has not been created.

Fix:

```bash
createdb expense_tracker_db
```

Or:

```bash
psql -U postgres
```

Then:

```sql
CREATE DATABASE expense_tracker_db;
```

## `relation "users" does not exist`

The app has not created tables yet, or the wrong database is connected.

Fix:

1. Check `DATABASE_URL`.
2. Run the app:

```bash
python3 app.py
```

The app uses `db.create_all()` during startup for local development.

## Login Works But Dashboard Shows No Old Transactions

This can happen if transactions were created before user accounts existed.

SpendWise now shows only transactions linked to the logged-in user through `user_id`.

Fix:

- Create new transactions after logging in.
- Old transactions without `user_id` are intentionally hidden from account-specific dashboards.

## CSS Changes Do Not Show

The browser may be caching old CSS.

Fix:

```text
Ctrl + Shift + R
```

Or clear browser cache.

## Port 5000 Already In Use

Another Flask app may already be running.

Fix:

Stop the other process or run on another port:

```bash
flask run --port 5001
```

If using `python3 app.py`, change the `app.run()` call temporarily:

```python
app.run(debug=True, port=5001)
```

## Syntax Check

Run:

```bash
python3 -m py_compile app.py
```

If there is no output, the syntax check passed.
