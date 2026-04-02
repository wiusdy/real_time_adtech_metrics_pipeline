FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir .[streaming,batch,dashboard]

COPY . .

CMD ["bash"]
