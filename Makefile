.PHONY: test
test:
	(cd ./python3 && make)
	./test_vader.sh
