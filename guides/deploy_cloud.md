# Cloud Deployment

This repository serves as a generic boilerplate designed to run effortlessly on major cloud providers.

## Google Cloud / Cloud Run
If utilizing a Dockerized environment (e.g. for Streamlit Dashboards):
1. **Build Container:** `gcloud builds submit --tag gcr.io/[PROJECT_ID]/data-platform`
2. **Deploy:** `gcloud run deploy --image gcr.io/[PROJECT_ID]/data-platform --platform managed`

## AWS / ECS (Fargate)
Deploy a task definition pulling from ECR, ensuring environment parameters are passed according to `[ENVIRONMENT_VARS]` guidelines.

## Best Practices
- **Secret Management:** Hardcoded credentials should never enter git. Always mount via Secrets Manager.
- **CI/CD Automation:** Attach continuous deployments strictly to `main` via cloudbuild or AWS CodePipeline.
