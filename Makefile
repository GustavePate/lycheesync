.PHONY: test

test_all:
	python main.py ./tmptest/ /var/www/Lychee/ ./ressources/test_conf.json -v -d


mkdir_test:
	-mkdir ./tmptest

test_min: mkdir_test
	cp -r ./test/mini ./tmptest
	python main.py ./tmptest/ /var/www/Lychee/ ./ressources/test_conf.json -v -d
	rm -rf ./tmptest

test_lang: mkdir_test
	cp -r ./test/Fu* ./tmptest
	python main.py ./tmptest/ /var/www/Lychee/ ./ressources/test_conf.json -v -d
	rm -rf ./tmptest

test_long: mkdir_test
	cp -r ./test/veryveryyveryyveryyveryyveryyveryyveryyveryyveryyveryyver_long_album_namey ./tmptest
	python main.py ./tmptest/ /var/www/Lychee/ ./ressources/test_conf.json -v -d
	rm -rf ./tmptest

test:
	py.test -c ./ressources/pytest.ini  --showlocals  --duration=3 -v  -s --confpath=${PWD}/ressources/test_conf.json

testdev:
	#py.test -c ./ressources/pytest.ini  --showlocals  --duration=3 -v  -s --confpath=${PWD}/ressources/test_conf.json  -k  test_dash_r
	py.test -c ./ressources/pytest.ini  --showlocals  --duration=3 -v  -s --confpath=${PWD}/ressources/test_conf.json  -k  test_album_date

initvenv:
	pip install -r requirements.txt


