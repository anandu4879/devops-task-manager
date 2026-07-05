variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix used for tagging and resource names"
  type        = string
  default     = "task-manager"
}

variable "instance_type" {
  description = "EC2 instance type (t3.micro / t2.micro are free-tier eligible)"
  type        = string
  default     = "t3.micro"
}

variable "github_repo" {
  description = "GitHub repo in 'owner/repo' form, used to scope the OIDC trust policy"
  type        = string
  # e.g. "yourusername/devops-task-manager"
}

variable "allowed_http_cidr" {
  description = "CIDR allowed to reach the app on port 80"
  type        = string
  default     = "0.0.0.0/0"
}
