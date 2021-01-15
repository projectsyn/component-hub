from logging import root
import os
import shutil
import argparse
from cookiecutter.main import cookiecutter

parser = argparse.ArgumentParser(description='Create a Commodore Components Hub website with Antora.')
parser.add_argument('-p', '--path', help='path where the Antora site is created', default='build')
parser.add_argument('-s', '--slug', help='path where the Antora site is created', default='commodore-components-hub')
args = parser.parse_args()
root_path = args.path
project_slug = args.slug

deployment_path = f'{root_path}/{project_slug}/deployment'
ebook_path = f'{root_path}/{project_slug}/docs/{project_slug}.adoc'
ebook_folder_path = f'{root_path}/{project_slug}/docs/ebook'
images_path = f'{root_path}/{project_slug}/docs/modules/ROOT/assets/images'
pages_path = f'{root_path}/{project_slug}/docs/modules/ROOT/pages'
gitlab_ci_path = f'{root_path}/{project_slug}/.gitlab-ci.yml'

# Uses Cookiecutter to generate a new Antora documentation site
params = {
    'project_title': 'Commodore Components Hub',
    'project_slug': project_slug,
    'project_url': 'https://hub.syn.tools',
    'antora_prefix': 'hub',
    'antora_theme': 'syn'
}

cookiecutter('https://github.com/vshn/antora-bootstrap.git',
             no_input=True,
             extra_context=params,
             overwrite_if_exists=True,
             output_dir=root_path)

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
