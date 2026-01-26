#!/bin/bash

# Configuration - Update these values
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="spendee-dashboard"
REGION="us-central1"

echo "Using Project ID: $PROJECT_ID"

# 1. Enable APIs
echo "Enabling necessary APIs..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# 2. Build and Push Image using Cloud Build
echo "Building and pushing image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# 3. Deploy to Cloud Run
# Note: We are setting environment variables that Streamlit will pick up as st.secrets.
# Nested sections use double underscores, e.g., [auth] -> AUTH__CLIENT_ID
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "^:^SUPABASE_URL=$(grep SUPABASE_URL .streamlit/secrets.toml | cut -d'"' -f2)" \
  --set-env-vars "SUPABASE_KEY=$(grep SUPABASE_KEY .streamlit/secrets.toml | cut -d'"' -f2)" \
  --set-env-vars "AUTH__REDIRECT_URI=YOUR_CLOUD_RUN_URL" \
  --set-env-vars "AUTH__COOKIE_SECRET=$(grep cookie_secret .streamlit/secrets.toml | cut -d'"' -f2)" \
  --set-env-vars "AUTH__CLIENT_ID=$(grep client_id .streamlit/secrets.toml | cut -d'"' -f2)" \
  --set-env-vars "AUTH__CLIENT_SECRET=$(grep client_secret .streamlit/secrets.toml | cut -d'"' -f2)" \
  --set-env-vars "AUTH__SERVER_METADATA_URL=$(grep server_metadata_url .streamlit/secrets.toml | cut -d'"' -f2)" \
  --set-env-vars "ALLOWED_EMAILS=edu.cifuentes@gmail.com,email5@gmail.com"

echo "Deployment complete!"
echo "IMPORTANT: Update your Google OAuth console with the new Redirect URI."
