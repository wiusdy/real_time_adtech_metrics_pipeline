# ===========================
# IAM Role for Glue Jobs
# ===========================

resource "aws_iam_role" "glue_role" {
  name = "${var.project_name}-glue-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy" "glue_s3_access" {
  name = "${var.project_name}-glue-s3-policy"
  role = aws_iam_role.glue_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
        ]
        Resource = [
          "arn:aws:s3:::${var.silver_bucket}",
          "arn:aws:s3:::${var.silver_bucket}/*",
          "arn:aws:s3:::${var.gold_bucket}",
          "arn:aws:s3:::${var.gold_bucket}/*",
          "arn:aws:s3:::${var.glue_scripts_bucket}",
          "arn:aws:s3:::${var.glue_scripts_bucket}/*",
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kafka:DescribeCluster",
          "kafka:GetBootstrapBrokers",
          "kafka-cluster:Connect",
          "kafka-cluster:DescribeTopic",
          "kafka-cluster:ReadData",
        ]
        Resource = ["*"]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Resource = ["arn:aws:logs:*:*:/aws-glue/*"]
      }
    ]
  })
}

# ===========================
# Glue Data Catalog
# ===========================

resource "aws_glue_catalog_database" "adtech" {
  name = "${var.project_name}-${var.environment}"
}

resource "aws_glue_catalog_table" "gold_metrics" {
  database_name = aws_glue_catalog_database.adtech.name
  name          = "metrics_gold"

  table_type = "EXTERNAL_TABLE"

  parameters = {
    classification = "parquet"
  }

  storage_descriptor {
    location      = "s3://${var.gold_bucket}/aggregated/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "user_id"
      type = "int"
    }

    columns {
      name = "total_revenue"
      type = "double"
    }

    columns {
      name = "total_events"
      type = "bigint"
    }
  }
}

# ===========================
# Upload Glue Scripts to S3
# ===========================

resource "aws_s3_object" "streaming_script" {
  bucket = var.glue_scripts_bucket
  key    = "glue/scripts/streaming_job.py"
  source = "${path.module}/../glue/streaming_job.py"
  etag   = filemd5("${path.module}/../glue/streaming_job.py")
}

resource "aws_s3_object" "batch_script" {
  bucket = var.glue_scripts_bucket
  key    = "glue/scripts/batch_job.py"
  source = "${path.module}/../glue/batch_job.py"
  etag   = filemd5("${path.module}/../glue/batch_job.py")
}

# ===========================
# Glue Streaming Job
# ===========================

resource "aws_glue_job" "streaming" {
  name     = "${var.project_name}-streaming-${var.environment}"
  role_arn = aws_iam_role.glue_role.arn

  glue_version      = "4.0"
  worker_type       = var.glue_worker_type
  number_of_workers = var.glue_num_workers

  command {
    name            = "gluestreaming"
    script_location = "s3://${var.glue_scripts_bucket}/glue/scripts/streaming_job.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"             = "python"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-metrics"           = "true"
    "--KAFKA_BOOTSTRAP_SERVERS"  = var.kafka_bootstrap_servers
    "--KAFKA_TOPIC"              = var.kafka_topic
    "--OUTPUT_PATH"              = "s3://${var.silver_bucket}/events/"
    "--CHECKPOINT_PATH"          = "s3://${var.silver_bucket}/checkpoints/"
    "--WINDOW_DURATION"          = var.streaming_window
    "--WATERMARK"                = var.streaming_watermark
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# ===========================
# Glue Batch Job
# ===========================

resource "aws_glue_job" "batch" {
  name     = "${var.project_name}-batch-${var.environment}"
  role_arn = aws_iam_role.glue_role.arn

  glue_version      = "4.0"
  worker_type       = var.glue_worker_type
  number_of_workers = var.glue_num_workers

  command {
    name            = "glueetl"
    script_location = "s3://${var.glue_scripts_bucket}/glue/scripts/batch_job.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"             = "python"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-metrics"           = "true"
    "--SILVER_PATH"              = "s3://${var.silver_bucket}/events/"
    "--GOLD_PATH"                = "s3://${var.gold_bucket}/aggregated/"
    "--GLUE_DATABASE"            = aws_glue_catalog_database.adtech.name
    "--GLUE_TABLE"               = "metrics_gold"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# ===========================
# Glue Trigger (Batch on Schedule)
# ===========================

resource "aws_glue_trigger" "batch_schedule" {
  name     = "${var.project_name}-batch-trigger-${var.environment}"
  type     = "SCHEDULED"
  schedule = "cron(0 */1 * * ? *)" # Every hour

  actions {
    job_name = aws_glue_job.batch.name
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}
