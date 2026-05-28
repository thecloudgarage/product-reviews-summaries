FROM python:3.11-slim
WORKDIR /app
COPY services/review_batch_aggregator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/common /app/common
COPY services/review_batch_aggregator/main.py /app/main.py
CMD ["python", "main.py"]
