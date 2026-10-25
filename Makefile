VENV := .venv
BIN := $(VENV)/bin

.PHONY: all install-deps run test lint build-deb build-aur clean

all: install-deps

$(VENV)/bin/python:
	python3 -m venv $(VENV)

install-deps: $(VENV)/bin/python
	$(BIN)/pip install --quiet --upgrade pip ruff mypy pytest pre-commit commitizen

setup-hooks:
	$(BIN)/pre-commit install
	$(BIN)/pre-commit install --hook-type commit-msg

run-hooks:
	$(BIN)/pre-commit run --all-files

run:
	python3 src/main.py

test:
	pytest

lint:
	$(BIN)/ruff check src tests
	$(BIN)/mypy

build-deb:
	./packaging/build_deb.sh 1.0.0

build-aur:
	cd packaging && makepkg -sf

clean:
	rm -rf $(VENV) .pytest_cache
