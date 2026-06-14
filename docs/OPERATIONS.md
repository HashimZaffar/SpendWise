# Operations

This guide covers running, observing, and publishing SpendWise.

## Local Runtime

Start:

```bash
docker compose up --build
```

Start in the background:

```bash
docker compose up --build -d
```

Status:

```bash
docker compose ps
```

Logs:

```bash
docker compose logs --tail 100
```

Stop:

```bash
docker compose down
```

Reset data:

```bash
docker compose down -v
```

The helper script provides equivalent commands:

```bash
python3 scripts/docker_tools.py up
python3 scripts/docker_tools.py status
python3 scripts/docker_tools.py logs
python3 scripts/docker_tools.py down
python3 scripts/docker_tools.py clean
```

## Health and Readiness

Web app endpoints:

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/ready
```

Use the helper to check both web endpoints:

```bash
python3 scripts/docker_tools.py health
```

Expected readiness shape:

```json
{
  "status": "ready",
  "service": "web-app",
  "check": "ready",
  "checks": {
    "auth_service": "ok",
    "transaction_service": "ok"
  }
}
```

The backend services each expose `/ready` and check database connectivity.

## Logs

All Flask services write JSON logs to stdout. Log records include:

- `timestamp`
- `level`
- `service`
- `message`
- `request_id`
- `method`
- `path`
- `status_code`
- `duration_ms`

Example:

```json
{
  "level": "info",
  "message": "Request completed",
  "timestamp": "2026-06-14T12:00:00Z",
  "service": "web-app",
  "request_id": "f9e3...",
  "method": "GET",
  "path": "/dashboard",
  "status_code": 200,
  "duration_ms": 42.7
}
```

Request IDs are propagated from the web app to backend service calls with `X-Request-ID`.

## Persistence

PostgreSQL data is stored in the named Docker volume:

```text
spendwise_postgres_data
```

Removing the volume deletes local app data:

```bash
docker compose down -v
```

For any shared or production-like environment, take database backups before changing images, schemas, or environment variables.

## Configuration for Shared Environments

Do not use the local placeholder secrets outside local development.

Set at minimum:

```env
APP_ENV=production
LOG_LEVEL=INFO
POSTGRES_USER=<strong-user>
POSTGRES_PASSWORD=<strong-password>
SECRET_KEY=<strong-random-secret>
JWT_SECRET=<strong-random-secret>
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

When using cross-site cookies, set:

```env
SESSION_COOKIE_SAMESITE=None
SESSION_COOKIE_SECURE=true
```

The application validates this combination at startup.

## CI Workflows

### `.github/workflows/ci.yml`

Runs on pushes to all branches, pull requests to `main` or `master`, and manual dispatch.

The job:

- Checks out code with persisted credentials disabled.
- Sets up Python 3.12.
- Installs development and service dependencies.
- Runs `python scripts/ci_check.py`.

### `.github/workflows/security.yml`

Runs on pushes to all branches, pull requests to `main` or `master`, weekly on Monday, and manual dispatch.

The workflow includes:

- Python dependency audit.
- Pull request dependency review.
- Gitleaks secret scanning.
- CodeQL Python analysis.
- Trivy image scans for all service images.
- CycloneDX SBOM artifact upload for each service image.

### `.github/workflows/docker-build.yml`

Runs on pushes to `main` or `master` and manual dispatch.

The workflow:

- Builds each service image.
- Publishes images to GitHub Container Registry.
- Tags images by branch and full commit SHA.
- Uses the `production` GitHub environment gate.

Images are named:

```text
ghcr.io/<owner>/spendwise-auth-service
ghcr.io/<owner>/spendwise-transaction-service
ghcr.io/<owner>/spendwise-web-app
```

## Release Checklist

Before publishing images from `main` or `master`:

1. Run `python3 scripts/ci_check.py`.
2. Confirm `docker compose up --build` starts cleanly.
3. Confirm `python3 scripts/docker_tools.py health` passes.
4. Review dependency and security workflow results.
5. Confirm production environment protection is enabled in GitHub.
6. Confirm production secrets are set and are not the local defaults.
7. Confirm database backup and rollback plans for any schema-affecting changes.

## Rollback Notes

Images are tagged with the full commit SHA. To roll back a deployment, redeploy the last known-good SHA-tagged image for each service and verify readiness.

Database rollback is separate from image rollback. The current app uses an initialization SQL script rather than a migration tool, so schema changes should be planned carefully before shared deployments.
