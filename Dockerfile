FROM python:3.10-alpine3.15

RUN adduser -D duser

WORKDIR /home/duser

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY dbs/* dbs/
COPY *.py ./
COPY .env ./
COPY modules/* modules/
COPY static static
COPY templates templates
COPY boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP demos.py

RUN chown -R duser:duser ./
USER duser

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
