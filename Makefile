.PHONY: test
test:
	(cd ./python3 && make)
	./test.sh
