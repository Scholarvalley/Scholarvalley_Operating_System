output "aws_region" {
  value = var.aws_region
}

output "s3_bucket_name" {
  description = "S3 bucket for app uploads and assets"
  value       = aws_s3_bucket.app.id
}

output "ecr_repository_url" {
  description = "ECR repository URL for the app image"
  value       = local.ecr_repository_url
}

output "ecr_repository_uri" {
  value = aws_ecr_repository.app.repository_url
}

output "alb_dns_name" {
  description = "ALB DNS name – use this URL to reach the API (HTTP)"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  value = aws_lb.main.zone_id
}

output "api_url" {
  description = "Base URL for the API (HTTP until you add HTTPS)"
  value       = "http://${aws_lb.main.dns_name}"
}

output "rds_endpoint" {
  description = "RDS instance endpoint (for DATABASE_URL)"
  value       = var.create_rds ? aws_db_instance.main[0].endpoint : null
}

output "rds_database_name" {
  value = var.create_rds ? aws_db_instance.main[0].db_name : null
}

output "database_url_placeholder" {
  description = "Use this format in Secrets Manager; replace PASSWORD with actual password"
  value       = var.create_rds ? "postgresql+psycopg2://${var.db_username}:PASSWORD@${aws_db_instance.main[0].endpoint}/${var.db_name}" : null
  sensitive   = true
}
