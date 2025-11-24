#!/bin/bash
set -e

cd ../terraform
REGISTRY_NAME=$(terraform output -raw container_registry_name)
cd ../backend

IMAGE_NAME="question-answer-api"
RESOURCE_GROUP="rg-case"
APP_NAME="question-answer-api"

VERSION=$([ -f version.txt ] && cat version.txt || echo "0.1.0")
IFS='.' read -r major minor patch <<< "$VERSION"
NEW_VERSION="$major.$minor.$((patch + 1))"

echo "Building $IMAGE_NAME:$NEW_VERSION"
az login

az acr build --registry $REGISTRY_NAME --image ${IMAGE_NAME}:${NEW_VERSION} --image ${IMAGE_NAME}:latest .
echo $NEW_VERSION > version.txt

echo "Deploying to $APP_NAME..."
az webapp stop --name $APP_NAME --resource-group $RESOURCE_GROUP

az webapp sitecontainers update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --container-name main \
    --image ${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:latest \
    --target-port 8000 \
    --is-main true

az webapp start --name $APP_NAME --resource-group $RESOURCE_GROUP

echo "✅ Deployed! https://${APP_NAME}.azurewebsites.net"
sleep 15
for i in {1..5}; do
    curl -sf https://${APP_NAME}.azurewebsites.net/health > /dev/null && echo "✅ Healthy!" && exit 0
    echo "⏳ $i/5..."
    sleep 10
done
echo "⚠️ Check app manually"
