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
  #
  # backend "s3" {
  #   bucket         = "your-unique-tfstate-bucket-name"
  #   key            = "task-manager/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region
}
