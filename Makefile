# run one file with: make test P=utils_test.py
P ?= *_test.py

.PHONY: test
test:
	python -m unittest discover -s tests -p "$(P)"
start: 
	python -m main
stress-start:
	python -m stress_app.main
build:
	rm -rf build && rm -rf dist && rm -rf src/tkinter_devtools.egg-info && python -m build
deploy-test:
	python -m twine \
  	upload \
  	-r testpypi \
  	dist/*
