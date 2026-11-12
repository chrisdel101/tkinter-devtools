# run one file with: make test P=utils_test.py
P ?= *_test.py

.PHONY: test
test:
	python3 -m unittest discover -s tests -p "$(P)"
start: 
	python3 -m main
