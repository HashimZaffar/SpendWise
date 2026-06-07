.PHONY: install run check test build

install:
	python3 -m pip install -r requirements.txt

run:
	python3 app.py

check:
	python3 -m py_compile app.py

test: check
	@echo "No automated tests yet. Syntax check passed."

build:
	@echo "No build step required for this server-rendered Flask app."
