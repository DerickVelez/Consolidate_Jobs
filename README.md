################################################################################
# Terraform Configuration for ECS Fargate + RDS
#
# This set of files describes the AWS infrastructure for:
# 1. A new VPC with two public subnets in different Availability Zones.
# 2. An ECR repository to store the application's Docker image.
# 3. An RDS PostgreSQL database instance.
# 4. An ECS Fargate cluster.
# 5. An ECS Task Definition for a Flask application.
# 6. An ECS Service to run the Flask task and expose it publicly.
# 7. Security groups to control traffic between the services.
#
################################################################################

# ------------------------------------------------------------------------------
# main.tf
# ------------------------------------------------------------------------------

terraform {
  backend "s3" {
    bucket = "flask-api-practice-deployment"
    key    = "terraform/infrastructure.tfstate"
    region = "us-east-1"
    use_lockfile = true
  }
}

provider "aws" {
  region = var.aws_region
}

################################################################################
# NETWORKING
# A custom VPC with two public subnets for High Availability.
################################################################################

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "main-vpc"
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

# Public Subnet in the first AZ
resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.5.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true # Essential for public subnets

  tags = {
    Name = "public-subnet-a"
  }
}

# Public Subnet in the second AZ
resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.6.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true # Essential for public subnets

  tags = {
    Name = "public-subnet-b"
  }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "main-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "public-route-table"
  }
}

# Associate route table with the first public subnet
resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

# Associate route table with the second public subnet
resource "aws_route_table_association" "public_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}

################################################################################
# SECURITY GROUPS
# Controls what traffic is allowed to/from our services.
################################################################################

# Security group for the ECS Fargate service
resource "aws_security_group" "ecs_service_sg" {
  name        = "ecs-service-sg"
  description = "Allow HTTP inbound traffic for Flask app"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5000 # The port our Flask app runs on
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allow traffic from anywhere
  }

  ingress {
    from_port   = 3000 # The port our Flask app runs on
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allow traffic from anywhere
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ecs-service-sg"
  }
}

# Security group for the RDS database
resource "aws_security_group" "rds_sg" {
  name        = "rds-sg"
  description = "Allow Postgres inbound traffic from the ECS service"
  vpc_id      = aws_vpc.main.id

  # Allow inbound traffic from the ECS service security group
  ingress {
    from_port       = 5432 # PostgreSQL port
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_service_sg.id]
  }

    # Allow ALL inbound traffic from ANY source
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rds-sg"
  }
}

################################################################################
# ECR REPOSITORY
# A private repository to store our Flask app's Docker image.
################################################################################

resource "aws_ecr_repository" "flask_app_repo" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecr_repository" "grafana_repo" {
  name                 = var.grafana_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecr_repository" "testing_repo" {
  name                 = "testing-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

################################################################################
# DATABASE (RDS)
# A single PostgreSQL instance.
################################################################################

resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "rds-subnet-group"
  # Provide subnets from at least two AZs
  subnet_ids = [aws_subnet.public_a.id, aws_subnet.public_b.id]

  tags = {
    Name = "My RDS subnet group"
  }
}

resource "aws_db_instance" "postgres_db" {
  identifier             = "flask-db-instance"
  allocated_storage      = 10
  storage_type           = "gp2"
  engine                 = "postgres"
  engine_version         = "17.4"
  instance_class         = "db.t3.micro"
  db_name                = var.db_name
  username               = var.db_user
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  publicly_accessible    = true # As requested for testing
  skip_final_snapshot    = true # For easy cleanup in testing
}

################################################################################
# ECS FARGATE
# The cluster, task definition, and service for our Flask app.
################################################################################

resource "aws_ecs_cluster" "main" {
  name = "flask-cluster"
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecs-task-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_task_definition" "flask_app" {
  family                   = "flask-app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"  # 0.25 vCPU
  memory                   = "512"  # 0.5 GB
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "flask-container"
      image     = "${aws_ecr_repository.flask_app_repo.repository_url}:${var.image_tag}"
      essential = true
      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
        }
      ]
      # Pass database credentials to the container securely
      environment = [
        {
          name  = "DATABASE_HOST"
          value = aws_db_instance.postgres_db.address
        },
        {
          name  = "DATABASE_NAME"
          value = var.db_name
        },
        {
          name  = "DATABASE_USER"
          value = var.db_user
        },
        {
          name  = "DATABASE_PASSWORD"
          value = var.db_password
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/flask-app"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  depends_on = [
    aws_db_instance.postgres_db
  ]
}

resource "aws_ecs_task_definition" "grafana_app" {
  family                   = "grafana-app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"  # 0.25 vCPU
  memory                   = "2048"  # 0.5 GB
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "grafana-container"
      image     = "${aws_ecr_repository.grafana_repo.repository_url}:${var.image_tag}"
      essential = true
      portMappings = [
        {
          containerPort = 3000
          hostPort      = 3000
        }
      ]
      # Pass database credentials to the container securely
      environment = [
        {
          name  = "GF_DATABASE_TYPE"
          value = "postgres"
        },
        {
          name  = "GF_DATABASE_HOST"
          value = aws_db_instance.postgres_db.address
        },
        {
          name  = "GF_DATABASE_NAME"
          value = var.db_name
        },
        {
          name  = "GF_DATABASE_USER"
          value = var.db_user
        },
        {
          name  = "GF_DATABASE_PASSWORD"
          value = var.db_password
        },
        {
          name  = "GF_DATABASE_SSL_MODE"
          value = "require"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/grafana-app"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  depends_on = [
    aws_db_instance.postgres_db
  ]
}

resource "aws_cloudwatch_log_group" "flask_app_logs" {
  name = "/ecs/flask-app"
}

resource "aws_cloudwatch_log_group" "grafana_app_logs" {
  name = "/ecs/grafana-app"
}

resource "aws_ecs_service" "flask_service" {
  name            = "flask-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.flask_app.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    # Allow the service to launch tasks in either public subnet
    subnets         = [aws_subnet.public_a.id, aws_subnet.public_b.id]
    security_groups = [aws_security_group.ecs_service_sg.id]
    assign_public_ip = true # Give our Fargate task a public IP
  }

  # This ensures the service doesn't try to start before the IGW is ready
  depends_on = [aws_internet_gateway.gw]
}

resource "aws_ecs_service" "grafana_service" {
  name            = "grafana-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.grafana_app.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    # Allow the service to launch tasks in either public subnet
    subnets         = [aws_subnet.public_a.id, aws_subnet.public_b.id]
    security_groups = [aws_security_group.ecs_service_sg.id]
    assign_public_ip = true # Give our Fargate task a public IP
  }

  # This ensures the service doesn't try to start before the IGW is ready
  depends_on = [aws_internet_gateway.gw]
}


# ------------------------------------------------------------------------------
# variables.tf
# ------------------------------------------------------------------------------

variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "ecr_repository_name" {
  description = "The name for the ECR repository."
  type        = string
  default     = "my-flask-app"
}

variable "grafana_repository_name" {
  description = "The name for the ECR repository for grafana."
  type        = string
  default     = "my-grafana"
}

variable "image_tag" {
  description = "The tag of the Docker image to use (e.g., 'latest')."
  type        = string
  default     = "latest"
}

variable "db_name" {
  description = "The name of the PostgreSQL database."
  type        = string
  default     = "flaskdb"
}

variable "db_user" {
  description = "The username for the PostgreSQL database."
  type        = string
  default     = "flaskadmin"
}

variable "db_password" {
  description = "The password for the PostgreSQL database."
  type        = string
  default = "Admin123456!"
  sensitive   = true # Marks this as sensitive in Terraform output
}

--------github action deployment.yaml
name: Deployment Workflow

on:
  push:
    branches:
      - main
      - development

jobs:
  deploy_applications:
    runs-on: self-hosted
    environment: ${{ github.ref_name }}
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
      - name: Print Selected Branch
        run: |
          echo "The selected branch is: ${GITHUB_REF#refs/heads/}"
          echo "MY_ENV_VAR value is: $MY_ENV_VAR 1111"
          echo "test value ${MY_ENV_VAR}"
          echo ${{ vars.MY_ENV_VAR }}
          echo ${{ vars.MY_ENV_VAR }} this is running on our test machine
          echo test again
      - name: Check Runner Hostname
        run: hostname
      - name: Go to IAC code
        run: |
          cd infrastructure_code
          ls -la
          terraform init
          terraform apply --auto-approve
      - name: execute aws ecr login command
        run: aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 975391190725.dkr.ecr.us-east-1.amazonaws.com
      - name: assign credentials to docker login
        run: sudo docker login -u AWS -p $(aws ecr get-login-password) 975391190725.dkr.ecr.us-east-1.amazonaws.com/my-flask-app:latest
      - name: build docker images
        run: sudo docker build -t my-flask-app .
      - name: tag docker image
        run: sudo docker tag my-flask-app:latest 975391190725.dkr.ecr.us-east-1.amazonaws.com/my-flask-app:latest
      - name: tag docker image
        run: sudo docker push 975391190725.dkr.ecr.us-east-1.amazonaws.com/my-flask-app:latest
      - name: update ecr service
        run: aws ecs update-service --cluster flask-cluster --service flask-service --force-new-deployment
      - name: tag docker image
        run: sudo docker tag grafana/grafana-oss:latest 975391190725.dkr.ecr.us-east-1.amazonaws.com/my-grafana:latest
      - name: tag docker image
        run: sudo docker push 975391190725.dkr.ecr.us-east-1.amazonaws.com/my-grafana:latest
      - name: update ecr service
        run: aws ecs update-service --cluster flask-cluster --service grafana-service --force-new-deployment
    
    
    
    ------------project

    
from flask import Flask, jsonify, abort, request
import redis
from datetime import datetime
from functools import wraps
import json
from .decorators.auth import auth_sample

app = Flask(__name__)

app.config["TOTAL_CALLS"] = 0
r = redis.Redis(host='localhost', port=6379, db=0)

def update_api_request_count(api_key: str) -> int:
    existing_redis = r.get(api_key)
    if existing_redis:
        existing_redis = str(int(existing_redis) + 1)
        r.set(api_key, existing_redis)
    else:
        existing_redis = str(1)
        r.set(api_key, existing_redis)
    return int(existing_redis)
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="ratelimit exceeded", message="You have exceeded your request rate"), 429


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error="Huy wala naman yun hinahanap mo"), 404



def logger_redis(func):
    @wraps(func)
    def inner(*args, **kwargs):
        log_key = datetime.now().strftime("%Y%m%d%H%M%S") + "_logs"
        r.set(log_key, "this is just a logging example")
        result = func(*args, **kwargs)
        query_params = request.args.to_dict()
        after_key_logs = datetime.now().strftime("%Y%m%d%H%M%S") + "_after_logs_query_params"
        object_to_log = {
            "query_params": query_params,
            "result": result,
        }
        r.set(after_key_logs, json.dumps(object_to_log))

        return result
    return inner


@app.route("/api/weather", methods=["GET"])
@logger_redis
@auth_sample
def get_weather():
    query_params = request.args.to_dict()
    api_key = query_params.get("apiKey","default")
    call_count = update_api_request_count(api_key)
    if call_count <= 12:
        return {
            "test": 123,
            "name": "testname",
            "counter": app.config["TOTAL_CALLS"],
            "call_count": call_count,
        }
    else:
        abort(429)

@app.route("/api/customers", methods=["GET"])
@auth_sample
def get_customers():
    return {
        "customers": ["alvin","diane","derick"]
    }
-------------auth.py  
from functools import wraps

from flask import abort, request


def auth_sample(func):
    @wraps(func)
    def inner(*args, **kwargs):
        query_params = request.args.to_dict()
        if query_params.get("apiKey") is None or query_params.get("apiKey") == "":
            abort(401)
        result = func(*args, **kwargs)
        return result
    return inner
    
