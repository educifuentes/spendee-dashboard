#!/bin/bash

# Configuration - Update these values
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="spendee-dashboard"
REGION="southamerica-west-1"

echo "Using Project ID: $PROJECT_ID"

# Function to extract value from TOML (simple version)
get_secret() {
    grep "$1" .streamlit/secrets.toml | head -1 | cut -d'"' -f2 | cut -d"'" -f2
}

# 1. Enable APIs
echo "Enabling necessary APIs..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# 2. Build and Push Image using Cloud Build
echo "Building and pushing image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# 3. Deploy to Cloud Run
# We use ^|^ as a delimiter to avoid issues with : and , in URLs and strings
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "^|^SUPABASE_URL=$(get_secret SUPABASE_URL)|SUPABASE_KEY=$(get_secret SUPABASE_KEY)|AUTH__COOKIE_SECRET=$(get_secret cookie_secret)|AUTH__CLIENT_ID=$(get_secret client_id)|AUTH__CLIENT_SECRET=$(get_secret client_secret)|AUTH__SERVER_METADATA_URL=$(get_secret server_metadata_url)|ALLOWED_EMAILS=edu.cifuentes@gmail.com,email5@gmail.com"

echo "Deployment complete!"
echo "IMPORTANT:"
echo "1. Update your Google OAuth console with the new Redirect URI."
echo "2. You may need to update the AUTH__REDIRECT_URI env var in the Cloud Run console once you have the service URL."
