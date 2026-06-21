# Local Rancher Lab

This lab runs Rancher on a local Kind cluster. Rancher chart `2.14.x` does not support Kubernetes `v1.36.x`, so the lab uses Kubernetes `v1.35.0`.

The lab also runs the SpendWise Kubernetes deployment in the `spendwise` namespace.

## Create the Cluster

```bash
kind create cluster --config k8s/lab/kind-rancher.yaml
```

The cluster maps local ports to the Kind control-plane node:

- `http://localhost:8080` to cluster port `80`
- `https://localhost:8443` to cluster port `443`

## Install Ingress NGINX

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.15.1/deploy/static/provider/kind/deploy.yaml
kubectl patch deployment ingress-nginx-controller -n ingress-nginx --type merge \
  -p '{"spec":{"template":{"spec":{"nodeSelector":{"kubernetes.io/os":"linux","kubernetes.io/hostname":"spendwise-lab-control-plane"}}}}}'
kubectl rollout status deployment/ingress-nginx-controller -n ingress-nginx --timeout=180s
```

The patch keeps ingress-nginx on the control-plane node so the Kind host port mappings work.

## Install Rancher Prerequisites

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
helm repo update jetstack rancher-stable

helm upgrade --install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true \
  --wait \
  --timeout 5m
```

## Install Rancher

```bash
helm upgrade --install rancher rancher-stable/rancher \
  --namespace cattle-system \
  --create-namespace \
  --set hostname=rancher.localhost \
  --set bootstrapPassword=admin12345 \
  --set replicas=1 \
  --set ingress.tls.source=rancher \
  --wait \
  --timeout 10m
```

Open Rancher locally:

```text
https://rancher.localhost:8443
```

The certificate is self-signed, so the browser will show a local certificate warning.

Bootstrap password for this local lab:

```text
admin12345
```

## Deploy SpendWise

Apply the app:

```bash
kubectl apply -k k8s/base
```

Verify:

```bash
kubectl get pods,svc,ingress,pvc -n spendwise -o wide
kubectl rollout status statefulset/postgres -n spendwise
kubectl rollout status deployment/auth-service -n spendwise
kubectl rollout status deployment/transaction-service -n spendwise
kubectl rollout status deployment/web-app -n spendwise
```

Open SpendWise:

```text
http://spendwise.localhost:8080
```

CLI test:

```bash
curl -i -H "Host: spendwise.localhost" http://localhost:8080
```

## Verify

```bash
kubectl get pods -n cert-manager
kubectl get pods -n ingress-nginx
kubectl get pods,svc,ingress -n cattle-system
kubectl get pods,svc,ingress -n spendwise
curl -k -I --resolve rancher.localhost:8443:127.0.0.1 https://rancher.localhost:8443
```

## Stop and Start Node Containers

Stop the Kind node containers:

```bash
docker stop spendwise-lab-control-plane spendwise-lab-worker spendwise-lab-worker2
```

Start them again:

```bash
docker start spendwise-lab-control-plane spendwise-lab-worker spendwise-lab-worker2
```

After starting the containers, give Kubernetes a little time to recover:

```bash
kubectl get nodes
kubectl get pods -A
```

If SpendWise returns `Recv failure: Connection reset by peer`, check ingress and app readiness:

```bash
kubectl get pods -n ingress-nginx -o wide
kubectl get pods -n spendwise -o wide
kubectl get endpoints web-app -n spendwise
```

If stateless app pods are stuck in `Unknown`, delete those pods and let Deployments recreate them.

## Delete the Lab

```bash
kind delete cluster --name spendwise-lab
```
