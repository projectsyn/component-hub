from pathlib import Path
from typing import List, Optional

import click
import yaml
from github import Github, GithubException
from github.Repository import Repository


class ComponentRepo:
    def __init__(self, r):
        self._repo: Repository = r
        self._has_antora_yml = False
        self._antora_yml: Optional[str] = None
        self._cache_antora_yml()

    @property
    def repo(self) -> Repository:
        return self._repo

    def _cache_antora_yml(self):
        try:
            contents = self.repo.get_contents("docs/antora.yml").decoded_content
            self._antora_yml = yaml.safe_load(contents)
            self._has_antora_yml = True
        except GithubException:
            click.echo(f"No antora.yml found for component {self.repo.name}")

    @property
    def main_branch(self) -> str:
        branches = [b.name for b in self.repo.get_branches()]
        main_branch = "main"
        if "master" in branches:
            main_branch = "master"
        return main_branch

    @property
    def has_antora_yml(self) -> bool:
        return self._has_antora_yml

    @property
    def antora_yml(self) -> Optional[str]:
        return self._antora_yml


class GithubRepoLoader:
    def __init__(self, github_token: str, ignorelist: Optional[Path] = None):
        self._github: Github = Github(github_token)
        self._ignore_list: List[str] = []
        if ignorelist is not None:
            with open(ignorelist) as f:
                self._ignore_list = [
                    item.strip() for item in f.readlines() if not item.startswith("#")
                ]

    def get_commodore_component_repos(self) -> List[ComponentRepo]:
        """
        Get active component repos from search results.
        Filters out repos listed in the ignore-list
        """

        repositories = list(
            self._github.search_repositories(query="topic:commodore-component", sort="updated")
        )

        # Filter out archived repositories
        def active(r):
            return not r.archived

        def non_ignored(r):
            return r.clone_url not in self._ignore_list

        # Return filtered list of repositories
        return [ComponentRepo(r) for r in filter(non_ignored, filter(active, repositories))]
