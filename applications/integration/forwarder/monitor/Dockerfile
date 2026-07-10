# syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm

ENV REDIS_ENDPOINT=127.0.0.1
ENV REDIS_PORT=6379
ENV REDIS_DB=0

ENV FLOWER_USERNAME=flower123
ENV FLOWER_PASSWORD=flower456

WORKDIR /monitor

COPY setup_flower.py .

COPY run_flower.py .

COPY requirements.txt .

RUN pip3 install -r requirements.txt

EXPOSE 6501

CMD ["python", "run_flower.py"]