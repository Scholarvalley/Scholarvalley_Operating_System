# Scholarvalley – AWS infrastructure (ECS Fargate, RDS, S3, ECR, ALB)
# Run: terraform init && terraform plan -var="db_password=YOUR_SECURE_PASSWORD" && terraform apply

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  name = "${var.project}-${var.environment}"
  # Use default VPC and subnets if not provided
  vpc_id             = var.vpc_id != "" ? var.vpc_id : data.aws_vpc.default.id
  subnet_ids         = length(var.private_subnet_ids) > 0 ? var.private_subnet_ids : data.aws_subnets.default.ids
  account_id         = data.aws_caller_identity.current.account_id
  ecr_repository_url = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/${aws_ecr_repository.app.name}"
}

# Default VPC and subnets (simplest for dev)
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# S3 – document uploads and static assets
resource "aws_s3_bucket" "app" {
  bucket = "${local.name}-app-${local.account_id}"

  tags = {
    Name        = local.name
    Environment = var.environment
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "app" {
  bucket = aws_s3_bucket.app.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "app" {
  bucket = aws_s3_bucket.app.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ECR – container registry
resource "aws_ecr_repository" "app" {
  name                 = var.project
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = { Name = local.name, Environment = var.environment }
}

# IAM – ECS task execution role (pull image, logs)
resource "aws_iam_role" "ecs_execution" {
  name = "${local.name}-ecs-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IAM – ECS task role (app: S3, SES, etc.)
resource "aws_iam_role" "ecs_task" {
  name = "${local.name}-ecs-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "ecs_task" {
  name   = "${local.name}-ecs-task"
  role   = aws_iam_role.ecs_task.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket", "s3:DeleteObject"]
        Resource = [aws_s3_bucket.app.arn, "${aws_s3_bucket.app.arn}/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["ses:SendEmail", "ses:SendRawEmail"]
        Resource = "*"
      }
    ]
  })
}

# Security groups
resource "aws_security_group" "alb" {
  name        = "${local.name}-alb"
  description = "ALB for Scholarvalley"
  vpc_id      = local.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "${local.name}-alb" }
}

resource "aws_security_group" "ecs" {
  name        = "${local.name}-ecs"
  description = "ECS tasks for Scholarvalley"
  vpc_id      = local.vpc_id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "${local.name}-ecs" }
}

# RDS (optional)
resource "aws_security_group" "rds" {
  count       = var.create_rds ? 1 : 0
  name        = "${local.name}-rds"
  description = "RDS PostgreSQL for Scholarvalley"
  vpc_id      = local.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "${local.name}-rds" }
}

resource "aws_db_subnet_group" "main" {
  count       = var.create_rds ? 1 : 0
  name        = "${local.name}-db"
  subnet_ids  = local.subnet_ids
  description = "Subnets for RDS"
  tags        = { Name = "${local.name}-db" }
}

resource "aws_db_instance" "main" {
  count = var.create_rds ? 1 : 0

  identifier     = "${local.name}-db"
  engine         = "postgres"
  engine_version = "15"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  storage_encrypted = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.main[0].name
  vpc_security_group_ids = [aws_security_group.rds[0].id]
  publicly_accessible    = false
  skip_final_snapshot    = var.environment != "prod"
  multi_az               = false

  tags = { Name = "${local.name}-db", Environment = var.environment }
}

# ALB
resource "aws_lb" "main" {
  name               = local.name
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = local.subnet_ids
  tags               = { Name = local.name }
}

resource "aws_lb_target_group" "app" {
  name        = "${local.name}-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = local.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
  }
  tags = { Name = local.name }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# ECS cluster and service
resource "aws_ecs_cluster" "main" {
  name = local.name
  tags = { Name = local.name }
}

resource "aws_ecs_task_definition" "app" {
  family                   = local.name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory_mb

  execution_role_arn = aws_iam_role.ecs_execution.arn
  task_role_arn      = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "app"
    image = "${local.ecr_repository_url}:latest"
    portMappings = [{ containerPort = 8000, protocol = "tcp" }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/${local.name}"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
    environment = [
      { name = "AWS_REGION", value = var.aws_region },
      { name = "AWS_S3_BUCKET", value = aws_s3_bucket.app.id }
    ]
    # Secrets: inject DATABASE_URL, JWT_SECRET_KEY etc. from Secrets Manager in your pipeline
    secrets = []
  }])
}

resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${local.name}"
  retention_in_days  = var.environment == "prod" ? 30 : 7
  tags              = { Name = local.name }
}

resource "aws_ecs_service" "app" {
  name            = local.name
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = local.subnet_ids
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "app"
    container_port   = 8000
  }

  tags = { Name = local.name }
}
