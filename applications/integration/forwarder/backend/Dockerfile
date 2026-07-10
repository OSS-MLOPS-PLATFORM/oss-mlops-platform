# syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm

ENV REDIS_ENDPOINT=127.0.0.1
ENV REDIS_PORT=6379
ENV REDIS_DB=0

ENV CELERY_CONCURRENCY=8
ENV CELERY_LOGLEVEL=warning

ENV FLOWER_ENDPOINT=127.0.0.1
ENV FLOWER_PORT=6501
ENV FLOWER_USERNAME=flower123
ENV FLOWER_PASSWORD=flower456

ENV PROMETHEUS_PORT=6502 

WORKDIR /backend

COPY setup_celery.py .

COPY run_celery.py .

COPY forwards /backend/forwards

COPY functions /backend/functions

COPY scheduler /backend/scheduler

COPY tasks /backend/tasks

COPY requirements.txt .

RUN pip3 install -r requirements.txt

RUN apt-get update

RUN apt-get install -y curl

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.24.0/bin/linux/amd64/kubectl

RUN chmod +x ./kubectl

RUN mv ./kubectl /usr/local/bin

EXPOSE 6502

CMD ["python", "run_celery.py"]