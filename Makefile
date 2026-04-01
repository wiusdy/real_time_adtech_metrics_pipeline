# ===============================
# VARIABLES
# ===============================

PYTHON=python3.11
CONFIG=config/dev.yaml
DOCKER_IMAGE=ml-pipeline
DOCKER_TAG=latest

# ===============================
# SETUP
# ===============================

install:
	$(PYTHON) -m pip install --upgrade pip
	pip install .[streaming,batch,dashboard,dev]
	pre-commit install

# ===============================
# LINT & FORMAT
# ===============================

format:
	black .
	isort .
	ruff check . --fix
	pre-commit run --all-files

lint:
	black --check .
	isort --check-only .
	ruff check .

# ===============================
# TESTS
# ===============================

test:
	pytest || true

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
# CLEAN
# ===============================

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# ===============================
# CI (LOCAL)
# ===============================

ci:
	$(MAKE) lint
	$(MAKE) test

all:
	$(MAKE) ci