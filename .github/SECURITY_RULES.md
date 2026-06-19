# GitHub Actions Security Rules

Use these repository settings with the checked-in workflows. Application-level security guidance lives in [docs/SECURITY.md](../docs/SECURITY.md).

## Branch Protection

Protect `main` and `master`:

- Require pull requests before merging.
- Require approvals and dismiss stale approvals on new commits.
- Require the CI and security scanning status checks before merge.
- Require branches to be up to date before merging.
- Block force pushes and branch deletion.
- Restrict who can bypass required checks.
- Keep Docker publishing behind protected branches and the `production` environment gate.

## Required Status Checks

At minimum, require these workflows before merge:

- `CI`
- `Security Scanning`

If GitHub exposes individual job names as checks, require:

- `Lint, test, build, and integration`
- `Python dependency scan`
- `Secret scan`
- `CodeQL analysis`
- `Trivy image scan and SBOM (auth-service)`
- `Trivy image scan and SBOM (transaction-service)`
- `Trivy image scan and SBOM (web-app)`

## Production Approval

Create a `production` environment:

- Require manual approval from trusted reviewers.
- Limit deployments to protected branches.
- Store production-only secrets as environment secrets.
- Review deployments before publishing images from `main` or `master`.

The Docker image publishing workflow targets the `production` environment, so registry publishing waits on environment protection rules when they are enabled.

## Workflow Safety

- Keep default workflow permissions empty and grant permissions per job.
- Do not use `pull_request_target` for workflows that check out or execute pull request code.
- Do not publish images or deploy artifacts from pull request events.
- Keep third-party actions pinned to full commit SHAs with version comments for Dependabot.
- Disable persisted checkout credentials unless a job explicitly needs to push.
- Never echo secrets, tokens, cookies, or credentials.
- Mask generated credentials with `::add-mask::` before logging anything that could include them.
- Keep `GITHUB_TOKEN` permissions scoped to the minimum each job needs.

## Dependency and Action Updates

Dependabot is configured for:

- Python packages.
- Docker base images.
- Docker Compose image references.
- GitHub Actions.

Review Dependabot pull requests promptly. For action updates, keep the action reference pinned to a full commit SHA and preserve the version comment for readability.
