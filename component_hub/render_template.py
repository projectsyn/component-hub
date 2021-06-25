from typing import Dict, List, Set

import yaml

from jinja2 import Environment, PackageLoader, select_autoescape

from .config import Config, Template
from .github_wrapper import ComponentRepo, GithubOwner


class Renderer:
    def __init__(self, config, project_syn_orgs):
        self._config: Config = config
        self._repositories: List[ComponentRepo] = []
        self._project_syn_orgs: List[str] = project_syn_orgs

    def _cache_component_repositories(self, refresh=False):
        """
        Fetch and cache list of repositories from GitHub
        """
        if len(self._repositories) == 0 or refresh:
            repositories = self._config.github.get_commodore_component_repos()
            for repo in repositories:
                # Find out the 'docs/antora.yml' file and get its contents
                if repo.has_antora_yml:
                    self._repositories.append(repo)
            self._repositories = sorted(
                self._repositories, key=lambda r: r.antora_yml["title"].lower()
            )

    def _list_organizations(self) -> List[GithubOwner]:
        """
        List owners of repositories. Sorting prefers organizations over individual users.
        :return: sorted iterable
        """
        organizations = set()
        for r in self.repositories:
            organizations.add(r.owner)
        return sorted(organizations)

    def _list_topics(self) -> List[str]:
        """
        List all topics of all repositories
        :return: sorted iterable
        """
        topics: Set[str] = set()
        for r in self.repositories:
            topics = topics.union(set(r.topics))
        return sorted(topics)

    def components_by_org(self) -> Dict[str, List[ComponentRepo]]:
        components: Dict[str, List[ComponentRepo]] = {}
        for r in self.repositories:
            components.setdefault(r.owner.name, []).append(r)
        return components

    def components_by_topic(self) -> Dict[str, List[ComponentRepo]]:
        """
        Organize components by topic
        :return: dict of topic to list of componentrepos
        """
        components: Dict[str, List[ComponentRepo]] = {}
        for r in self.repositories:
            for t in r.topics:
                components.setdefault(t, []).append(r)
        return components

    @property
    def repositories(self):
        self._cache_component_repositories()
        return self._repositories

    def render_adoc_template(self, template: Template):
        """
        Render asciidoc template using Jinja2
        """
        components_by_org = self.components_by_org()
        components_by_topic = self.components_by_topic()
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
            components_by_org=components_by_org,
            components_by_topic=components_by_topic,
            component_count=len(self.repositories),
        )
        with open(self._config.output_file(template), "w") as outf:
            outf.write(output)

    def render_antora_playbook(self):
        """
        Render antora playbook based template playbook which is part of the package.
        """
        with open(self._config.template_dir / "playbook.yml") as templatef:
            playbook = yaml.safe_load(templatef)

        for repo in self.repositories:
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
