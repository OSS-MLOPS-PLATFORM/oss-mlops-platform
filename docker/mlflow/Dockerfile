FROM python:3.8.3

ARG MLFLOW_VERSION=2.4.0
ARG PSYCOPG2_VERSION=2.9.2
ARG PYMYSQL_VERSION=1.0.2
ARG MYSQLCLIENT_VERSION=2.1.0

RUN apt-get update
RUN apt-get -y install default-libmysqlclient-dev

RUN pip install --upgrade pip setuptools wheel && pip install mlflow==${MLFLOW_VERSION} psycopg2==${PSYCOPG2_VERSION} protobuf==3.20.0 boto3==1.15.16

# RUN pip install PyMySQL==${PYMYSQL_VERSION}
RUN pip install mysqlclient==${MYSQLCLIENT_VERSION}

# To use GCS as artifact storage
RUN pip install google-cloud-storage

WORKDIR /mlflow

ENV BACKEND_STORE_URI=sqlite:////mlflow/mlflow.db
ENV DEFAULT_ARTIFACT_ROOT=/mlflow/mlruns/

EXPOSE 5000

RUN echo '#!/bin/bash \n\n\
    echo "Starting MLFlow server with DEFAULT_ARTIFACT_ROOT=${DEFAULT_ARTIFACT_ROOT}" \n\n\
    mlflow server --host 0.0.0.0 --port=5000 --backend-store-uri=${BACKEND_STORE_URI} --default-artifact-root=${DEFAULT_ARTIFACT_ROOT}' \
    > /usr/bin/start_mlflow.sh \
    && chmod +x /usr/bin/start_mlflow.sh

CMD [ "/usr/bin/start_mlflow.sh"]
