FROM python:3.11-slim

WORKDIR /app

COPY docker_requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r docker_requirements.txt

COPY . .
EXPOSE 8000

CMD [ "uvicorn", "src.serving.app:app", "--host", "0.0.0.0", "--port", "8000"]