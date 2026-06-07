VENV ?= venv
PYTHON ?= $(VENV)/bin/python
PIP ?= $(VENV)/bin/pip
GUNICORN ?= $(VENV)/bin/gunicorn

.PHONY: venv install init-db run prod check test build

venv:
	python3 -m venv $(VENV)

install: venv
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

init-db:
	$(PYTHON) -c "from app import initialize_local_database; initialize_local_database()"

run:
	$(PYTHON) app.py

prod:
	$(GUNICORN) --bind 0.0.0.0:$${APP_PORT:-5000} app:app

check:
	$(PYTHON) -m py_compile app.py

test: check
	$(PYTHON) -c "import app; print('Import check passed.')"
	@echo "No automated tests yet. Syntax and import checks passed."

build:
	@echo "No build step required for this server-rendered Flask app."
