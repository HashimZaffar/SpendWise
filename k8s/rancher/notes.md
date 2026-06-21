# Rancher Local Learning Notes

## Goal

Use Rancher as a Kubernetes management UI for the local Kind cluster.

## Current Setup

Rancher is installed inside the same Kind cluster used for the SpendWise local lab.

| Item | Value |
| --- | --- |
| Cluster | `spendwise-lab` |
| Rancher namespace | `cattle-system` |
| Rancher hostname | `rancher.localhost` |
| Local URL | `https://rancher.localhost:8443` |
| Local bootstrap password | `admin12345` |

## Required Components

- ingress-nginx
- cert-manager
- Rancher Helm chart

## Namespaces

- ingress-nginx
- cert-manager
- cattle-system
- spendwise

## Access Method

Access uses the Kind HTTPS port mapping:

```text
https://rancher.localhost:8443
```

The Rancher certificate is self-signed in this local lab, so the browser will show a certificate warning.

Verify from the CLI:

```bash
curl -k -I --resolve rancher.localhost:8443:127.0.0.1 https://rancher.localhost:8443
```

## Learning Tasks

- View nodes
- View namespaces
- View workloads
- View pods
- View services
- View ingress
- View logs
- Open pod shell
- Restart deployment
- Scale deployment
- Inspect events
- Compare Rancher views with `kubectl get pods,svc,ingress -n spendwise`
