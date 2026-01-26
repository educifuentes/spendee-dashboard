#!/bin/bash

# Configuration - RESPECTING USER UPDATED REGION
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="spendee-dashboard"
REGION="southamerica-west-1"

echo "Using Project ID: $PROJECT_ID"
echo "Using Region: $REGION"

# Function to extract value from TOML accurately
get_secret() {
    grep "^$1" .streamlit/secrets.toml | head -1 | cut -d'"' -f2 | cut -d"'" -f2
}

# 1. Enable APIs
echo "Enabling necessary APIs..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# 2. Build and Push Image
echo "Building and pushing image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# 3. Deploy to Cloud Run
# We use individual --set-env-vars to avoid delimiter issues
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "SUPABASE_URL=$(get_secret SUPABASE_URL)" \
  --set-env-vars "SUPABASE_KEY=$(get_secret SUPABASE_KEY)" \
  --set-env-vars "AUTH__COOKIE_SECRET=$(get_secret cookie_secret)" \
  --set-env-vars "AUTH__CLIENT_ID=$(get_secret client_id)" \
  --set-env-vars "AUTH__CLIENT_SECRET=$(get_secret client_secret)" \
  --set-env-vars "AUTH__SERVER_METADATA_URL=$(get_secret server_metadata_url)" \
  --set-env-vars "ALLOWED_EMAILS=edu.cifuentes@gmail.com,email5@gmail.com" \
  --set-env-vars "AUTH__REDIRECT_URI=https://spendee-dashboard-219154903837.southamerica-west1.run.app"

echo "Deployment complete!"
echo "Service URL should be: https://spendee-dashboard-219154903837.southamerica-west1.run.app"
