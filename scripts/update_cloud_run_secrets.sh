#!/bin/bash
set -e

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
PROJECT_ID=$(get_config_value "project_id")
SECRETS_FILE=$(get_config_value "secrets_file")

# Colors (simpler ANSI codes compatible with most terminals)
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Secrets Update for $SERVICE_NAME...${NC}"

# Pre-check: Verify secrets file exists
if [ ! -f "$SECRETS_FILE" ]; then
    echo -e "${RED}Error: Local secrets file '$SECRETS_FILE' not found!${NC}"
    exit 1
fi

# 0. Ensure Secret Manager API is enabled
echo -e "\n${YELLOW}--- Step 0: Checking Secret Manager API ---${NC}"
if ! gcloud services list --enabled --project="$PROJECT_ID" --filter="config.name:secretmanager.googleapis.com" --format="value(config.name)" | grep -q "secretmanager.googleapis.com"; then
    echo "Secret Manager API is not enabled. Enabling it now..."
    gcloud services enable secretmanager.googleapis.com --project="$PROJECT_ID"
    echo "API enabled."
else
    echo "Secret Manager API is already enabled."
fi

# 1. Upload Secrets to Secret Manager
echo -e "\n${YELLOW}--- Step 1: Uploading Secrets to Secret Manager ---${NC}"

# Check if secret exists. valid_secret will be true (0) if describe succeeds.
# We add --quiet to avoid interactive prompts that cause scripts to hang.
if gcloud secrets describe "$SECRET_NAME" --project="$PROJECT_ID" --quiet >/dev/null 2>&1; then
    echo "Secret '$SECRET_NAME' exists. Adding new version..."
else
    echo "Secret '$SECRET_NAME' not found. Creating new secret..."
    gcloud secrets create "$SECRET_NAME" --replication-policy="automatic" --project="$PROJECT_ID" --quiet
    echo "Secret created."
fi

echo "Uploading contents of $SECRETS_FILE..."
gcloud secrets versions add "$SECRET_NAME" --data-file="$SECRETS_FILE" --project="$PROJECT_ID" --quiet

# 2. Grant Access
echo -e "\n${YELLOW}--- Step 2: Granting Access to Cloud Run Service Account ---${NC}"

# Attempt to get the service account from the running service
# We capture stderr to null to avoid noise if the service doesn't exist yet or other errors
EXISTING_SA=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="value(spec.template.spec.serviceAccountName)" --quiet 2>/dev/null || true)

if [ -n "$EXISTING_SA" ]; then
    SERVICE_ACCOUNT="$EXISTING_SA"
    echo "Found configured Service Account: $SERVICE_ACCOUNT"
else
    # Fallback: Construct the default compute service account
    echo "Could not retrieve service account (service might not exist yet)."
    echo "Fetching project number to determine default compute service account..."
    PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)" --quiet)
    SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
    echo -e "${YELLOW}Using default Compute Engine Service Account: $SERVICE_ACCOUNT${NC}"
fi

echo "Granting 'roles/secretmanager.secretAccessor' to $SERVICE_ACCOUNT..."
gcloud secrets add-iam-policy-binding "$SECRET_NAME" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" \
    --project="$PROJECT_ID" \
    --quiet >/dev/null

# 3. Update Cloud Run Service
echo -e "\n${YELLOW}--- Step 3: Updating Cloud Run Service to Mount Secret ---${NC}"

if gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --quiet >/dev/null 2>&1; then
    echo "Updating Cloud Run service to mount the secret at /app/.streamlit/secrets.toml..."
    gcloud run services update "$SERVICE_NAME" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --set-secrets="/app/.streamlit/secrets.toml=${SECRET_NAME}:latest" \
        --quiet
    echo -e "\n${GREEN}✅ Secrets updated and service re-deployed successfully!${NC}"
else
    echo -e "\n${YELLOW}Service '$SERVICE_NAME' does not exist yet. Skipping service update. It will be configured during initial deployment.${NC}"
    echo -e "\n${GREEN}✅ Secrets uploaded and ready for initial deployment!${NC}"
fi
