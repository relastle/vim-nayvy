.PHONY: test
test:
	flake8 ./nayvy ./nayvy_vim_if ./tests ./pivmy
	mypy --cache-dir /dev/null ./nayvy ./nayvy_vim_if ./tests ./pivmy
	coverage run --omit='./nayvy_vim_if/*,./tests/**/*' --source=. -m pytest -vv --durations=10 --diff-type=split
	coverage report -m

.PHONY: clean
clean:
	rm -rf ./**/.mypy_cache/
	rm -rf ./**/__pycache__/
