variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "image_tag" {
  description = "Docker image tag for deployment"
  type        = string
  default     = "latest"
}

variable "ecr_repository" {
  description = "ECR repository URL"
  type        = string
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "app_domain" {
  description = "Application domain name"
  type        = string
}

# Environment-specific variables
locals {
  common_tags = {
    Project     = "auth-system"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  # API endpoints used by frontend apps
  api_endpoints = {
    auth    = "https://api.${var.app_domain}/auth"
    users   = "https://api.${var.app_domain}/users"
  }
}
