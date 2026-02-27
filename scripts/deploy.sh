#!/bin/bash

# Configuration
SERVICE_NAME="spendee-dashboard"
REGION="southamerica-west1"
SECRET_NAME="spendee-dashboard-secrets"
REPO_NAME="cloud-run-source-deploy" # Standard repo name
PROJECT_ID="personal-dashboards-487913"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:latest"
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "🚀 Starting Deployment Process..."

# 1. Upload and Configure Secrets
echo "--- Step 1: Uploading Secrets & Granting Access ---"
./scripts/update_cloud_run_secrets.sh

# 2. Ensure Artifact Registry Repository exists
echo "--- Step 2: Ensuring Artifact Registry Repository exists ---"
gcloud artifacts repositories describe $REPO_NAME --location=$REGION --project=$PROJECT_ID >/dev/null 2>&1 || \
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Repository for Cloud Run images" \
    --project=$PROJECT_ID

# 3. Build the Image using Cloud Build
echo "--- Step 3: Building Image with Cloud Build ---"
gcloud builds submit --project=$PROJECT_ID --tag $IMAGE_NAME .

# 4. Deploy to Cloud Run
echo "--- Step 4: Deploying to Cloud Run ---"
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --set-secrets="/app/.streamlit/secrets.toml=${SECRET_NAME}:latest" \
    --port 8080

echo "✅ Deployment complete!"
