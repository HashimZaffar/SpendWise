# Rancher Local Learning Plan

## Goal

Use Rancher as a Kubernetes management UI for the local kind cluster.

## Initial Setup

Rancher will be installed inside the same kind cluster for learning.

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

Initial access will use kubectl port-forward.

Later access may use local hostname and ingress.

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