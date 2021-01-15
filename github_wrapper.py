import os
import yaml
from github import Github, GithubException
from yaml.loader import Loader

# Loads the list of repository clone URLs to ignore when calling get_commodore_component_repos()
def load_ignore_list():
    f = open('reposignore.txt', 'r')
    lines = [line for line in f.readlines()]
    f.close()
    return [item.replace('\n', '') for item in lines if not item.startswith('#')]

# Makes sure that the repository has an Antora definition file, and fetches some info from it
def get_antora_yml(repo):
    try:
        contents = repo.get_contents('docs/antora.yml').decoded_content
        y = yaml.load(contents, Loader=Loader)
        return y
    except GithubException:
        return None

# Returns True if the current repo has a corresponding Antora definition file, False otherwise
def has_antora_yml(repo):
    try:
        repo.get_contents('docs/antora.yml')
        return True
    except GithubException:
        return False

# Figures out the main branch of the repository (usually "master" or "main")
def get_main_branch(repo):
    branches = [b.name for b in repo.get_branches().get_page(0)]
    main_branch = 'main'
    if 'master' in branches:
        main_branch = 'master'
    return main_branch

# Fetch a list of all repositories in GitHub with the "commodore-component" topic
def get_commodore_component_repos():
    # Connect to GitHub (read the token from environment)
    token = os.environ['GITHUB_TOKEN']
    g = Github(token)

    # Fetch all repositories in GitHub with the "commodore-component" topic
    repositories = g.search_repositories(query='topic:commodore-component')

    # Filter out archived repositories
    not_archived_repos = [r for r in repositories if not r.archived]
    ignore_list = load_ignore_list()

    # Filter out repositories to be ignored
    return [r for r in not_archived_repos if r.clone_url not in ignore_list]
