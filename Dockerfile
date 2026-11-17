FROM python:3.11-slim

WORKDIR /app
COPY main.py inventory.py storage.py ./
COPY data/ ./data/
VOLUME ["/app/data"]

CMD ["python", "main.py"]
