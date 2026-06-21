# SpendWise Docker Compose to Kubernetes Plan

## Goal

Convert SpendWise from Docker Compose into a Kubernetes-native local deployment running on Kind and managed through Rancher.

Current status: the local Kubernetes implementation exists in `k8s/base/` and deploys into the `spendwise` namespace.

## Local Platform

- Host OS: Ubuntu
- Container runtime: Docker
- Kubernetes cluster: Kind
- Kubernetes management UI: Rancher
- App namespace: spendwise

## Docker Compose Components

| Compose Component | Current Role | Kubernetes Object |
|---|---|---|
| web-app | Browser UI | Deployment + Service + Ingress |
| auth-service | Signup, login, JWT | Deployment + Service |
| transaction-service | Transactions and dashboard data | Deployment + Service |
| postgres | Database | StatefulSet + Service + PVC |
| .env | App configuration | ConfigMap + Secret |
| Docker network | Internal service communication | Kubernetes Services/DNS |
| Docker volume | Persistent database storage | PersistentVolumeClaim |

## Kubernetes Namespaces

| Namespace | Purpose |
|---|---|
| spendwise | SpendWise application |
| ingress-nginx | Ingress controller |
| cert-manager | Certificate management for Rancher |
| cattle-system | Rancher server |

## SpendWise Kubernetes Resources

### web-app

- Type: Deployment
- Replicas: 2
- Container port: 5000
- Service type: ClusterIP
- Exposed through Ingress

### auth-service

- Type: Deployment
- Replicas: 2
- Container port: 5001
- Service type: ClusterIP
- Internal URL: http://auth-service:5001

### transaction-service

- Type: Deployment
- Replicas: 2
- Container port: 5002
- Service type: ClusterIP
- Internal URL: http://transaction-service:5002

### postgres

- Type: StatefulSet
- Replicas: 1
- Container port: 5432
- Service type: ClusterIP
- Storage: PersistentVolumeClaim

## Configuration Plan

ConfigMap stores non-sensitive values:

- `APP_ENV`
- `LOG_LEVEL`
- `AUTH_SERVICE_PORT`
- `TRANSACTION_SERVICE_PORT`
- `WEB_APP_PORT`
- `AUTH_SERVICE_URL`
- `TRANSACTION_SERVICE_URL`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `SERVICE_TIMEOUT_SECONDS`
- `JWT_EXPIRES_MINUTES`
- `SESSION_COOKIE_SECURE`
- `SESSION_COOKIE_HTTPONLY`
- `SESSION_COOKIE_SAMESITE`

Secret stores local lab sensitive values:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `JWT_SECRET`
- `SECRET_KEY`
- `AUTH_DATABASE_URL`
- `TRANSACTION_DATABASE_URL`

These checked-in Secret values are local placeholders only.

## Ingress Plan

Browser traffic will enter through ingress-nginx.

Expected local access:

- SpendWise: http://spendwise.localhost:8080
- Rancher: https://rancher.localhost:8443

## Image Plan

Kubernetes manifests use the GHCR images produced by the CI/CD pipeline:

- ghcr.io/hashimzaffar/spendwise-web-app:6d5987e8207a48fa22649c34d27c64991c377f21
- ghcr.io/hashimzaffar/spendwise-auth-service:6d5987e8207a48fa22649c34d27c64991c377f21
- ghcr.io/hashimzaffar/spendwise-transaction-service:6d5987e8207a48fa22649c34d27c64991c377f21

For local Kind testing, preload those exact image references into the Kind nodes and set `imagePullPolicy: IfNotPresent`. Avoid `spendwise-*:local` unless those tags are explicitly created and loaded.

## Learning Goals

After this stage, I should understand:

- How Docker Compose maps to Kubernetes
- Why stateless apps use Deployments
- Why Postgres should use StatefulSet and PVC
- Why Services are needed for internal communication
- Why Ingress is needed for browser access
- How Rancher visualizes workloads, services, pods, logs, and namespaces

## Apply Commands

```bash
kubectl apply -k k8s/base
kubectl get pods,svc,ingress,pvc -n spendwise -o wide
```

Layered apply:

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
