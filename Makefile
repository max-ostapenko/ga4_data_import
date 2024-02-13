.PHONY: docs

env:
	pip install -q -r requirements.txt
	pip install -q -r requirements-dev.txt

lint:
	pylint ga4_data_import/
	black .
	flake8 --extend-ignore F401,E501 ga4_data_import/
	yamllint -d relaxed .
	mypy .
	isort .

build:
	make docs
	python -m build

docs:
	pydoc-markdown
