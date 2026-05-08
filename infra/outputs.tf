output "glue_streaming_job_name" {
  description = "Name of the Glue streaming job"
  value       = aws_glue_job.streaming.name
}

output "glue_batch_job_name" {
  description = "Name of the Glue batch job"
  value       = aws_glue_job.batch.name
}

output "glue_database_name" {
  description = "Glue Data Catalog database name"
  value       = aws_glue_catalog_database.adtech.name
}

output "glue_role_arn" {
  description = "IAM Role ARN used by Glue jobs"
  value       = aws_iam_role.glue_role.arn
}
