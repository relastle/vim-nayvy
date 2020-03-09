.PHONY: test
test:
	flake8 .
	mypy --ignore-missing-imports --follow-imports=skip --strict-optional --disallow-untyped-defs --disallow-untyped-calls .
	coverage run --source=. -m pytest -vv --durations=10
	coverage report -m

.PHONY: clean
clean:
	rm -rf **/.mypy_cache
	rm -rf **/__pycache__
