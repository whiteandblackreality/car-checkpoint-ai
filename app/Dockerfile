FROM docker.io/library/python:3.10.1

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && apt-get install -y gcc postgresql libpq-dev netcat

RUN pip install --upgrade pip
COPY app/requirements/requirements.txt .
RUN pip install -r requirements.txt

COPY . .
