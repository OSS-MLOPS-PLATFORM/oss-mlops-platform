FROM python:3.8.1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt --quiet --no-cache-dir

COPY train.py .

CMD ["python", "train.py"]
