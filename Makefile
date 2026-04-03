VENV        := .venv
POETRY      := $(VENV)/bin/poetry
PYTHON      := $(VENV)/bin/python
PIP         := $(VENV)/bin/pip
MAZEGEN		:= ./mazegen-1.0.0-py3-none-any.whl
MLX			:= ./mlx/mlx-2.2-py3-none-any.whl
CONFIG      ?= ./config.txt

$(VENV):
	python3 -m venv $(VENV)

$(MAZEGEN): $(VENV)
	$(PIP) install build
	$(PYTHON) -m build --wheel --outdir .

$(POETRY): $(VENV) $(MAZEGEN)
	$(PIP) install --upgrade pip
	$(PIP) install $(MLX)
	$(PIP) install $(MAZEGEN)
	$(PIP) install poetry

.PHONY: install run debug clean lint lint-strict re

build-mazegen: $(POETRY)

install: $(POETRY)
	$(POETRY) install

run: install
	$(POETRY) run python ./a_maze_ing.py $(CONFIG)

debug: install
	$(POETRY) run python -m pdb ./a_maze_ing.py $(CONFIG)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .mypy_cache

fclean: clean
	rm -rf $(VENV)

lint: install
	$(POETRY) run flake8 . --exclude=.venv
	$(POETRY) run mypy . --exclude .venv --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: install
	$(POETRY) run mypy . --exclude .venv --strict
	$(POETRY) run flake8 . --exclude=.venv

re:
	make fclean
	rm -rf $(MAZEGEN)
	make install