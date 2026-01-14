#!/usr/bin/env bash
set -euo pipefail

# Streamlit global config directory
mkdir -p ~/.streamlit

# 1) Streamlit server config (config.toml)
cat > ~/.streamlit/config.toml << EOF
[server]
headless = true
port = ${PORT}
enableCORS = false
address = "0.0.0.0"
EOF

# 2) Streamlit secrets (secrets.toml) used by st.secrets / st.login()
# Values are read from Heroku Config Vars (environment variables).
cat > ~/.streamlit/secrets.toml << EOF
[auth]
redirect_uri = "${AUTH_REDIRECT_URI}"
cookie_secret = "${AUTH_COOKIE_SECRET}"

[auth.google]
client_id = "${AUTH_CLIENT_ID}"
client_secret = "${AUTH_CLIENT_SECRET}"
EOF