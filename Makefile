SHELL := /bin/bash
out_dir ?= ./build
project_slug ?= component-hub
poetry := $(shell command -v poetry 2>/dev/null)


.PHONY: all
all: setup hub

.PHONY: setup
setup:
ifndef poetry
	$(error "Poetry not in path, check installation instructions on https://python-poetry.org/docs/#installation")
endif
	$(poetry) install

.PHONY: hub
hub:
	$(poetry) run component-hub make && \
	cd $(out_dir)/$(project_slug) && \
	git add . && \
	git commit -m "First commit" && \
	make html

.PHONY: clean
clean:
	rm -rf $(out_dir)

###
### Python lints
###
.PHONY: lint lint_flake8 lint_pylint lint_bandit lint_black

RUN_COMMAND = $(poetry) run

lint_flake8:
	$(RUN_COMMAND) flake8 --config pyproject.toml

lint_pylint:
	$(RUN_COMMAND) pylint component_hub

lint_bandit:
	$(RUN_COMMAND) bandit -r component_hub

lint_mypy:
	$(RUN_COMMAND) mypy --ignore-missing-imports component_hub

lint_black:
	$(RUN_COMMAND) black --check .

lint: lint_flake8 lint_pylint lint_bandit lint_mypy lint_black

.PHONY: test
test:
	$(RUN_COMMAND) pytest
