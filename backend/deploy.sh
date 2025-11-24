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

echo "✅ Built and pushed ${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:${NEW_VERSION}"

# Configuration
RESOURCE_GROUP="rg-case"
APP_NAME="question-answer-api"

echo "ℹ️  Environment variables are managed by Terraform"
echo "🔄 Updating web app with new container configuration..."

# Stop the app to minimize issues during update
az webapp stop --name $APP_NAME --resource-group $RESOURCE_GROUP

# Update container configuration using the new format
# Always use :latest tag so the app pulls the most recent image
az webapp config container set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --docker-custom-image-name ${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:latest \
    --docker-registry-server-url https://${REGISTRY_NAME}.azurecr.io

# Start the app with new configuration
az webapp start --name $APP_NAME --resource-group $RESOURCE_GROUP

echo "✅ Deployment complete!"
echo "🌐 App URL: https://${APP_NAME}.azurewebsites.net"
echo "⏱️  Waiting for app to be ready..."

# Health check
sleep 15
for i in {1..5}; do
    if curl -sf https://${APP_NAME}.azurewebsites.net/health > /dev/null; then
        echo "✅ App is healthy and responding!"
        exit 0
    fi
    echo "⏳ Attempt $i/5 - waiting for app to start..."
    sleep 10
done

echo "⚠️  Deployment completed but health check timed out. Check the app manually."
