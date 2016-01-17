.PHONY: test

test_all:
	python main.py ./tmptest/ /var/www/Lychee/ ./ressources/test_conf.json -v -d

test:
	coverage run -m --source ./lycheesync py.test -c ./ressources/pytest.ini  --showlocals  --duration=3 -v  -s --confpath=${PWD}/ressources/test_conf.json
	# py.test -c ./ressources/pytest.ini  --showlocals  --duration=3 -v  -s --confpath=${PWD}/ressources/test_conf.json

testdev:
	coverage run -m --source ./lycheesync py.test -c ./ressources/pytest.ini  --showlocals  --duration=3 -v  -s --confpath=${PWD}/ressources/test_conf.json  -k sanity 

initvenv:
	pip install -r requirements.txt


