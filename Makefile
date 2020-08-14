.PHONY: test
test:
	vint ./plugin ./autoload
	(cd ./python3 && make)
	./vader_test_nvim.sh
	# ./vader_test_vim.sh
