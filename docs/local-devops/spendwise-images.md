# SpendWise Container Images

## Current Image Tag

```text
6d5987e8207a48fa22649c34d27c64991c377f21
```

## Images

```text
ghcr.io/hashimzaffar/spendwise-web-app:6d5987e8207a48fa22649c34d27c64991c377f21
ghcr.io/hashimzaffar/spendwise-auth-service:6d5987e8207a48fa22649c34d27c64991c377f21
ghcr.io/hashimzaffar/spendwise-transaction-service:6d5987e8207a48fa22649c34d27c64991c377f21
```

## Kind Cluster

```text
spendwise-lab
```

## Kubernetes Manifests

The manifests in `k8s/base/` use the GHCR image tags above directly with:

```yaml
imagePullPolicy: IfNotPresent
```

That means Kubernetes will use the image already present inside the Kind node. If it is missing, Kubernetes may try to pull it from GHCR.

Apply the app manifests:

```bash
kubectl apply -k k8s/base
```

Check rollout:

```bash
kubectl rollout status statefulset/postgres -n spendwise
kubectl rollout status deployment/auth-service -n spendwise
kubectl rollout status deployment/transaction-service -n spendwise
kubectl rollout status deployment/web-app -n spendwise
kubectl get pods,svc,ingress,pvc -n spendwise -o wide
```

Open locally through ingress-nginx:

```text
http://spendwise.localhost:8080
```

Quick ingress test:

```bash
curl -i -H "Host: spendwise.localhost" http://localhost:8080
```

## Loading Images Into Kind

`kind load docker-image` reads from the host Docker image cache. It will fail if the exact tag is not present on the host, for example:

```text
spendwise-web-app:local
```

The current images are OCI index images, so the reliable local lab method is to pull each image directly into every Kind node's containerd:

```bash
TAG=6d5987e8207a48fa22649c34d27c64991c377f21

for node in spendwise-lab-control-plane spendwise-lab-worker spendwise-lab-worker2; do
  docker exec "$node" ctr --namespace=k8s.io images pull --platform linux/amd64 \
    "ghcr.io/hashimzaffar/spendwise-web-app:$TAG"
  docker exec "$node" ctr --namespace=k8s.io images pull --platform linux/amd64 \
    "ghcr.io/hashimzaffar/spendwise-auth-service:$TAG"
  docker exec "$node" ctr --namespace=k8s.io images pull --platform linux/amd64 \
    "ghcr.io/hashimzaffar/spendwise-transaction-service:$TAG"
done
```

Verify:

```bash
TAG=6d5987e8207a48fa22649c34d27c64991c377f21

for node in spendwise-lab-control-plane spendwise-lab-worker spendwise-lab-worker2; do
  echo "$node"
  docker exec "$node" ctr --namespace=k8s.io images list | grep "$TAG"
done
```

## Local Tags Versus GHCR Tags

`kind load docker-image spendwise-web-app:local --name spendwise-lab` works only when the host Docker daemon already has an image with that exact local tag. Pulling an image inside a Kind node does not automatically create a matching host Docker image tag.

For this lab, prefer the GHCR references above and keep the manifests aligned with the exact tag you loaded or pulled.
