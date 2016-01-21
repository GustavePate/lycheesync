.PHONY: test

test_all:
	python main.py ./tmptest/ /var/www/Lychee/ ./ressources/test_conf.json -v -d

test:
	py.test -c ./ressources/pytest.ini --cov=lycheesync --pep8 --showlocals  --duration=3 -v  -s --confpath=${PWD}/ressources/test_conf.json --cov-report term-missing
	# py.test -c ./ressources/pytest.ini  --showlocals  --duration=3 -v  -s --confpath=${PWD}/ressources/test_conf.json

testdev:
	py.test -c ./ressources/pytest.ini --cov=lycheesync --pep8  --showlocals  --duration=3 -v  -s --confpath=${PWD}/ressources/test_conf.json  -k corrupted


