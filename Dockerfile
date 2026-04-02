# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# dependências do sistema
RUN apt-get update && apt-get install -y \
    default-jdk \
    curl \
    && rm -rf /var/lib/apt/lists/*

# instalar pyspark + kafka
COPY pyproject.toml .
RUN pip install --no-cache-dir pyspark kafka-python pyyaml

# copiar código
COPY . .

ENV PYTHONPATH=/app

CMD ["bash"]
