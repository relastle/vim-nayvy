.PHONY: test
test:
	(cd ./python3 && make)
	./vader_test_nvim.sh
	./vader_test_vim.sh
