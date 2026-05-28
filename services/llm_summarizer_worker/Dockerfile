FROM python:3.11-slim
WORKDIR /app
COPY services/llm_summarizer_worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/common /app/common
COPY services/llm_summarizer_worker/main.py /app/main.py
CMD ["python", "main.py"]
