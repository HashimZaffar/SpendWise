# Operations

This guide covers running, observing, and publishing SpendWise.

## Local Runtime

### Docker Compose

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

The full local CI command also manages the stack:

```bash
python3 scripts/ci_check.py
```

It starts Compose for the integration smoke test and finishes with `docker compose down -v`, which removes local database data.

### Kubernetes Local Lab

Apply the current Kubernetes base:

```bash
kubectl apply -k k8s/base
```

Check rollout:

```bash
kubectl rollout status statefulset/postgres -n spendwise
kubectl rollout status deployment/auth-service -n spendwise
kubectl rollout status deployment/transaction-service -n spendwise
kubectl rollout status deployment/web-app -n spendwise
```

Check resources:

```bash
kubectl get pods,svc,ingress,pvc -n spendwise -o wide
```

Test the app through ingress:

```bash
curl -i -H "Host: spendwise.localhost" http://localhost:8080
```

Expected browser URL:

```text
http://spendwise.localhost:8080
```

Stop only app services while leaving PostgreSQL running:

```bash
kubectl scale deployment/auth-service --replicas=0 -n spendwise
kubectl scale deployment/transaction-service --replicas=0 -n spendwise
kubectl scale deployment/web-app --replicas=0 -n spendwise
```

Start app services again:

```bash
kubectl scale deployment/auth-service --replicas=2 -n spendwise
kubectl scale deployment/transaction-service --replicas=2 -n spendwise
kubectl scale deployment/web-app --replicas=2 -n spendwise
```

Stop the full workload:

```bash
kubectl scale deployment/auth-service --replicas=0 -n spendwise
kubectl scale deployment/transaction-service --replicas=0 -n spendwise
kubectl scale deployment/web-app --replicas=0 -n spendwise
kubectl scale statefulset/postgres --replicas=0 -n spendwise
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

In Kubernetes, PostgreSQL data is stored in a PVC created from `k8s/base/03-postgres.yaml`:

```bash
kubectl get pvc -n spendwise
```

Deleting pods does not delete the PVC. Deleting the PVC or the Kind cluster removes the local Kubernetes database data.

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

The local CI script performs linting, Python syntax checks, Compose config validation, Docker image builds, and an integration smoke test. The integration step starts the stack, waits for web readiness, runs the `integration-tests` service, and removes containers and volumes when finished.

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

The local Kubernetes manifests currently pin GHCR images by full commit SHA. This makes the lab reproducible and avoids accidental use of a moving tag.

## Release Checklist

Before publishing images from `main` or `master`:

1. Run `python3 scripts/ci_check.py`.
2. Confirm the CI, security scanning, and Docker build workflows are green.
3. Confirm `docker compose up --build` starts cleanly after any local reset.
4. Confirm `python3 scripts/docker_tools.py health` passes.
5. Review dependency audit, secret scan, CodeQL, Trivy, and SBOM results.
6. Confirm production environment protection is enabled in GitHub.
7. Confirm production secrets are set and are not the local defaults.
8. Confirm database backup and rollback plans for any schema-affecting changes.

## Rollback Notes

Images are tagged with the full commit SHA. To roll back a deployment, redeploy the last known-good SHA-tagged image for each service and verify readiness.

Database rollback is separate from image rollback. The current app uses an initialization SQL script rather than a migration tool, so schema changes should be planned carefully before shared deployments.

## Kubernetes Troubleshooting

### Ingress returns connection reset

Check ingress-nginx and web-app readiness:

```bash
kubectl get pods -n ingress-nginx -o wide
kubectl get pods -n spendwise -o wide
kubectl get endpoints web-app -n spendwise
```

If this happens immediately after `docker start` of the Kind node containers, wait for Kubernetes to recover and retry.

### Pods are stuck in `Unknown`

For stateless app pods, delete the stuck pod and let the Deployment recreate it:

```bash
kubectl delete pod <pod-name> -n spendwise
```

Avoid deleting `postgres-0` unless you are intentionally working on database recovery.

### Service DNS or ClusterIP is broken on one worker

Check kube-proxy:

```bash
kubectl get pods -n kube-system -o wide | grep kube-proxy
kubectl logs -n kube-system <kube-proxy-pod-name> --tail=80
```

For local lab recovery, temporarily stop scheduling new pods on the bad worker:

```bash
kubectl cordon spendwise-lab-worker
```

When the node is healthy:

```bash
kubectl uncordon spendwise-lab-worker
```
