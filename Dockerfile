FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-jdk \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .[streaming,batch,producer,api]

COPY . .

ENV PYTHONPATH=/app
ENV CONFIG_PATH=config/docker.yaml

CMD ["python", "-m", "streaming.streaming_job"]
