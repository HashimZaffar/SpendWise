# Local DevOps Tool Versions

## Host

- OS: Ubuntu
- Lab project: SpendWise
- Cluster type: Kind
- Kubernetes management: Rancher

## Tool checks

```bash
docker --version
docker compose version
kubectl version --client
kind version
helm version
git --version
```

## Main local endpoints

```text
Docker Compose app: http://localhost:8000
Kubernetes app:    http://spendwise.localhost:8080
Rancher:           https://rancher.localhost:8443
```
