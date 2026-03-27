VENV         := .venv
POETRY       := $(VENV)/bin/poetry
PYTHON       := $(VENV)/bin/python
PIP          := $(VENV)/bin/pip
SRC          := src
CONFIG       ?= config_test.txt

$(VENV):
	python3 -m venv $(VENV)

$(POETRY): | $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install poetry

.PHONY: install run debug clean lint lint-strict

install: $(POETRY)
	$(POETRY) install

run: install
	$(POETRY) run python $(SRC)/main.py $(CONFIG)

run-ascii: install
	$(POETRY) run python $(SRC)/main.py $(CONFIG) -a

run-tests: install
	$(POETRY) run python $(SRC)/main.py $(CONFIG) -t

debug: install
	$(POETRY) run python -m pdb $(SRC)/main.py $(CONFIG)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf $(VENV)

lint: install
	$(POETRY) run flake8 $(SRC)
	$(POETRY) run mypy $(SRC)

lint-strict: install
	$(POETRY) run mypy $(SRC) --strict
	$(POETRY) run flake8 $(SRC)
