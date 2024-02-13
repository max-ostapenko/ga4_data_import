# Define variables
VENV_NAME := .venv
PYTHON := python3

.PHONY: docs

env:
	$(PYTHON) -m venv $(VENV_NAME)
	$(VENV_NAME)/bin/$(PYTHON) -m pip install -q -r requirements.txt
	$(VENV_NAME)/bin/$(PYTHON) -m pip install -q -r requirements-dev.txt

lint:
	pylint $(git ls-files '*.py')

build:
	make docs
	python -m build

docs:
	pydoc-markdown
