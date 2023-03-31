.PHONY: all prepare-dev venv lint test run shell clean build install docker
SHELL=/bin/bash

all:
	@echo "make test"
	@echo "    Run tests on project."
	@echo "make install"
	@echo "    Installs package in your system."

install: venv
	pip --version && pip install app

test: venv
	python3 -m unittest discover -s app

