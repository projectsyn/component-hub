#!/bin/sh

OUT_DIR="${OUT_DIR:-build}"
PROJECT_SLUG="${PROJECT_SLUG:-commodore-components-hub}"

python create-antora-site.py --path "$OUT_DIR" --slug "$PROJECT_SLUG"
GITHUB_TOKEN=$GITHUB_TOKEN python generate-nav.py > "$OUT_DIR"/"$PROJECT_SLUG"/docs/modules/ROOT/nav.adoc
GITHUB_TOKEN=$GITHUB_TOKEN python generate-index.py > "$OUT_DIR"/"$PROJECT_SLUG"/docs/modules/ROOT/pages/index.adoc
GITHUB_TOKEN=$GITHUB_TOKEN python generate-playbook.py > "$OUT_DIR"/"$PROJECT_SLUG"/playbook.yml
cd "$OUT_DIR"/"$PROJECT_SLUG" || exit
git add .
git commit -m "First commit"
