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
	poetry install

.PHONY: hub
hub:
	poetry run component-hub make && \
	cd $(out_dir)/$(project_slug) && \
	git add . && \
	git commit -m "First commit" && \
	make html

.PHONY: clean
clean:
	rm -rf $(out_dir)
