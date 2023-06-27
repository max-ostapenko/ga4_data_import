.PHONY: docs
docs:
	-rm -rf docs/
	pydoc-markdown
