# Task Manager — End-to-End CI/CD Pipeline

A small Flask task-tracking API used as the vehicle for a complete, production-style
CI/CD pipeline: Git → GitHub Actions → Docker → Amazon ECR → Terraform-provisioned
AWS infrastructure → EC2, deployed with zero long-lived AWS credentials via OIDC.

## Architecture

<img width="2760" height="1504" alt="daigram2 (1)" src="https://github.com/user-attachments/assets/f737d43f-845b-4a8e-92db-654ab9a84ba8" />


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
docker run -p 5001:5001 -v task-data:/data task-manager
curl http://localhost:5001/health
```

## Deploying to AWS

### 1. Bootstrap remote state (one-time, manual)
Create an S3 bucket for Terraform state (console or CLI),
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

## Terraform Daigram

<img width="1408" height="768" alt="12- terrafom archi" src="https://github.com/user-attachments/assets/38d0a552-b392-42fa-a0b1-92ba3eeb475c" />

## Docker running in the container
<img width="1440" height="816" alt="10-docker image" src="https://github.com/user-attachments/assets/f03e3189-7875-4ecb-843b-817ca8594890" />

## Status OK screenshot
<img width="1440" height="816" alt="11-health" src="https://github.com/user-attachments/assets/5f096c61-93c8-46bc-ae2e-131f7d0bafa1" />


