# Step 4: Local Kubernetes Tooling

## Goal

Install and verify the tools required to run SpendWise on a local Kubernetes cluster using kind and manage it through Rancher.

## Tools

| Tool | Purpose |
|---|---|
| Docker | Runs containers and kind Kubernetes nodes |
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