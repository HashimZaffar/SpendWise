# Security

SpendWise includes baseline security controls for a small Flask application. This document explains what is already present and what must be hardened outside local-only development.

## Current Controls

### Authentication

- Passwords are hashed with Werkzeug before storage.
- Login returns a signed JWT access token.
- JWTs include:
  - `sub`
  - `name`
  - `email`
  - `iat`
  - `exp`
  - `iss`
- `transaction-service` requires issuer `spendwise-auth-service`.
- Token lifetime is configured with `JWT_EXPIRES_MINUTES`.

### Authorization

- Transaction routes require `Authorization: Bearer <token>`.
- Transaction reads, updates, and deletes filter by both `transaction_id` and JWT subject user ID.
- A user cannot access another user's transactions through the transaction API.

### Browser Session Protection

- Browser sessions are signed with `SECRET_KEY`.
- Browser POST routes validate CSRF tokens.
- Session cookie settings are environment-controlled:
  - `SESSION_COOKIE_SECURE`
  - `SESSION_COOKIE_HTTPONLY`
  - `SESSION_COOKIE_SAMESITE`
- The app rejects `SESSION_COOKIE_SAMESITE=None` unless `SESSION_COOKIE_SECURE=true`.

### Service and Container Hardening

- App containers run as non-root `appuser`.
- Dockerfiles use multi-stage builds.
- Only `web-app` is published to the host by default.
- Backend APIs stay inside the Compose network by default.
- Services expose health checks.

### Logging and Traceability

- Services emit JSON logs.
- Each request receives an `X-Request-ID`.
- The web app forwards the request ID to backend service calls.

### CI Security

Security automation includes:

- Full local CI with an integration smoke test.
- Python dependency audit.
- Pull request dependency review.
- Secret scanning with Gitleaks.
- CodeQL Python analysis.
- Trivy container image scanning for high and critical vulnerabilities.
- CycloneDX SBOM artifacts.
- Dependabot updates for Python, Docker, Docker Compose, and GitHub Actions.

Gitleaks uses `.gitleaks.toml`. The config extends the default Gitleaks rules and allows only the known SpendWise GHCR image references that end in 40-character Git commit SHA tags. This prevents Docker image tags from being reported as generic API keys while keeping the default secret rules active.

### Optional Local Security Checks

These commands mirror the main security workflow checks when Docker and network access are available:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pip-audit
pip-audit \
  -r requirements-dev.txt \
  -r services/auth-service/requirements.txt \
  -r services/transaction-service/requirements.txt \
  -r services/web-app/requirements.txt
```

```bash
docker run --rm -v "${PWD}:/repo" zricethezav/gitleaks:latest \
  detect --source=/repo --config=/repo/.gitleaks.toml --verbose --redact
```

After building images with `docker compose build`, scan each service image:

```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest \
  image --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 \
  spendwise-auth-service:latest

docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest \
  image --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 \
  spendwise-transaction-service:latest

docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest \
  image --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 \
  spendwise-web-app:latest
```

## Local Defaults Are Not Production Secrets

The default values in `docker-compose.yml` and `.env.example` are for local development only:

```env
SECRET_KEY=change-this-local-secret
JWT_SECRET=change-this-local-jwt-secret
POSTGRES_PASSWORD=spendwise_password
```

Use strong unique values in any shared, staging, or production environment.

The Kubernetes lab Secret in `k8s/base/02-secret.yaml` also contains local-only placeholder values. It is acceptable for the local Kind lab, but it must be replaced with real secret management before any shared or production deployment.

## Required Production Hardening

Before exposing SpendWise beyond a local workstation:

1. Set strong `SECRET_KEY`, `JWT_SECRET`, and PostgreSQL credentials.
2. Run behind HTTPS.
3. Set `SESSION_COOKIE_SECURE=true`.
4. Keep `SESSION_COOKIE_HTTPONLY=true`.
5. Use `SESSION_COOKIE_SAMESITE=Lax` unless cross-site cookie behavior is required.
6. Restrict network access to backend services and PostgreSQL.
7. Configure database backups and restore testing.
8. Keep GitHub branch protection and environment approval rules enabled.
9. Review image scan and dependency audit results before release.
10. Avoid logging credentials, tokens, cookies, or full request bodies.

## Secret Handling

- Do not commit `.env`.
- Store shared-environment secrets in a secret manager or GitHub environment secrets.
- Rotate `JWT_SECRET` and `SECRET_KEY` if they are exposed.
- Rotating `JWT_SECRET` invalidates existing JWTs.
- Rotating `SECRET_KEY` invalidates existing browser sessions.

## Dependency Updates

Dependabot checks:

- Root Python dependencies.
- Service Python dependencies.
- Dockerfiles.
- Docker Compose.
- GitHub Actions.

Security updates should be reviewed and merged promptly after CI passes.

## Known Gaps

These are acceptable for a local demo app but should be addressed for production use:

- No database migration tool is configured.
- No rate limiting is implemented on login or signup.
- No account lockout or email verification flow is implemented.
- No refresh-token flow is implemented.
- No centralized log aggregation or alerting is configured.
- No dedicated unit-test suite exists yet.
- Integration smoke tests do not yet cover browser HTML flows, negative authorization cases, or cross-user isolation attempts.

## Reporting Security Issues

Do not open public issues for secrets, credential exposure, authentication bypasses, or data isolation bugs. Report privately to the repository owner or through the repository's private vulnerability reporting flow if enabled.
