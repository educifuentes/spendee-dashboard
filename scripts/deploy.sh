#!/bin/bash

# Load configuration from central config file
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." >/dev/null 2>&1 && pwd)
CONFIG_FILE="$PROJECT_ROOT/config/deploy.toml"

get_config_value() {
    local key=$1
    grep -E "^${key}[[:space:]]*=" "$CONFIG_FILE" | sed -E 's/.*=[[:space:]]*"(.*)".*/\1/'
}

SERVICE_NAME=$(get_config_value "service_name")
REGION=$(get_config_value "region")
SECRET_NAME=$(get_config_value "secret_name")
REPO_NAME=$(get_config_value "repo_name")
PROJECT_ID=$(get_config_value "project_id")
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
