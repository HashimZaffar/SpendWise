VENV ?= venv
PYTHON ?= $(VENV)/bin/python
PIP ?= $(VENV)/bin/pip
GUNICORN ?= $(VENV)/bin/gunicorn

.PHONY: venv install install-services init-db run run-auth run-transactions run-web prod-web prod-auth prod-transactions check check-services test build

venv:
	python3 -m venv $(VENV)

install: venv
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

install-services: venv
	$(VENV)/bin/pip install -r services/auth-service/requirements.txt
	$(VENV)/bin/pip install -r services/transaction-service/requirements.txt
	$(VENV)/bin/pip install -r services/web-app/requirements.txt

init-db:
	$(PYTHON) -c "from app import initialize_local_database; initialize_local_database()"

run:
	$(PYTHON) app.py

run-auth:
	$(PYTHON) services/auth-service/app.py

run-transactions:
	$(PYTHON) services/transaction-service/app.py

run-web:
	$(PYTHON) services/web-app/app.py

prod:
	$(GUNICORN) --bind 0.0.0.0:$${APP_PORT:-5000} app:app

prod-web:
	cd services/web-app && ../../$(GUNICORN) --bind 0.0.0.0:$${WEB_APP_PORT:-5000} app:app

prod-auth:
	cd services/auth-service && ../../$(GUNICORN) --bind 0.0.0.0:$${AUTH_SERVICE_PORT:-5001} app:app

prod-transactions:
	cd services/transaction-service && ../../$(GUNICORN) --bind 0.0.0.0:$${TRANSACTION_SERVICE_PORT:-5002} app:app

check:
	$(PYTHON) -m py_compile app.py

check-services:
	$(PYTHON) -m py_compile services/auth-service/app.py
	$(PYTHON) -m py_compile services/transaction-service/app.py
	$(PYTHON) -m py_compile services/web-app/app.py

test: check check-services
	$(PYTHON) -c "import app; print('Import check passed.')"
	@echo "No automated tests yet. Syntax and import checks passed."

build:
	@echo "No build step required for this server-rendered Flask app."
