# Local Development

This guide covers day-to-day development for SpendWise.

## Requirements

- Docker
- Docker Compose
- Python 3.12 for local lint and syntax checks

The app itself is Docker-first. Running services directly on the host is possible, but the documented path is Docker Compose because it provides PostgreSQL and the correct service URLs.

## Start the Stack

### Docker Compose

```bash
docker compose up --build
```

Open:

```text
http://localhost:8000
```

Run in the background with the helper:

```bash
python3 scripts/docker_tools.py up
```

Check container status:

```bash
python3 scripts/docker_tools.py status
```

Tail logs:

```bash
python3 scripts/docker_tools.py logs
```

Stop:

```bash
python3 scripts/docker_tools.py down
```

Remove local data and orphaned containers:

```bash
python3 scripts/docker_tools.py clean
```

### Kubernetes Lab

Use the Kubernetes lab when you want to practice Deployments, Services, Ingress, ConfigMaps, Secrets, StatefulSets, PVCs, and Rancher.

The app namespace is:

```text
spendwise
```

Apply the local Kubernetes manifests:

```bash
kubectl apply -k k8s/base
```

Check pods and ingress:

```bash
kubectl get pods,svc,ingress,pvc -n spendwise -o wide
```

Open:

```text
http://spendwise.localhost:8080
```

If you want to apply the app in order:

```bash
kubectl apply -f k8s/base/00-namespace.yaml
kubectl apply -f k8s/base/01-configmap.yaml
kubectl apply -f k8s/base/02-secret.yaml
kubectl apply -f k8s/base/02a-postgres-init-configmap.yaml
kubectl apply -f k8s/base/03-postgres.yaml
kubectl apply -f k8s/base/04-auth-service.yaml
kubectl apply -f k8s/base/05-transaction-service.yaml
kubectl apply -f k8s/base/06-web-app.yaml
kubectl apply -f k8s/base/07-ingress.yaml
```

Kubernetes lab details live in [Kubernetes Local Lab](KUBERNETES.md).

## Environment Setup

The defaults in `docker-compose.yml` are enough for local development. Create `.env` only when you need to override them:

```bash
cp .env.example .env
```

Useful overrides:

```env
WEB_APP_HOST_PORT=8000
LOG_LEVEL=DEBUG
SECRET_KEY=replace-me-for-shared-environments
JWT_SECRET=replace-me-for-shared-environments
SESSION_COOKIE_SECURE=false
```

Use strong unique values for `SECRET_KEY` and `JWT_SECRET` outside local-only development.

## Local Tooling

Create a virtual environment and install development tools:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Install service dependencies locally only when you need editor analysis or to run a service outside Docker:

```bash
pip install -r services/auth-service/requirements.txt
pip install -r services/transaction-service/requirements.txt
pip install -r services/web-app/requirements.txt
```

## Checks

Run the same local CI script used by GitHub Actions:

```bash
python3 scripts/ci_check.py
```

The full run is destructive for local Compose data. It starts the stack, waits for readiness, runs the integration smoke test in the Compose network, and finishes with `docker compose down -v` so CI always tests from a clean database.

This runs:

- Ruff linting for `services` and `scripts`.
- Python syntax checks for app and script files.
- `docker compose config`.
- `docker compose build`.
- The integration smoke test in `scripts/integration_test.py`.

Skip the integration smoke test when you want to preserve local database data:

```bash
python3 scripts/ci_check.py --skip-integration
```

Skip Docker Compose config, build, and integration checks when iterating on Python-only changes:

```bash
python3 scripts/ci_check.py --skip-build
```

Run lint only:

```bash
ruff check services scripts
```

Run syntax checks only:

```bash
PYTHONPYCACHEPREFIX=/tmp/spendwise-pycache python3 -m py_compile \
  services/auth-service/app.py \
  services/transaction-service/app.py \
  services/web-app/app.py \
  scripts/docker_tools.py \
  scripts/ci_check.py \
  scripts/integration_test.py
```

The integration smoke test covers signup, login, current-user lookup, transaction creation, listing, search, summary totals, and chart flags. There is no separate unit-test suite yet. Add focused tests before changing shared validation, auth behavior, or transaction summary logic.

## Database

The PostgreSQL container runs the initialization scripts in `database/init/` the first time the volume is created.

The app uses:

- `spendwise_auth_db` for users.
- `spendwise_transaction_db` for transactions.

To reset the local databases:

```bash
docker compose down -v
docker compose up --build
```

or:

```bash
python3 scripts/docker_tools.py clean
python3 scripts/docker_tools.py up
```

## Common Workflows

### Add a Dashboard Field

1. Update the model or serializer in `services/transaction-service/app.py`.
2. Add the field to the JSON response if it should reach the UI.
3. Update `services/web-app/app.py` to pass the field into the template.
4. Update `services/web-app/templates/index.html`.
5. Update docs if the API contract changes.
6. Run `python3 scripts/ci_check.py --skip-build`.

### Add an Auth Field

1. Update `User` and `serialize_user` in `services/auth-service/app.py`.
2. Update `database/init/01-create-spendwise-databases.sql` for fresh local databases.
3. Update signup or login handling in `services/web-app/app.py` if browser forms change.
4. Update templates and docs.
5. Reset local database data if testing from a fresh schema.

### Add a Service Environment Variable

1. Add the variable to the relevant service in `docker-compose.yml`.
2. Add it to `.env.example` if users may override it.
3. Validate it in the service at startup.
4. Document it in `README.md` or the relevant docs page.

## Troubleshooting

### Port 8000 Is Already In Use

Set another host port:

```bash
WEB_APP_HOST_PORT=8010 docker compose up --build
```

or put this in `.env`:

```env
WEB_APP_HOST_PORT=8010
```

### Readiness Fails

Check the stack:

```bash
docker compose ps
python3 scripts/docker_tools.py health
python3 scripts/docker_tools.py logs
```

Common causes:

- PostgreSQL is still starting.
- `.env` has mismatched database credentials.
- `JWT_SECRET` differs between `auth-service` and `transaction-service`.
- A service failed startup validation for an environment variable.
- The local Postgres volume is stale or partially initialized.

### Kubernetes URL Resets After Restart

If `curl -H "Host: spendwise.localhost" http://localhost:8080` returns `Recv failure: Connection reset by peer`, the cluster may still be recovering after Docker node containers were restarted.

Check:

```bash
kubectl get nodes
kubectl get pods -n ingress-nginx
kubectl get pods -n spendwise -o wide
```

Wait for `ingress-nginx-controller` and `web-app` pods to become `Running` and ready, then retry the URL.

### PostgreSQL Volume Is Stale or Broken

If Postgres logs include `directory "/var/lib/postgresql/data" exists but is not empty`, reset the local Compose volume:

```bash
docker compose down -v
docker compose up --build
```

This deletes local SpendWise database data.

### Login Works but Dashboard Logs Out

The transaction service rejects the bearer token when it cannot validate the JWT. Confirm:

- `JWT_SECRET` is the same for auth and transaction services.
- The token is not expired.
- The services were restarted after changing `.env`.

### `SESSION_COOKIE_SAMESITE=None` Fails Startup

`SESSION_COOKIE_SECURE` must be `true` when `SESSION_COOKIE_SAMESITE=None`.

```env
SESSION_COOKIE_SAMESITE=None
SESSION_COOKIE_SECURE=true
```
