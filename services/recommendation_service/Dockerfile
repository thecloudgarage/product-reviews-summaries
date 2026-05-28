FROM python:3.11-slim
WORKDIR /app
COPY services/recommendation_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/common /app/common
COPY services/recommendation_service/main.py /app/main.py
CMD ["python", "main.py"]
