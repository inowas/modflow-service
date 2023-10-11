.SILENT:
.PHONY: all prepare-dev venv lint test run shell clean build install docker help
SHELL=/bin/bash

# Based on https://gist.github.com/prwhite/8168133#comment-1313022

## This help screen
help:
	printf "Available commands\n\n"
	awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "%-40s -- %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)


## Install development environment
install: venv
	pip --version && pip install -r app/requirements.txt

## Start development environment
start-local:
	docker compose -f docker-compose.dev.local.yml up -d

## Stop development environment
stop:
	docker compose down

test: venv
	python3 -m unittest discover -s app

