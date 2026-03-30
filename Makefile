VENV        := .venv
POETRY      := $(VENV)/bin/poetry
PYTHON      := $(VENV)/bin/python
PIP         := $(VENV)/bin/pip
MAZEGEN		:= ./mazegen-1.0.0-py3-none-any.whl
MLX			:= ./mlx/mlx-2.2-py3-none-any.whl
SRC         := ./src
CONFIG      ?= ./config.txt

$(VENV):
	python3 -m venv $(VENV) --without-pip
	curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
	$(PYTHON) get-pip.py
	rm get-pip.py

$(MAZEGEN): $(VENV)
	$(PIP) install build
	$(PYTHON) -m build --wheel --outdir .

$(POETRY): $(VENV) $(MAZEGEN)
	$(PIP) install --upgrade pip
	$(PIP) install $(MLX)
	$(PIP) install $(MAZEGEN)
	$(PIP) install poetry

.PHONY: install run debug clean lint lint-strict


install: $(POETRY)
	$(POETRY) install

run: install
	$(POETRY) run python $(SRC)/main.py $(CONFIG)

debug: install
	$(POETRY) run python -m pdb $(SRC)/main.py $(CONFIG)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .mypy_cache

fclean: clean
	rm -rf $(VENV)

lint: install
	$(POETRY) run flake8 $(SRC)
	$(POETRY) run mypy $(SRC) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: install
	$(POETRY) run mypy $(SRC) --strict
	$(POETRY) run flake8 $(SRC)
