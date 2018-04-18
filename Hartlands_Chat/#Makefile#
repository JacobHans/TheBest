
all: init test 

init:
	sudo pip install -r requirements.txt

test:
	py.test --cov-report term-missing --cov=tests

coverage:
	 py.test --cov-report html --cov=tests

.PHONY: all init test
