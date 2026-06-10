# Troubleshooting

This guide lists common local issues and fixes.

## PostgreSQL Is Not Running

Symptom:

```text
localhost:5432 - no response
connection refused
```

Fix:

```bash
sudo pg_ctlcluster 16 main start
pg_isready -h localhost -p 5432
```

Expected:

```text
localhost:5432 - accepting connections
```

## Database Does Not Exist

Symptom:

```text
database "spendwise_auth_db" does not exist
database "spendwise_transaction_db" does not exist
```

Fix:

```bash
createdb -U postgres -h localhost spendwise_auth_db
createdb -U postgres -h localhost spendwise_transaction_db
```

## Wrong PostgreSQL Password

Symptom:

```text
password authentication failed for user "postgres"
```

Fix:

Update `.env` with the correct password:

```env
AUTH_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/spendwise_auth_db
TRANSACTION_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/spendwise_transaction_db
```

## Port Already In Use

Symptom:

```text
Address already in use
```

Fix:

Find and stop the old process, or change the service port in `.env`.

Default ports:

```env
WEB_APP_PORT=5000
AUTH_SERVICE_PORT=5001
TRANSACTION_SERVICE_PORT=5002
```

## Web App Opens But Dashboard Fails

This usually means one backend service is down.

Check:

```bash
curl http://127.0.0.1:5001/ready
curl http://127.0.0.1:5002/ready
```

Both should return:

```json
{
  "status": "ready"
}
```

## Changes To `.env` Are Not Working

Stop the service and start it again.

Environment variables are loaded when the Python process starts.

## Python Dependency Error

Symptom:

```text
ModuleNotFoundError
```

Fix:

```bash
source venv/bin/activate
make install
make install-services
```

## Docker Compose Database Was Not Reinitialized

Symptom:

```text
database table does not exist
old test data still exists
```

Reason:

Docker keeps PostgreSQL data in a named volume. Init SQL files only run the
first time the volume is created.

Fix:

```bash
docker compose down -v
docker compose up --build
```

Warning: `docker compose down -v` deletes the local Docker database volume.

## Docker Port Already In Use

Symptom:

```text
port is already allocated
```

Fix:

Stop the local service using that port, or stop the old Compose stack:

```bash
docker compose down
```
