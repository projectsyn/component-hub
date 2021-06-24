import click

from dotenv import load_dotenv
from importlib_metadata import version

from component_hub import __git_version__
from .config import Config, Template
from .antora_site import create
from .render_template import Renderer


def _version():
    pyversion = version("component_hub")
    if f"v{pyversion}" != __git_version__:
        return f"{pyversion} (Git version: {__git_version__})"


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
@click.option("--root", help="Root directory for generated files")
@click.option("--slug", help="directory name for the generated Antora project")
@click.option(
    "--ignore-list",
    help="File listing clone URLs of repositories to ignore",
    default=None,
)
def component_hub(ctx, github_token, root, slug, ignore_list):
    cfg = Config(
        github_token=github_token,
        root_path=root,
        project_slug=slug,
        ignorelist=ignore_list,
    )
    r = Renderer(cfg)
    ctx.obj = Context(cfg, r)


@component_hub.group(short_help="Generate individual part of documentation")
@click.pass_context
def generate(ctx):
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
    ctx.obj.renderer.render_yaml_template("playbook.yml")


@component_hub.command(short_help="Generate full documentation")
@click.pass_context
def make(ctx):
    ctx.invoke(antora_site)
    ctx.invoke(nav)
    ctx.invoke(index)
    ctx.invoke(playbook)


def main():
    load_dotenv()
    component_hub.main(prog_name="component-hub", auto_envvar_prefix="COMPONENT_HUB")
