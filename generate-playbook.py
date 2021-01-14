import yaml
from github_wrapper import get_commodore_component_repos, has_antora_yml, get_main_branch

# Load the Antora playbook.yml file
stream = open('templates/playbook.yml', 'r')
playbook = yaml.load(stream, Loader=yaml.Loader)

# Fetch list of repositories from GitHub
repositories = get_commodore_component_repos()
for repo in repositories:
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
