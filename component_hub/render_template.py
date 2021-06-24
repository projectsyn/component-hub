import yaml

from jinja2 import Environment, PackageLoader
from typing import List

from .config import Config, Template
from .github_wrapper import ComponentRepo, GithubRepoLoader


class Renderer:
    def __init__(self, config):
        self._config: Config = config
        self._repositories: List[ComponentRepo] = []

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

    @property
    def repositories(self):
        self._cache_component_repositories()
        return self._repositories

    def render_adoc_template(self, template: Template):
        """
        Render asciidoc template using Jinja2
        """
        components = [r.antora_yml for r in self.repositories]

        jinja_env = Environment(loader=PackageLoader("component_hub", "templates"))
        tpl = jinja_env.get_template(template.template_file)
        output = tpl.render(components=components)
        with open(self._config.output_file(template), "w") as outf:
            outf.write(output)

    def render_yaml_template(self, template: str):
        """
        Render YAML file based on input YAML `template`
        :param template: Input YAML file
        """
        with open(self._config.template_dir / template) as templatef:
            playbook = yaml.safe_load(templatef)

        for repo in self.repositories:
            if repo.repo.organization is not None:
                ghorg = repo.repo.organization.login
            elif repo.repo.owner is not None:
                ghorg = repo.repo.owner.login
            else:
                raise ValueError("Repository {repo.repo.name} has neither organization nor owner")
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
