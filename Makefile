VENV ?= venv
PYTHON ?= $(VENV)/bin/python
PIP ?= $(VENV)/bin/pip
GUNICORN ?= $(VENV)/bin/gunicorn

.PHONY: venv install install-services check-env audit run-local run-auth run-transactions run-web prod-web prod-auth prod-transactions docker-build docker-build-auth docker-build-transactions docker-build-web docker-run-auth docker-run-transactions docker-run-web compose-config compose-up compose-down compose-logs compose-ps check test build

venv:
	python3 -m venv $(VENV)

install: venv
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

install-services: venv
	$(VENV)/bin/pip install -r services/auth-service/requirements.txt
	$(VENV)/bin/pip install -r services/transaction-service/requirements.txt
	$(VENV)/bin/pip install -r services/web-app/requirements.txt

check-env:
	$(PYTHON) scripts/check_env.py

audit:
	$(PYTHON) scripts/project_audit.py

run-local:
	$(PYTHON) scripts/run_local.py

run-auth:
	$(PYTHON) services/auth-service/app.py

run-transactions:
	$(PYTHON) services/transaction-service/app.py

run-web:
	$(PYTHON) services/web-app/app.py

prod-web:
	cd services/web-app && ../../$(GUNICORN) --bind 0.0.0.0:$${WEB_APP_PORT:-5000} app:app

prod-auth:
	cd services/auth-service && ../../$(GUNICORN) --bind 0.0.0.0:$${AUTH_SERVICE_PORT:-5001} app:app

prod-transactions:
	cd services/transaction-service && ../../$(GUNICORN) --bind 0.0.0.0:$${TRANSACTION_SERVICE_PORT:-5002} app:app

docker-build: docker-build-auth docker-build-transactions docker-build-web

docker-build-auth:
	docker build -t spendwise-auth-service -f services/auth-service/Dockerfile .

docker-build-transactions:
	docker build -t spendwise-transaction-service -f services/transaction-service/Dockerfile .

docker-build-web:
	docker build -t spendwise-web-app -f services/web-app/Dockerfile .

docker-run-auth:
	docker run --rm --network host --env-file .env spendwise-auth-service

docker-run-transactions:
	docker run --rm --network host --env-file .env spendwise-transaction-service

docker-run-web:
	docker run --rm --network host --env-file .env spendwise-web-app

compose-config:
	docker compose config

compose-up:
	docker compose up --build

compose-down:
	docker compose down

compose-logs:
	docker compose logs -f

compose-ps:
	docker compose ps

check:
	$(PYTHON) -m py_compile scripts/check_env.py
	$(PYTHON) -m py_compile scripts/project_audit.py
	$(PYTHON) -m py_compile scripts/run_local.py
	$(PYTHON) -m py_compile services/auth-service/app.py
	$(PYTHON) -m py_compile services/transaction-service/app.py
	$(PYTHON) -m py_compile services/web-app/app.py

test: check
	@echo "No automated tests yet. Service syntax checks passed."

build:
	@echo "No build step required for this server-rendered Flask app."
