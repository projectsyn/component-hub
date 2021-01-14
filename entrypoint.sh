#!/bin/sh

python create-antora-site.py
GITHUB_TOKEN=$GITHUB_TOKEN python generate-nav.py > commodore-components-hub/docs/modules/ROOT/nav.adoc
GITHUB_TOKEN=$GITHUB_TOKEN python generate-index.py > commodore-components-hub/docs/modules/ROOT/pages/index.adoc
GITHUB_TOKEN=$GITHUB_TOKEN python generate-playbook.py > commodore-components-hub/playbook.yml
cd commodore-components-hub || exit
git add .
git commit -m "First commit"
make html
