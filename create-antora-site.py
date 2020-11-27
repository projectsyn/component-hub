from logging import root
import os
import shutil
from cookiecutter.main import cookiecutter

root_path = 'commodore-components-hub'
ebook_path = '%s/docs/%s.adoc' % (root_path, root_path)
ebook_folder_path = '%s/docs/ebook' % root_path
images_path = '%s/docs/modules/ROOT/assets/images' % root_path
pages_path = '%s/docs/modules/ROOT/pages' % root_path

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
shutil.rmtree(ebook_folder_path)
shutil.rmtree(images_path)
shutil.rmtree(pages_path)
os.makedirs(images_path)
os.makedirs(pages_path)
shutil.copyfile('assets/syn.png', '%s/syn.png' % images_path)