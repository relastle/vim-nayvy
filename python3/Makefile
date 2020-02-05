.PHONY: test
test:
	flake8 .
	mypy --ignore-missing-imports --follow-imports=skip --strict-optional --disallow-untyped-defs --disallow-untyped-calls .
	python3 -m pytest -v

.PHONY: clean
clean:
	rm -rf **/.mypy_cache
