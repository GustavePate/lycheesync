.PHONY: test

test_all:
	python main.py ./tmptest/ /var/www/Lychee/ ./ressources/test_conf.json -v -d

test:
	py.test -c ./ressources/pytest.ini  --showlocals  --duration=3 -v  -s --confpath=${PWD}/ressources/test_conf.json

testdev:
	py.test -c ./ressources/pytest.ini  --showlocals  --duration=3 -v  -s --confpath=${PWD}/ressources/test_conf.json  -k test_sha1

initvenv:
	pip install -r requirements.txt


