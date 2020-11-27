import os
import yaml
from github import Github, GithubException

# Figures out the main branch of the repository (usually "master" or "main")
def get_main_branch(repo):
    branches = [b.name for b in repo.get_branches().get_page(0)]
    main_branch = 'main'
    if 'master' in branches:
        main_branch = 'master'
    return main_branch

# Makes sure that the repository has an Antora definition file, and fetches some info from it
def has_antora_yml(repo):
    try:
        repo.get_contents('docs/antora.yml')
        return True
    except GithubException:
        return False

# Connect to GitHub (read the token from environment)
token = os.environ['GITHUB_TOKEN']
g = Github(token)

# Load the Antora playbook.yml file
stream = open('templates/playbook.yml', 'r')
playbook = yaml.load(stream, Loader=yaml.Loader)

# Fetch all repositories in GitHub with the "commodore-component" topic
repositories = g.search_repositories(query='topic:commodore-component')
not_archived_repos = [r for r in repositories if not r.archived]
for repo in not_archived_repos:
    # Find out the 'docs/antora.yml' file and get its contents
    if has_antora_yml(repo):
        # Decide which is the master branch
        main_branch = get_main_branch(repo)
        source = {
            'branches': main_branch,
            'start_path': 'docs',
            'url': repo.clone_url
        }
        playbook['content']['sources'].append(source)

print(yaml.dump(playbook))
