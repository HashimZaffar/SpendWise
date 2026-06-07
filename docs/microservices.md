# Microservices Guide

This document explains the SpendWise microservices setup in simple terms.

## What Changed

Before, SpendWise was mostly one Flask app in `app.py`.

Now, it is split into smaller services:

```text
web-app
auth-service
transaction-service
```

This means each service has a clear job.

## Service Responsibilities

### `web-app`

This is what the user opens in the browser.

It handles:

- HTML pages
- CSS
- login/signup forms
- dashboard form
- browser sessions
- CSRF protection

It does not directly save users or transactions in a database.

### `auth-service`

This service handles identity.

It owns:

- user signup
- user login
- password hashing
- JWT token creation
- `/me` endpoint

It uses its own PostgreSQL database.

### `transaction-service`

This service handles money records.

It owns:

- create transaction
- list transactions
- edit transaction
- delete transaction
- search/filter
- income, expense, and balance totals

It uses its own PostgreSQL database.

## Why This Is Microservices

This is microservices because:

- Code is split into independent services.
- Each service has one main responsibility.
- Auth and transactions have separate databases.
- Services talk over HTTP APIs.
- The services can run as separate local Python processes.
- Each service has its own health/readiness endpoints.

## Local URLs

| URL | Service |
| --- | --- |
| `http://127.0.0.1:5000` | web app |
| `http://127.0.0.1:5001` | auth API |
| `http://127.0.0.1:5002` | transaction API |

## End-to-End Request Example

When a user adds an expense:

```text
Browser
  -> web-app receives form
  -> web-app checks CSRF token
  -> web-app sends JWT + JSON to transaction-service
  -> transaction-service validates JWT
  -> transaction-service saves expense in its own database
  -> web-app shows updated dashboard
```
