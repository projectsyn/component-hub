SHELL := /bin/bash
out_dir ?= ./build
project_slug ?= commodore-components-hub

all: hub

.PHONY: hub
hub:
	python3 create-antora-site.py --path $(out_dir) --slug $(project_slug)
	GITHUB_TOKEN=$(GITHUB_TOKEN) python3 generate-nav.py > $(out_dir)/$(project_slug)/docs/modules/ROOT/nav.adoc && \
	GITHUB_TOKEN=$(GITHUB_TOKEN) python3 generate-index.py > $(out_dir)/$(project_slug)/docs/modules/ROOT/pages/index.adoc && \
	GITHUB_TOKEN=$(GITHUB_TOKEN) python3 generate-playbook.py > $(out_dir)/$(project_slug)/playbook.yml && \
	cd $(out_dir)/$(project_slug) && \
	git add . && \
	git commit -m "First commit" && \
	make html

.PHONY: clean
clean:
	rm -rf $(out_dir)
