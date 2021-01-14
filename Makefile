SHELL := /bin/bash

all: hub

.venv:
	python3 -m venv .venv && \
	source .venv/bin/activate && \
	pip install -r requirements.txt

commodore-components-hub: .venv
	python3 create-antora-site.py

.PHONY: hub
hub: commodore-components-hub
	GITHUB_TOKEN=$(GITHUB_TOKEN) python3 generate-nav.py > commodore-components-hub/docs/modules/ROOT/nav.adoc && \
	GITHUB_TOKEN=$(GITHUB_TOKEN) python3 generate-index.py > commodore-components-hub/docs/modules/ROOT/pages/index.adoc && \
	GITHUB_TOKEN=$(GITHUB_TOKEN) python3 generate-playbook.py > commodore-components-hub/playbook.yml && \
	cd commodore-components-hub && \
	git add . && \
	git commit -m "First commit" && \
	make html

.PHONY: clean
clean:
	rm -rf commodore-components-hub
