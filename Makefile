# ===============================
# VARIABLES
# ===============================

PYTHON=python
CONFIG=config/dev.yaml
DOCKER_IMAGE=ml-pipeline
DOCKER_TAG=latest

# ===============================
# SETUP
# ===============================

install:
	pip install --upgrade pip
	pip install .[streaming,batch,dashboard,dev]
	pre-commit install

setup:
	bash scripts/setup.sh

# ===============================
# LINT & FORMAT
# ===============================

format:
	black .
	isort .

lint:
	black --check .
	isort --check-only .
	flake8 .

# ===============================
# TESTS
# ===============================

test:
	pytest

# ===============================
# LOCAL RUN
# ===============================

run-producer:
	$(PYTHON) producer/producer.py

run-streaming:
	$(PYTHON) streaming/streaming_job.py --config $(CONFIG)

run-batch:
	$(PYTHON) batch/batch_job.py --config $(CONFIG)

run-dashboard:
	streamlit run dashboard/app.py -- --config $(CONFIG)

run-pipeline:
	$(MAKE) run-streaming & \
	sleep 5 && \
	$(MAKE) run-batch

# ===============================
# DOCKER
# ===============================

docker-build:
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run:
	docker run -it $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# ===============================
# DOCKER HUB
# ===============================

docker-login:
	docker login

docker-push:
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $$DOCKER_USERNAME/$(DOCKER_IMAGE):$(DOCKER_TAG)
	docker push $$DOCKER_USERNAME/$(DOCKER_IMAGE):$(DOCKER_TAG)

# ===============================
# AIRFLOW
# ===============================

airflow-up:
	docker-compose up airflow

airflow-down:
	docker-compose stop airflow

# ===============================
# CLEAN
# ===============================

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# ===============================
# FULL PIPELINE (CI LIKE)
# ===============================

ci:
	$(MAKE) lint
	$(MAKE) test

cd:
	$(MAKE) docker-build
	$(MAKE) docker-push

all:
	$(MAKE) ci
	$(MAKE) cd
