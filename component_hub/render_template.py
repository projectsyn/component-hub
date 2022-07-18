from typing import Dict, List, Set

import yaml
import click

from jinja2 import Environment, PackageLoader, select_autoescape

from .config import Config, Template
from .github_wrapper import Repo, GithubOwner


def _filter_antora_repos(repositories: List[Repo]):
    res: List[Repo] = []
    for repo in repositories:
        # Find out the 'docs/antora.yml' file and get its contents
        if repo.has_antora_yml:
            res.append(repo)
    return sorted(res, key=lambda r: r.title.lower())


class Renderer:
    def __init__(self, config, project_syn_orgs):
        self._config: Config = config
        self._component_repositories: List[Repo] = []
        self._package_repositories: List[Repo] = []
        self._project_syn_orgs: List[str] = project_syn_orgs

        self._cached: bool = False

    def _deduplicate_repositories(self):
        uniq: dict[str, Repo] = {}
        for r in self._component_repositories + self._package_repositories:
            if r.name not in uniq or (
                r.owner.name in self._project_syn_orgs
                and uniq[r.name].owner.name not in self._project_syn_orgs
            ):
                uniq[r.name] = r

        def keep(r: Repo):
            if uniq[r.name] != r:
                click.echo(
                    f"Dropping {r.github_full_name} in favour of {uniq[r.name].github_full_name}"
                )
                return False
            return True

        self._component_repositories = list(filter(keep, self._component_repositories))
        self._package_repositories = list(filter(keep, self._package_repositories))

    def _cache_repositories(self, refresh=False):
        """
        Fetch and cache list of component repositories from GitHub
        """
        if not self._cached or refresh:
            self._cached = True
            self._component_repositories = _filter_antora_repos(
                self._config.github.get_commodore_component_repos()
            )
            self._package_repositories = _filter_antora_repos(
                self._config.github.get_commodore_package_repos()
            )
            self._deduplicate_repositories()

    def _list_organizations(self) -> List[GithubOwner]:
        """
        List owners of repositories. Sorting prefers organizations over individual users.
        :return: sorted iterable
        """
        organizations = set()
        for r in self.component_repositories + self.package_repositories:
            organizations.add(r.owner)
        return sorted(organizations)

    def _list_topics(self) -> List[str]:
        """
        List all topics of all repositories
        :return: sorted iterable
        """
        topics: Set[str] = set()
        for r in self.component_repositories + self.package_repositories:
            topics = topics.union(set(r.topics))
        return sorted(topics)

    def components_by_org(self) -> Dict[str, List[Repo]]:
        components: Dict[str, List[Repo]] = {}
        for r in self.component_repositories:
            components.setdefault(r.owner.name, []).append(r)
        return components

    def packages_by_org(self) -> Dict[str, List[Repo]]:
        packages: Dict[str, List[Repo]] = {}
        for r in self.package_repositories:
            packages.setdefault(r.owner.name, []).append(r)
        return packages

    def components_by_topic(self) -> Dict[str, List[Repo]]:
        """
        Organize components by topic
        :return: dict of topic to list of componentrepos
        """
        components: Dict[str, List[Repo]] = {}
        for r in self.component_repositories:
            for t in r.topics:
                components.setdefault(t, []).append(r)
        return components

    def packages_by_topic(self) -> Dict[str, List[Repo]]:
        """
        Organize packages by topic
        :return: dict of topic to list of packagerepos
        """
        packages: Dict[str, List[Repo]] = {}
        for r in self.package_repositories:
            for t in r.topics:
                packages.setdefault(t, []).append(r)
        return packages

    @property
    def component_repositories(self):
        self._cache_repositories()
        return self._component_repositories

    @property
    def package_repositories(self):
        self._cache_repositories()
        return self._package_repositories

    def render_adoc_template(self, template: Template):
        """
        Render asciidoc template using Jinja2
        """
        components_by_org = self.components_by_org()
        packages_by_org = self.packages_by_org()
        components_by_topic = self.components_by_topic()
        packages_by_topic = self.packages_by_topic()
        organizations = self._list_organizations()

        syn_organizations = [o for o in organizations if o.name in self._project_syn_orgs]
        other_organizations = [o for o in organizations if o.name not in self._project_syn_orgs]

        jinja_env = Environment(
            loader=PackageLoader("component_hub", "templates"),
            autoescape=select_autoescape(["html"]),
        )

        tpl = jinja_env.get_template(template.template_file)
        output = tpl.render(
            syn_organizations=syn_organizations,
            other_organizations=other_organizations,
            topics=self._list_topics(),
            packages_by_org=packages_by_org,
            packages_by_topic=packages_by_topic,
            package_count=len(self.package_repositories),
            components_by_org=components_by_org,
            components_by_topic=components_by_topic,
            component_count=len(self.component_repositories),
        )
        with open(self._config.output_file(template), "w") as outf:
            outf.write(output)

    def render_antora_playbook(self):
        """
        Render antora playbook based template playbook which is part of the package.
        """
        with open(self._config.template_dir / "playbook.yml") as templatef:
            playbook = yaml.safe_load(templatef)

        for repo in self.component_repositories + self.package_repositories:
            ghorg = repo.owner.name
            playbook["content"]["sources"].append(
                {
                    "branches": repo.main_branch,
                    "start_path": "docs",
                    "url": repo.repo.clone_url,
                    "edit_url": f"https://github.com/{ghorg}/{repo.repo.name}/edit/{repo.main_branch}/{{path}}",
                }
            )

        with open(self._config.antora_playbook_yml, "w") as outf:
            yaml.safe_dump(playbook, outf)
