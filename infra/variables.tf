# Scholarvalley AWS infrastructure – variables

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project" {
  description = "Project name used in resource names"
  type        = string
  default     = "scholarvalley"
}

variable "vpc_id" {
  description = "VPC ID (leave empty to use default VPC)"
  type        = string
  default     = ""
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for ECS and RDS (empty = use default subnets)"
  type        = list(string)
  default     = []
}

variable "create_rds" {
  description = "Set to true to create RDS PostgreSQL instance"
  type        = bool
  default     = true
}

variable "db_username" {
  description = "Master username for RDS"
  type        = string
  default     = "scholarvalley"
  sensitive   = true
}

variable "db_password" {
  description = "Master password for RDS (set via TF_VAR_db_password or -var)"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Name of the default database"
  type        = string
  default     = "scholarvalley"
}

variable "ecs_cpu" {
  description = "CPU units for ECS Fargate task (256 = 0.25 vCPU, 512 = 0.5 vCPU). Use 256 to minimize cost."
  type        = number
  default     = 256
}

variable "ecs_memory_mb" {
  description = "Memory in MB for ECS Fargate task. Min 512 for 256 CPU; use 512 to minimize cost."
  type        = number
  default     = 512
}

variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 1
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for HTTPS (optional; leave empty for HTTP only)"
  type        = string
  default     = ""
}

variable "domain_name" {
  description = "Optional domain name for ALB (e.g. api.scholarvalley.com)"
  type        = string
  default     = ""
}
