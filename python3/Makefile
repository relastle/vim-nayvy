.PHONY: test
test:
	flake8 ./nayvy ./tests
	mypy ./nayvy ./tests
	coverage run --omit='./nayvy_vim_if/*,./tests/**/*' --source=. -m pytest -vv --durations=10
	coverage report -m

.PHONY: clean
clean:
	rm -rf ./**/.mypy_cache/
	rm -rf ./**/__pycache__/
