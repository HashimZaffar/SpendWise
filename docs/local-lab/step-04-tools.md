# Step 4: Local Kubernetes Tooling

## Goal

Install and verify the tools required to run SpendWise on a local Kubernetes cluster using Kind and manage it through Rancher.

## Tools

| Tool | Purpose |
|---|---|
| Docker | Runs containers and Kind Kubernetes nodes |
| Docker Compose | Runs current SpendWise local stack |
| kubectl | Controls Kubernetes clusters |
| kind | Creates local Kubernetes clusters using Docker containers |
| Helm | Installs Kubernetes applications such as Rancher and ingress-nginx |

## Verification Commands

```bash
docker --version
docker compose version
kubectl version --client
kind version
helm version
```

## Current Lab URLs

```text
SpendWise on Docker Compose: http://localhost:8000
SpendWise on Kubernetes:    http://spendwise.localhost:8080
Rancher:                    https://rancher.localhost:8443
```

## Next Step

Use `k8s/lab/README.md` to create the Kind/Rancher lab, then use `docs/KUBERNETES.md` to deploy and operate SpendWise.
