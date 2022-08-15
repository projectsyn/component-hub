from pathlib import Path
from typing import List, Optional, Set, Union

import click
import yaml
from github import Github, GithubException
from github.Repository import Repository
from github.Organization import Organization
from github.NamedUser import NamedUser

from profanity_check import predict


class GithubOwner:
    def __init__(self, owner: Union[Organization, NamedUser]):
        self._owner = owner

    @property
    def name(self):
        return self._owner.login

    @property
    def is_organization(self):
        return isinstance(self._owner, Organization)

    @property
    def is_user(self):
        return not self.is_organization

    @property
    def display_name(self):
        return self._owner.name

    @property
    def github_url(self):
        return self._owner.html_url

    def __eq__(self, other):
        return self._owner.login == other._owner.login

    def __lt__(self, other):
        """
        Ordering: Orgs before Users, alphabetical otherwise
        """
        if (self.is_organization and other.is_organization) or (self.is_user and other.is_user):
            return self._owner.login < other._owner.login

        # from here: self and other are not both the same type
        if self.is_organization:
            return True

        return False

    def __hash__(self):
        return hash(self._owner.login)

    def __repr__(self):
        return f"{self.name}({self.display_name})"


class Repo:
    def __init__(self, r: Repository, ignore_topics: List[str]):
        self._repo: Repository = r
        self._has_antora_yml = False
        self._antora_yml: Optional[str] = None
        self._topics: Optional[List[str]] = None
        self._ignore_topics = set(ignore_topics)
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
            click.echo(f"No antora.yml found for {self.repo.name}")

    @property
    def main_branch(self) -> str:
        return self.repo.default_branch

    @property
    def has_antora_yml(self) -> bool:
        return self._has_antora_yml

    @property
    def antora_yml(self) -> Optional[str]:
        return self._antora_yml

    @property
    def title(self):
        if "title" in self._antora_yml:
            return self._antora_yml["title"]
        if "name" in self._antora_yml:
            return self._antora_yml["name"]

        return self.repo.name

    @property
    def name(self):
        if "name" in self._antora_yml:
            return self._antora_yml["name"]

        return self.repo.name

    @property
    def description(self):
        if self.repo.description is None:
            return "—"
        return self.repo.description

    @property
    def github_url(self):
        """
        :return: Link to repo on GitHub
        """
        return self.repo.html_url

    @property
    def github_full_name(self):
        """
        :return: Repo name including org
        """
        return self.repo.full_name

    @property
    def topics(self):
        """
        Returns topics of repo.
        Removes topics provided in `self._ignore_topics`
        Removes topics that profanity-check detects as profanitites.
        :return: topics of repository
        """
        if self._topics is None:
            _topics: Set[str] = set(self.repo.get_topics())
            topics: List[str] = sorted(_topics - self._ignore_topics)
            self._topics = []
            if len(topics) > 0:
                profanity: List[int] = predict(topics)
                for t, p in zip(topics, profanity):
                    if p == 0:
                        self._topics.append(t)
                    else:
                        click.echo(
                            f"Profanity filter triggered for topic `{t}` on '{self.github_full_name}'"
                            + ", dropping the topic"
                        )
        return self._topics

    @property
    def owner(self) -> GithubOwner:
        """
        :return: Owner (User or Org) of repo
        """
        if self.repo.organization is not None:
            return GithubOwner(self.repo.organization)
        if self.repo.owner is not None:
            return GithubOwner(self.repo.owner)

        raise ValueError(f"Repository {self.repo.name} has neither organization nor owner")


class GithubRepoLoader:
    def __init__(
        self,
        github_token: str,
        ignore_topics: List[str],
        ignorelist: Optional[Path] = None,
    ):
        self._github: Github = Github(github_token)
        self._ignore_list: List[str] = []
        self._ignore_topics = ignore_topics
        if ignorelist is not None:
            with open(ignorelist, encoding="utf-8") as f:
                self._ignore_list = [
                    item.strip() for item in f.readlines() if not item.startswith("#")
                ]

    def get_commodore_repos(self, query: str) -> List[Repo]:

        """
        Get active repos from search results.
        Filters out repos listed in the ignore-list
        """

        repositories: List[Repository] = list(
            self._github.search_repositories(query=query, sort="updated")
        )

        # Filter out archived repositories
        def active(r):
            if r.archived:
                click.echo(f"Skipping archived repository {r.full_name}")
                return False

            return True

        def non_ignored(r):
            if r.clone_url in self._ignore_list:
                click.echo(f"Dropping repository {r.full_name} on ignore list")
                return False

            return True

        def non_profane(r):
            # drop repo names which are detected as profanities
            rp = predict([r.full_name])[0]
            if rp == 1:
                click.echo("Profanity filter triggered for repo {r.full_name}, dropping repository")
                return False

            return True

        # Return filtered list of repositories
        return [
            Repo(r, self._ignore_topics)
            for r in filter(non_profane, filter(non_ignored, filter(active, repositories)))
        ]

    def get_commodore_component_repos(self) -> List[Repo]:
        return self.get_commodore_repos("topic:commodore-component")

    def get_commodore_package_repos(self) -> List[Repo]:
        return self.get_commodore_repos("topic:commodore-package")
