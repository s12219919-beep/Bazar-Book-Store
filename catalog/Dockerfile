FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY database.py .

RUN mkdir -p /data

ENV CATALOG_DB=/data/catalog.db

EXPOSE 5001

CMD ["python", "app.py"]







