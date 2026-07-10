# syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm

ENV REDIS_ENDPOINT=127.0.0.1
ENV REDIS_PORT=6379
ENV REDIS_DB=0

ENV SCHEDULER_TIMES=50|165|230

WORKDIR /scheduler

COPY setup_beat.py .

COPY run_beat.py .

COPY requirements.txt .

RUN pip3 install -r requirements.txt

CMD ["python", "run_beat.py"]