# GitHub Actions Security Rules

Use these repository settings with the checked-in workflows.

## Branch Protection

Protect `main` and `master`:

- Require pull requests before merging.
- Require approvals and dismiss stale approvals on new commits.
- Require CI and security scanning status checks before merge.
- Keep Docker publishing behind the protected branch and production environment gate.
- Require branches to be up to date before merging.
- Block force pushes and branch deletion.
- Restrict who can bypass required checks.

## Production Approval

Create a `production` environment:

- Require manual approval from trusted reviewers.
- Limit deployments to protected branches.
- Store production-only secrets as environment secrets.

The Docker image publishing workflow targets the `production` environment, so registry publishing waits on the environment protection rules when they are enabled.

## Workflow Safety

- Keep default workflow permissions empty and grant permissions per job.
- Do not use `pull_request_target` for workflows that check out or execute pull request code.
- Do not publish images or deploy artifacts from pull request events.
- Keep third-party actions pinned to full commit SHAs with version comments for Dependabot.
- Disable persisted checkout credentials unless a job explicitly needs to push.
- Never echo secrets or tokens. Mask generated credentials with `::add-mask::` before logging anything that could include them.
