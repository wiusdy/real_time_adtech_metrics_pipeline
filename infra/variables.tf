variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name prefix for resources"
  type        = string
  default     = "adtech-pipeline"
}

variable "glue_scripts_bucket" {
  description = "S3 bucket for Glue job scripts"
  type        = string
}

variable "silver_bucket" {
  description = "S3 bucket for silver layer"
  type        = string
}

variable "gold_bucket" {
  description = "S3 bucket for gold layer"
  type        = string
}

variable "kafka_bootstrap_servers" {
  description = "Kafka bootstrap servers (MSK endpoint)"
  type        = string
}

variable "kafka_topic" {
  description = "Kafka topic name"
  type        = string
  default     = "ad-events"
}

variable "streaming_window" {
  description = "Streaming aggregation window"
  type        = string
  default     = "5 minutes"
}

variable "streaming_watermark" {
  description = "Streaming watermark delay"
  type        = string
  default     = "10 minutes"
}

variable "glue_worker_type" {
  description = "Glue worker type"
  type        = string
  default     = "G.1X"
}

variable "glue_num_workers" {
  description = "Number of Glue workers"
  type        = number
  default     = 2
}
