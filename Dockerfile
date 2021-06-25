FROM python:3.9.5-alpine3.12

RUN apk add --no-cache git
RUN adduser creator --disabled-password --home /home/creator

USER creator
RUN git config --global user.email "info@vshn.ch" && git config --global user.name "VSHN Creator user"

WORKDIR /home/creator/tool
ENV PATH $PATH:/home/creator/.local/bin
COPY requirements.txt /home/creator/tool
RUN pip install --no-cache-dir --requirement requirements.txt

COPY assets /home/creator/tool/assets/
COPY templates /home/creator/tool/templates/
COPY ["entrypoint.sh", "reposignore.txt", "create-antora-site.py", "github_wrapper.py", "generate-index.py", "generate-nav.py", "generate-playbook.py", "/home/creator/tool/"]

ENV OUT_DIR /home/creator/build
ENV PROJECT_SLUG commodore-components-hub
ENTRYPOINT [ "/home/creator/tool/entrypoint.sh" ]
