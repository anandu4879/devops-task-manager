output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "ec2_instance_id" {
  description = "Set this as the EC2_INSTANCE_ID GitHub secret"
  value       = aws_instance.app.id
}

output "ec2_public_ip" {
  value = aws_instance.app.public_ip
}

output "app_health_url" {
  description = "Set this as the APP_HEALTH_URL GitHub secret"
  value       = "http://${aws_instance.app.public_ip}"
}

output "github_actions_role_arn" {
  description = "Set this as the AWS_DEPLOY_ROLE_ARN GitHub secret"
  value       = aws_iam_role.github_actions.arn
}
