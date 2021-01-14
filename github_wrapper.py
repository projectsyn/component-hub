import os
from github import Github

def load_ignore_list():
    f = open('reposignore', 'r+')
    lines = [line for line in f.readlines()]
    f.close()
    return [item.replace('\n', '') for item in lines if not item.startswith('#')]


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
