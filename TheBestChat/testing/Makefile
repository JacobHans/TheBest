
all: init test clean

init:
	sudo pip install -r requirements.txt

test:
	py.test --cov-report term-missing --cov=tests

coverage:
	 py.test --cov-report html --cov=tests
	 
clean: 
	rm tutorial.db

.PHONY: all init test clean
