# SpendWise

![SpendWise app screenshot](Screenshot%20from%202026-06-14%2018-57-56.png)

SpendWise is a small full-stack finance app for tracking income, expenses, and balance.

The local setup is Docker-only. One Docker Compose command starts the web app, backend services, and PostgreSQL database.

## Services

| Service | Purpose |
| --- | --- |
| `web-app` | Flask/Jinja browser UI |
| `auth-service` | Signup, login, password hashing, JWT tokens |
| `transaction-service` | Transaction CRUD, filters, totals |
| `postgres` | Database for auth and transactions |

## Requirements

- Docker
- Docker Compose

## Run Locally

Start the full app:

```bash
docker compose up --build
```

Open:

```text
http://localhost:8000
```

Stop:

```bash
docker compose down
```

Reset local database data:

```bash
docker compose down -v
```

## Environment

The app runs with safe local defaults from `docker-compose.yml`.

To customize local settings:

```bash
cp .env.example .env
```

Then edit `.env`.

Do not commit `.env`. Only `.env.example` should be committed.

## Health Checks

After the app starts:

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/ready
```


## Local Quality Checks

Install local dev tools:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Run lint:

```bash
ruff check services scripts
```

Run all local CI checks:

```bash
python3 scripts/ci_check.py
```

Run lint only:

```bash
ruff check services scripts
```

Run syntax checks only:

```bash
PYTHONPYCACHEPREFIX=/tmp/spendwise-pycache python3 -m py_compile services/auth-service/app.py services/transaction-service/app.py services/web-app/app.py scripts/docker_tools.py scripts/ci_check.py
```

Use the Docker helper script:

```bash
python3 scripts/docker_tools.py status
python3 scripts/docker_tools.py health
```

## CI

GitHub Actions runs lint, syntax checks, Docker Compose config validation, and Docker image builds on pushes and pull requests to `main` or `master`.

## Project Structure

```text
SpendWise/
  README.md
  .env.example
  .dockerignore
  .gitignore
  docker-compose.yml
  pyproject.toml
  requirements-dev.txt
  .github/
    workflows/
      ci.yml
  scripts/
    docker_tools.py
    ci_check.py
  database/
    init/
      01-create-spendwise-databases.sql
  services/
    auth-service/
      Dockerfile
      app.py
      requirements.txt
    transaction-service/
      Dockerfile
      app.py
      requirements.txt
    web-app/
      Dockerfile
      app.py
      requirements.txt
      static/
      templates/
```
