# ===============================
# VARIABLES
# ===============================

PYTHON = python3.11
CONFIG = config/dev.yaml

# ===============================
# SETUP
# ===============================

install:
	$(PYTHON) -m pip install --upgrade pip
	pip install -e .[streaming,batch,dashboard,dev]
	pre-commit install

# ===============================
# LINT & FORMAT
# ===============================

format:
	black .
	isort .
	ruff check . --fix

lint:
	black --check .
	isort --check-only .
	ruff check .

# ===============================
# TESTS
# ===============================

test:
	PYTHONPATH=. pytest

# ===============================
# LOCAL RUN
# ===============================

producer:
	PYTHONPATH=. $(PYTHON) -m producer.producer

run-streaming:
	PYTHONPATH=. $(PYTHON) -m streaming.streaming_job

run-batch:
	PYTHONPATH=. $(PYTHON) -m batch.batch_job

run-pipeline:
	PYTHONPATH=. $(PYTHON) run_pipeline.py --mode streaming &
	sleep 5
	PYTHONPATH=. $(PYTHON) run_pipeline.py --mode batch

dashboard:
	PYTHONPATH=. streamlit run dashboard/app.py

# ===============================
# DOCKER
# ===============================

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

restart:
	docker compose down && docker compose up -d --build

# ===============================
# AWS GLUE
# ===============================

glue-upload:
	aws s3 cp glue/streaming_job.py s3://$(GLUE_SCRIPTS_BUCKET)/glue/scripts/streaming_job.py
	aws s3 cp glue/batch_job.py s3://$(GLUE_SCRIPTS_BUCKET)/glue/scripts/batch_job.py

glue-start-streaming:
	aws glue start-job-run --job-name adtech-pipeline-streaming-$(ENV)

glue-start-batch:
	aws glue start-job-run --job-name adtech-pipeline-batch-$(ENV)

glue-status:
	@echo "=== Streaming Job ==="
	aws glue get-job-runs --job-name adtech-pipeline-streaming-$(ENV) --max-items 3
	@echo "=== Batch Job ==="
	aws glue get-job-runs --job-name adtech-pipeline-batch-$(ENV) --max-items 3

# ===============================
# TERRAFORM (INFRA)
# ===============================

infra-init:
	cd infra && terraform init

infra-plan:
	cd infra && terraform plan -var-file=terraform.tfvars

infra-apply:
	cd infra && terraform apply -var-file=terraform.tfvars

infra-destroy:
	cd infra && terraform destroy -var-file=terraform.tfvars

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
