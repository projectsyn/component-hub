import os
import shutil
from pathlib import Path

from cookiecutter.main import cookiecutter

from component_hub import __install_dir__


def create(root_path, project_slug):
    root = Path(root_path) / project_slug
    docs_path = root / "docs"
    # Uses Cookiecutter to generate a new Antora documentation site
    params = {
        "project_title": "Commodore Components Hub",
        "project_slug": project_slug,
        "project_url": "https://hub.syn.tools",
        "antora_prefix": "hub",
        "antora_theme": "syn",
    }

    cookiecutter(
        "https://github.com/vshn/antora-bootstrap.git",
        no_input=True,
        extra_context=params,
        overwrite_if_exists=True,
        output_dir=root_path,
    )

    # Remove extra files
    os.remove(docs_path / f"{project_slug}.adoc")
    os.remove(root / ".gitlab-ci.yml")
    shutil.rmtree(root / "deployment")
    shutil.rmtree(docs_path / "ebook")

    # Clean unnecessary image assets
    images_path = docs_path / "modules/ROOT/assets/images"
    shutil.rmtree(images_path)
    os.makedirs(images_path)

    # Clean unnecessary documentation pages
    pages_path = docs_path / "modules/ROOT/pages"
    shutil.rmtree(pages_path)
    os.makedirs(pages_path)

    # Copy extra files
    shutil.copyfile(
        __install_dir__ / "assets" / "logo_projectsyn.png",
        f"{images_path}/logo_projectsyn.png",
    )
