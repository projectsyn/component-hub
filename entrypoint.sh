#!/bin/sh

python create-antora-site.py
python generate-nav.py > commodore-components-hub/docs/modules/ROOT/nav.adoc
python generate-index.py > commodore-components-hub/docs/modules/ROOT/pages/index.adoc
python generate-playbook.py > commodore-components-hub/playbook.yml
cd commodore-components-hub || exit
git add .
git commit -m "First commit"
make html
