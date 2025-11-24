#!/bin/bash
# Script to copy environment variables from .env to terraform.tfvars

set -e

# Load .env file
ENV_FILE="../.env"
[ ! -f "$ENV_FILE" ] && echo "Error: .env file not found at $ENV_FILE" && exit 1

# Export variables from .env (strip quotes and spaces)
while IFS= read -r line; do
  # Skip comments and empty lines
  [[ "$line" =~ ^[[:space:]]*# ]] && continue
  [[ -z "$line" ]] && continue
  
  # Remove quotes and spaces around =
  line=$(echo "$line" | sed -E 's/[[:space:]]*=[[:space:]]*/=/' | sed 's/"//g' | sed "s/'//g")
  
  # Export the variable
  export "$line"
done < "$ENV_FILE"

# Set defaults
LANGFUSE_BASE_URL=${LANGFUSE_BASE_URL:-http://langfuse.legocase.com}

# Validate required variables
missing=()
[ -z "$OPENAI_API_KEY" ] && missing+=("OPENAI_API_KEY")
[ -z "$LANGFUSE_SECRET_KEY" ] && missing+=("LANGFUSE_SECRET_KEY")
[ -z "$LANGFUSE_PUBLIC_KEY" ] && missing+=("LANGFUSE_PUBLIC_KEY")

if [ ${#missing[@]} -gt 0 ]; then
    echo "Error: Missing required variables: ${missing[*]}"
    exit 1
fi

# Create terraform.tfvars
cat > terraform.tfvars << EOF
resource_group_name = "rg-case"

openai_api_key      = "${OPENAI_API_KEY}"
langfuse_secret_key = "${LANGFUSE_SECRET_KEY}"
langfuse_public_key = "${LANGFUSE_PUBLIC_KEY}"
langfuse_base_url   = "${LANGFUSE_BASE_URL}"
EOF

echo "✅ terraform.tfvars created successfully!"

