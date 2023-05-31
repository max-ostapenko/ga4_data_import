.PHONY: build
build:
	-rm -rf dist/
	-sudo rm -rf dist/
	python3 -m build --wheel .

.PHONY: release
release: build
	@echo "This target will upload a new release to PyPi hosting."
	@echo "Are you sure you want to proceed? (yes/no)"
	@read yn; if [ yes -ne $(yn) ]; then exit 1; fi
	@echo "Here we go..."
	twine upload dist/*
