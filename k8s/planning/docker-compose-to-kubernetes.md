# SpendWise Docker Compose to Kubernetes Plan

## Goal

Convert SpendWise from Docker Compose into a Kubernetes-native local deployment running on kind and managed through Rancher.

## Local Platform

- Host OS: Ubuntu
- Container runtime: Docker
- Kubernetes cluster: kind
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

ConfigMap will store non-sensitive values:

- FLASK_ENV
- AUTH_SERVICE_URL
- TRANSACTION_SERVICE_URL
- POSTGRES_HOST
- POSTGRES_PORT

Secret will store sensitive values:

- POSTGRES_USER
- POSTGRES_PASSWORD
- JWT_SECRET
- FLASK_SECRET_KEY
- Database connection strings if needed

## Ingress Plan

Browser traffic will enter through ingress-nginx.

Expected local access:

- SpendWise: http://localhost:8080 or http://spendwise.localhost:8080
- Rancher: via port-forward or local hostname

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
