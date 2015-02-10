
test_all:
	python main.py ./test/ /var/www/lycheetest/ testconf.json -v -d

test_min:
	-mkdir ./tmptest
	cp -r ./test/mini ./tmptest
	python main.py ./tmptest/ /var/www/lycheetest/ testconf.json -v -d
	rm -rf ./tmptest



