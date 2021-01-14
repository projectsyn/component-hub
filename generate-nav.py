import yaml
from github_wrapper import get_repos
from github import GithubException
from yaml.loader import Loader

# Makes sure that the repository has an Antora definition file, and fetches some info from it
def get_antora_yml(repo):
    try:
        contents = repo.get_contents('docs/antora.yml').decoded_content
        y = yaml.load(contents, Loader=Loader)
        return y
    except GithubException:
        return None

# Fetch all repositories in GitHub with the "commodore-component" topic
components = []
repositories = get_repos()
for repo in repositories:
    # Find out the 'docs/antora.yml' file and get its contents
    antora = get_antora_yml(repo)
    if not antora is None:
        components.append({
            'name': antora['name'],
            'title': antora['title']
        })

# Output template
template = open('templates/nav.adoc', 'r')
print(template.read())

# Output list of components sorted by name
components_sorted = sorted(components, key=lambda c: c['title'].upper())
for component in components_sorted:
    print('* xref:%s:ROOT:index.adoc[%s]' % (component['name'], component['title']))
