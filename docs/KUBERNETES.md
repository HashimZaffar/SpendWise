# Kubernetes Local Lab

This guide documents the current local Kubernetes setup for SpendWise.

## Current Lab

| Item | Value |
| --- | --- |
| Cluster type | Kind |
| Cluster name | `spendwise-lab` |
| Kubernetes version | `v1.35.0` |
| App namespace | `spendwise` |
| App URL | `http://spendwise.localhost:8080` |
| Rancher URL | `https://rancher.localhost:8443` |
| Ingress controller | ingress-nginx |

The Kind control-plane maps host ports to the cluster:

| Host port | Cluster port | Purpose |
| ---: | ---: | --- |
| `8080` | `80` | HTTP ingress for SpendWise |
| `8443` | `443` | HTTPS ingress for Rancher |

## Kubernetes Objects

| Component | Kubernetes object | Replicas | Notes |
| --- | --- | ---: | --- |
| `web-app` | Deployment + Service + Ingress | 2 | Browser UI on container port `5000` |
| `auth-service` | Deployment + Service | 2 | Auth API on container port `5001` |
| `transaction-service` | Deployment + Service | 2 | Transaction API on container port `5002` |
| `postgres` | StatefulSet + Service + PVC | 1 | PostgreSQL on container port `5432` |
| App config | ConfigMap | n/a | Non-sensitive settings |
| App secrets | Secret | n/a | Local lab credentials and connection strings |
| Postgres init SQL | ConfigMap | n/a | Creates app databases and tables on first PVC initialization |

## Deploy

Apply everything:

```bash
kubectl apply -k k8s/base
```

Or apply in layers:

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

## Verify

```bash
kubectl get pods,svc,ingress,pvc -n spendwise -o wide
```

Wait for rollouts:

```bash
kubectl rollout status statefulset/postgres -n spendwise
kubectl rollout status deployment/auth-service -n spendwise
kubectl rollout status deployment/transaction-service -n spendwise
kubectl rollout status deployment/web-app -n spendwise
```

Test through ingress:

```bash
curl -i -H "Host: spendwise.localhost" http://localhost:8080
```

Expected result:

```text
HTTP/1.1 200 OK
```

## Image References

The manifests currently use GHCR image tags produced by CI/CD:

```text
ghcr.io/hashimzaffar/spendwise-web-app:6d5987e8207a48fa22649c34d27c64991c377f21
ghcr.io/hashimzaffar/spendwise-auth-service:6d5987e8207a48fa22649c34d27c64991c377f21
ghcr.io/hashimzaffar/spendwise-transaction-service:6d5987e8207a48fa22649c34d27c64991c377f21
```

The app manifests set:

```yaml
imagePullPolicy: IfNotPresent
```

This lets Kind use an image already present inside node containerd. See [SpendWise Container Images](local-devops/spendwise-images.md) for image loading commands.

## Start and Stop

Stop only the stateless app services:

```bash
kubectl scale deployment/auth-service --replicas=0 -n spendwise
kubectl scale deployment/transaction-service --replicas=0 -n spendwise
kubectl scale deployment/web-app --replicas=0 -n spendwise
```

Start the app services again:

```bash
kubectl scale deployment/auth-service --replicas=2 -n spendwise
kubectl scale deployment/transaction-service --replicas=2 -n spendwise
kubectl scale deployment/web-app --replicas=2 -n spendwise
```

Stop the full SpendWise workload, including PostgreSQL:

```bash
kubectl scale deployment/auth-service --replicas=0 -n spendwise
kubectl scale deployment/transaction-service --replicas=0 -n spendwise
kubectl scale deployment/web-app --replicas=0 -n spendwise
kubectl scale statefulset/postgres --replicas=0 -n spendwise
```

Start it again:

```bash
kubectl scale statefulset/postgres --replicas=1 -n spendwise
kubectl scale deployment/auth-service --replicas=2 -n spendwise
kubectl scale deployment/transaction-service --replicas=2 -n spendwise
kubectl scale deployment/web-app --replicas=2 -n spendwise
```

Stop the Kind node containers:

```bash
docker stop spendwise-lab-control-plane spendwise-lab-worker spendwise-lab-worker2
```

Start the Kind node containers:

```bash
docker start spendwise-lab-control-plane spendwise-lab-worker spendwise-lab-worker2
```

After starting Docker containers, wait for Kubernetes to recover:

```bash
kubectl get nodes
kubectl get pods -A
kubectl get pods -n spendwise
```

## Troubleshooting

### `curl: (56) Recv failure: Connection reset by peer`

This usually means ingress-nginx or the web app pods are not ready yet after a cluster restart.

Check:

```bash
kubectl get pods -n ingress-nginx -o wide
kubectl get pods -n spendwise -o wide
kubectl get endpoints web-app -n spendwise
```

If pods are still starting, wait and retry:

```bash
curl -i -H "Host: spendwise.localhost" http://localhost:8080
```

### Pods show `Unknown`

After stopping and starting Kind node containers, some old pods can remain in `Unknown`. For stateless app pods, delete the stuck pods and let Deployments recreate them:

```bash
kubectl delete pod <pod-name> -n spendwise
kubectl rollout status deployment/web-app -n spendwise
```

Do not delete `postgres-0` unless you know what will happen to the PVC and database state.

### A worker has broken service routing

If pods on one node cannot reach services like `postgres`, inspect kube-proxy:

```bash
kubectl get pods -n kube-system -o wide | grep kube-proxy
kubectl logs -n kube-system <kube-proxy-pod-name> --tail=80
```

For a temporary local lab workaround, stop new pods from scheduling on the bad worker:

```bash
kubectl cordon spendwise-lab-worker
```

Later, when the node is healthy again:

```bash
kubectl uncordon spendwise-lab-worker
```

## Delete the Lab

Deleting the Kind cluster removes the Kubernetes lab:

```bash
kind delete cluster --name spendwise-lab
```

This is different from scaling pods to zero. Deleting the cluster removes the local cluster and its workloads.
