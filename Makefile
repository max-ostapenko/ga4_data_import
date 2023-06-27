.PHONY: docs
docs:
	-rm -rf docs/
	pydoc-markdown

.PHONY: build
build: docs
	-rm -rf dist/ build/
	python3 -m build --wheel .

.PHONY: release
release: docs build
	@echo "This target will upload a new release to PyPi hosting."
	@echo "Are you sure you want to proceed? (yes/no)"
	@read yn; if [ yes -ne $(yn) ]; then exit 1; fi
	@echo "Here we go..."
	twine upload dist/*

