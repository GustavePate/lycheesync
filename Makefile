
test_all:
	python main.py ./test/ /var/www/lycheetest/ testconf.json -v -d


mkdir_test:
	-mkdir ./tmptest

test_min: mkdir_test
	cp -r ./test/mini ./tmptest
	python main.py ./tmptest/ /var/www/lycheetest/ testconf.json -v -d
	rm -rf ./tmptest

test_lang: mkdir_test
	cp -r ./test/Fu* ./tmptest
	python main.py ./tmptest/ /var/www/lycheetest/ testconf.json -v -d
	rm -rf ./tmptest

test_long: mkdir_test
	cp -r ./test/veryveryyveryyveryyveryyveryyveryyveryyveryyveryyveryyver_long_album_namey ./tmptest
	python main.py ./tmptest/ /var/www/lycheetest/ testconf.json -v -d
	rm -rf ./tmptest


