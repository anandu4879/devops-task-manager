terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Create the S3 bucket + DynamoDB table manually ONCE before using this
  # backend (see README "Bootstrap remote state" section), then uncomment:

  backend "s3" {
     bucket         = "anandu-devops-tfstate-2026"
     key            = "task-manager/terraform.tfstate"
     region         = "ap-south-1"
     #dynamodb_table = "terraform-locks"
     use_lockfile = true
     encrypt        = true
   }
}

provider "aws" {
  region = var.aws_region
}
