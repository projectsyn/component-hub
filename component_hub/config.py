from enum import Enum
from pathlib import Path
from typing import List, Optional

from component_hub import __install_dir__
from .github_wrapper import GithubRepoLoader


class Template(Enum):
    INDEX = Path("ROOT") / "pages" / "index.adoc"
    NAV = Path("ROOT") / "nav.adoc"

    @property
    def template_file(self):
        # pylint: disable=no-member
        return f"{self.value.name}.jinja2"


class Config:
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        github_token: str,
        root_path: str,
        project_slug: str,
        ignore_topics: List[str],
        ignorelist: Optional[Path] = None,
    ):
        self._root_path = root_path
        self._project_slug = project_slug
        self._github = GithubRepoLoader(
            github_token, ignorelist=ignorelist, ignore_topics=ignore_topics
        )

    @property
    def github(self):
        return self._github

    @property
    def root_path(self) -> str:
        return self._root_path

    @property
    def project_slug(self) -> str:
        return self._project_slug

    @property
    def output_dir(self) -> Path:
        return Path(self.root_path) / self.project_slug

    @property
    def module_dir(self) -> Path:
        return self.output_dir / "docs" / "modules"

    def output_file(self, template: Template) -> Path:
        return self.module_dir / template.value

    @property
    def template_dir(self) -> Path:
        return __install_dir__ / "templates"

    @property
    def antora_playbook_yml(self) -> Path:
        return self.output_dir / "playbook.yml"
