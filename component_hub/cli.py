import os
from pathlib import Path

import click
from dotenv import load_dotenv

from component_hub import __git_version__, __version__
from .config import Config, Template
from .antora_site import create
from .render_template import Renderer


def _version():
    if f"v{__version__}" != __git_version__:
        return f"{__version__} (Git version: {__git_version__})"
    return __version__


# pylint: disable=too-few-public-methods
class Context:
    def __init__(self, config: Config, renderer: Renderer):
        self.config = config
        self.renderer = renderer


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(_version(), prog_name="component-hub")
@click.option(
    "--github-token",
    envvar="GITHUB_TOKEN",
    help="GitHub API token",
    metavar="GITHUB_TOKEN",
)
@click.pass_context
@click.option("--root", help="Root directory for generated files", default="build")
@click.option(
    "--slug",
    help="directory name for the generated Antora project",
    default="component-hub",
)
@click.option(
    "--ignore-list",
    help="File listing clone URLs of repositories to ignore",
    default=None,
)
@click.option(
    "--project-syn-orgs",
    help="List GitHub organizations which are officially supported",
    default=("appuio", "projectsyn", "vshn"),
    multiple=True,
)
@click.option(
    "--ignore-topics",
    help="List of project topics which are not considered for sorting by topic",
    default=("commodore", "commodore-component", "syn", "projectsyn"),
    multiple=True,
)
# pylint: disable=too-many-arguments
def component_hub(ctx, github_token, root, slug, ignore_list, project_syn_orgs, ignore_topics):
    cfg = Config(
        github_token=github_token,
        root_path=root,
        project_slug=slug,
        ignorelist=ignore_list,
        ignore_topics=ignore_topics,
    )
    r = Renderer(cfg, list(project_syn_orgs))
    ctx.obj = Context(cfg, r)


@component_hub.group(short_help="Generate individual part of documentation")
def generate():
    pass


@generate.command(short_help="Initialize Antora site")
@click.pass_context
def antora_site(ctx):
    create(ctx.obj.config.root_path, ctx.obj.config.project_slug)


@generate.command(short_help="Generate documentation index")
@click.pass_context
def index(ctx):
    ctx.obj.renderer.render_adoc_template(Template.INDEX)


@generate.command(short_help="Generate documentation navigation")
@click.pass_context
def nav(ctx):
    ctx.obj.renderer.render_adoc_template(Template.NAV)


@generate.command(short_help="Generate documentation Antora playbook")
@click.pass_context
def playbook(ctx):
    ctx.obj.renderer.render_antora_playbook()


@component_hub.command(short_help="Generate full documentation")
@click.pass_context
def make(ctx):
    output_dir: Path = ctx.obj.config.output_dir
    create_site = (
        len(list(output_dir.iterdir())) == 0 if output_dir.is_dir() else not output_dir.is_dir()
    )
    if create_site:
        if output_dir.exists() and not output_dir.is_dir():
            click.confirm(
                f"Remove {output_dir} to create Antora site?",
                abort=True,
            )
            os.unlink(output_dir)
        click.echo("Setting up Antora site")
        ctx.invoke(antora_site)

    click.echo("Rendering nav.adoc")
    ctx.invoke(nav)
    click.echo("Rendering index.adoc")
    ctx.invoke(index)
    click.echo("Rendering playbook.yml")
    ctx.invoke(playbook)


def main():
    load_dotenv()
    component_hub.main(prog_name="component-hub", auto_envvar_prefix="COMPONENT_HUB")
