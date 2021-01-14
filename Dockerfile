FROM python:3.8.7-alpine3.12

RUN apk add --no-cache git
RUN adduser creator --disabled-password --home /creator

USER creator
RUN git config --global user.email "creator@vshn.ch" && git config --global user.name "Creator user"

WORKDIR /creator
COPY requirements.txt /creator
RUN pip install -r requirements.txt

COPY assets /creator/assets/
COPY templates /creator/templates/
COPY create-antora-site.py /creator
COPY ["entrypoint.sh", "reposignore", "github_wrapper.py", "generate-index.py", "generate-nav.py", "generate-playbook.py", "/creator/"]

ENTRYPOINT [ "/creator/entrypoint.sh" ]
