# Cloud Credentials

Managing cloud infrastructure requires appropriate permissions. Do NOT commit secrets like Google Cloud or AWS tokens to git. 

## Establishing Roles
The runtime Service Account (or IAM Role) requires:
* Storage read/write permissions for datasets (e.g. S3 Data Lake, BigQuery, or GCS buckets).
* Required invocation/logging permissions.

## Local Configuration Flow
1. Install the CLI for your respective cloud (e.g. `gcloud`, `aws-cli`).
2. Run standard local auth tools (e.g. `gcloud auth application-default login`).
3. Your local development scripts should gracefully default back to local profile settings if environment variables are not supplied.
