# Define variables
VENV_NAME := .venv
PYTHON := python3
REQUIREMENTS := requirements.txt

.PHONY: docs

env:
	$(PYTHON) -m venv $(VENV_NAME)
	$(VENV_NAME)/bin/$(PYTHON) -m pip install -q -r $(REQUIREMENTS)

lint:
	pip install pylint
    pylint $(git ls-files '*.py')

build:
	pip install build
    python -m build

docs:
	pydoc-markdown
