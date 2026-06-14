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

- Python dependency audit.
- Pull request dependency review.
- Secret scanning with Gitleaks.
- CodeQL Python analysis.
- Trivy container image scanning for high and critical vulnerabilities.
- CycloneDX SBOM artifacts.
- Dependabot updates for Python, Docker, Docker Compose, and GitHub Actions.

## Local Defaults Are Not Production Secrets

The default values in `docker-compose.yml` and `.env.example` are for local development only:

```env
SECRET_KEY=change-this-local-secret
JWT_SECRET=change-this-local-jwt-secret
POSTGRES_PASSWORD=spendwise_password
```

Use strong unique values in any shared, staging, or production environment.

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
- No automated unit or integration test suite exists yet.

## Reporting Security Issues

Do not open public issues for secrets, credential exposure, authentication bypasses, or data isolation bugs. Report privately to the repository owner or through the repository's private vulnerability reporting flow if enabled.
