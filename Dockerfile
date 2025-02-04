FROM docker.io/library/python:3.12.8-slim

LABEL org.opencontainers.image.title="drkeyongenesis/ansible-github-actions-cicd"
LABEL org.opencontainers.image.source="https://github.com/drkeyongenesis/ansible-github-actions-cicd"
LABEL org.opencontainers.image.documentation="https://ansible.readthedocs.io/projects/ansible-build-data"
LABEL org.opencontainers.image.base.name="docker.io/library/python:3.12.8-slim"

ENV ANSIBLE_CONFIG /etc/ansible/ansible.cfg
COPY ansible.cfg ${ANSIBLE_CONFIG}
COPY requirements.txt /requirements.txt
COPY app.sh /app.sh
COPY install.sh /install.sh

RUN chmod +x /app.sh
RUN chmod +x /install.sh
RUN /install.sh

RUN pip install --upgrade --no-cache-dir pip
RUN pip install --upgrade --no-cache-dir -r /requirements.txt

CMD ["/app.sh"]
