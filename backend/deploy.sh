#!/bin/bash

set -e

# Get registry name from Terraform output
cd ../terraform
REGISTRY_NAME=$(terraform output -raw container_registry_name)
cd ../backend

IMAGE_NAME="question-answer-api"

# Get version from file or use default
if [ -f version.txt ]; then
    VERSION=$(cat version.txt)
else
    VERSION="0.1.0"
fi

# Increment patch version
IFS='.' read -r major minor patch <<< "$VERSION"
patch=$((patch + 1))
NEW_VERSION="$major.$minor.$patch"

echo "Building version: $NEW_VERSION"
echo "Using registry: $REGISTRY_NAME"

# Login to Azure
az login

# Build and push using Azure Container Registry (handles multi-arch automatically)
az acr build \
    --registry $REGISTRY_NAME \
    --image ${IMAGE_NAME}:${NEW_VERSION} \
    --image ${IMAGE_NAME}:latest \
    .

# Save new version
echo $NEW_VERSION > version.txt

echo "✅ Deployed ${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:${NEW_VERSION}"

