# Auth Service Infrastructure
# Provisions backend API service with database and secrets

resource "aws_ecs_service" "auth_service" {
  name            = "auth-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.auth_service.arn
  desired_count   = 2

  load_balancer {
    target_group_arn = aws_lb_target_group.auth_service.arn
    container_name   = "auth-api"
    container_port   = 3000
  }

  network_configuration {
    subnets         = aws_subnet.private[*].id
    security_groups = [aws_security_group.auth_service.id]
  }

  depends_on = [
    aws_lb_listener.main,
    aws_iam_role_policy.auth_service
  ]

  tags = {
    Name        = "auth-service"
    Environment = var.environment
    Component   = "backend"
  }
}

resource "aws_ecs_task_definition" "auth_service" {
  family                   = "auth-service"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.auth_service.arn

  container_definitions = jsonencode([
    {
      name  = "auth-api"
      image = "${var.ecr_repository}/auth-service:${var.image_tag}"

      portMappings = [
        {
          containerPort = 3000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "NODE_ENV"
          value = var.environment
        },
        {
          name  = "DATABASE_HOST"
          value = aws_db_instance.main.endpoint
        },
        {
          name  = "REDIS_HOST"
          value = aws_elasticache_cluster.main.cache_nodes[0].address
        }
      ]

      secrets = [
        {
          name      = "JWT_SECRET"
          valueFrom = aws_secretsmanager_secret.jwt_secret.arn
        },
        {
          name      = "DATABASE_PASSWORD"
          valueFrom = aws_secretsmanager_secret.db_password.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.auth_service.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "auth"
        }
      }
    }
  ])
}

# JWT Secret for authentication
resource "aws_secretsmanager_secret" "jwt_secret" {
  name        = "${var.environment}-jwt-secret"
  description = "JWT secret for auth service"

  tags = {
    Name        = "jwt-secret"
    Environment = var.environment
    UsedBy      = "auth-service"
  }
}

# Database instance
resource "aws_db_instance" "main" {
  identifier           = "${var.environment}-auth-db"
  engine               = "postgres"
  engine_version       = "14.7"
  instance_class       = var.db_instance_class
  allocated_storage    = 20
  storage_encrypted    = true

  db_name  = "authdb"
  username = "admin"
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"

  tags = {
    Name        = "auth-database"
    Environment = var.environment
  }
}

# Security group for auth service
resource "aws_security_group" "auth_service" {
  name        = "${var.environment}-auth-service-sg"
  description = "Security group for auth service"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "auth-service-sg"
    Environment = var.environment
  }
}
