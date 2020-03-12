.PHONY: test
test:
	(cd ./python3 && make)
	./vader_test.sh
