# Task Manager — End-to-End CI/CD Pipeline

A small Flask task-tracking API used as the vehicle for a complete, production-style
CI/CD pipeline: Git → GitHub Actions → Docker → Amazon ECR → Terraform-provisioned
AWS infrastructure → EC2, deployed with zero long-lived AWS credentials via OIDC.

## Architecture

```
Developer → git push → GitHub Actions (CI: lint, test, build)
                              │
                        (on merge to main)
                              ▼
                    GitHub Actions (CD)
                    │  assumes AWS IAM role via OIDC (no static keys)
                    ▼
              Build & push Docker image → Amazon ECR
                              │
                              ▼
            AWS SSM Send-Command → EC2 instance
            (pulls new image, restarts container)
                              │
                              ▼
                   Flask app live on port 80
                   Infra provisioned by Terraform:
                   VPC, subnet, security group, EC2,
                   ECR repo, IAM roles (S3+DynamoDB state)
```

## Why these choices

- **EC2 over ECS/EKS**: keeps the infra simple and free-tier eligible while still
  demonstrating the full pipeline. No control-plane cost like EKS.
- **SSM Send-Command instead of SSH**: no open port 22, no SSH key management —
  the EC2 instance only needs an IAM role.
- **OIDC instead of AWS access keys in GitHub Secrets**: GitHub Actions assumes a
  short-lived IAM role scoped to this repo, so there are no long-lived credentials
  to leak or rotate.
- **SQLite instead of RDS**: keeps the whole thing inside the free tier; the
  pipeline concepts are unaffected by the database choice.

## Local development

```bash
cd app
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py
# in another terminal:
curl http://localhost:5000/health
curl -X POST http://localhost:5000/tasks -H "Content-Type: application/json" -d '{"title":"Try it out"}'
```

## Run with Docker locally

```bash
cd app
docker build -t task-manager .
docker run -p 5000:5000 -v task-data:/data task-manager
curl http://localhost:5000/health
```

## Deploying to AWS

### 1. Bootstrap remote state (one-time, manual)
Create an S3 bucket and DynamoDB table for Terraform state (console or CLI),
then uncomment the `backend "s3" {}` block in `terraform/versions.tf` with your
bucket name.

### 2. Provision infrastructure
```bash
cd terraform
terraform init
terraform plan -var="github_repo=yourusername/your-repo-name"
terraform apply -var="github_repo=yourusername/your-repo-name"
```

### 3. Configure GitHub repo secrets
From `terraform output`, copy these into **Settings → Secrets and variables → Actions**:
- `AWS_DEPLOY_ROLE_ARN` ← `github_actions_role_arn`
- `EC2_INSTANCE_ID` ← `ec2_instance_id`
- `APP_HEALTH_URL` ← `app_health_url`

### 4. Push to main
The `deploy.yml` workflow builds, pushes to ECR, and deploys automatically.

### 5. Tear down when done (avoid ongoing cost)
```bash
terraform destroy -var="github_repo=yourusername/your-repo-name"
```

## Cost

Everything here fits comfortably in the AWS Free Tier (EC2 t3.micro, ECR under
500MB, S3/DynamoDB at this scale). Run `terraform destroy` after you've taken
your screenshots and demoed it so nothing keeps billing.

## Screenshot checklist (for LinkedIn / portfolio)

1. GitHub repo structure (`app/`, `terraform/`, `.github/workflows/`)
2. Branch protection rule settings page
3. `docker build` + `docker run` + curl output in terminal
4. GitHub Actions — green CI run, pipeline graph view
5. `terraform plan` output (resource creation summary)
6. AWS Console — ECR repo showing pushed image
7. AWS Console — running EC2 instance
8. Live app response (browser or curl hitting the public IP)
9. CloudWatch/SSM command output confirming deploy
10. Architecture diagram (see below)

## Roadmap (future iterations)

- Staging vs. production environments via Terraform workspaces
- CloudWatch alarms on failed deploys
- Secrets via AWS Secrets Manager
