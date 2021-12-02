FROM python:3.10-alpine3.15

RUN adduser -D mrdemo

WORKDIR /home/mrdemo

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY dbs/* dbs/
COPY *.py ./
COPY static static
COPY templates templates
COPY boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP demos.py

RUN chown -R mrdemo:mrdemo ./
USER mrdemo

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
