import os
import shutil
from cookiecutter.main import cookiecutter

root_path = 'commodore-components-hub'
deployment_path = f'{root_path}/deployment'
ebook_path = f'{root_path}/docs/{root_path}.adoc'
ebook_folder_path = f'{root_path}/docs/ebook'
images_path = f'{root_path}/docs/modules/ROOT/assets/images'
pages_path = f'{root_path}/docs/modules/ROOT/pages'
gitlab_ci_path = f'{root_path}/.gitlab-ci.yml'

# Uses Cookiecutter to generate a new Antora documentation site
params = {
    'project_title': 'Commodore Components Hub',
    'project_slug': 'commodore-components-hub',
    'project_url': 'https://hub.syn.tools',
    'antora_prefix': 'hub',
    'antora_theme': 'syn'
}

cookiecutter('git@git.vshn.net:vshn/antora-bootstrap',
             no_input=True,
             extra_context=params)

# Remove extra files
os.remove(ebook_path)
os.remove(gitlab_ci_path)
shutil.rmtree(deployment_path)
shutil.rmtree(ebook_folder_path)
shutil.rmtree(images_path)
shutil.rmtree(pages_path)
os.makedirs(images_path)
os.makedirs(pages_path)

# Copy extra files
shutil.copyfile('assets/syn.png', f'{images_path}/syn.png')
