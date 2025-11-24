#!/bin/bash
set -e

echo "🚀 Deploying complete stack..."
RG_NAME="rg-case"

cd terraform
REGISTRY=$(terraform output -raw container_registry_name)
BACKEND_APP=$(terraform output -raw web_app_name)
FRONTEND_APP=$(terraform output -raw frontend_app_name)
BACKEND_URL=$(terraform output -raw web_app_url | sed 's|https://||')
FRONTEND_URL=$(terraform output -raw frontend_app_url | sed 's|https://||')
cd ..

echo "Registry: $REGISTRY | Backend: $BACKEND_APP | Frontend: $FRONTEND_APP"

# Backend
cd backend
VERSION=$(cat version.txt)
IFS='.' read -r major minor patch <<< "$VERSION"
NEW_VERSION="$major.$minor.$((patch + 1))"

echo "📦 Building backend:$NEW_VERSION"
az acr build --registry $REGISTRY --image question-answer-api:${NEW_VERSION} --image question-answer-api:latest .
echo $NEW_VERSION > version.txt

echo "Updating backend..."
az webapp sitecontainers update \
    --name $BACKEND_APP \
    --resource-group $RG_NAME \
    --container-name main \
    --image ${REGISTRY}.azurecr.io/question-answer-api:latest \
    --target-port 8000 \
    --is-main true

az webapp restart --name $BACKEND_APP --resource-group $RG_NAME
cd ..

# Frontend
cd frontend
VERSION=$(cat version.txt)
IFS='.' read -r major minor patch <<< "$VERSION"
NEW_VERSION="$major.$minor.$((patch + 1))"

echo "📦 Building frontend:$NEW_VERSION"
az acr build --registry $REGISTRY --image question-answer-frontend:${NEW_VERSION} --image question-answer-frontend:latest .
echo $NEW_VERSION > version.txt

echo "Updating frontend..."
az webapp sitecontainers update \
    --name $FRONTEND_APP \
    --resource-group $RG_NAME \
    --container-name main \
    --image ${REGISTRY}.azurecr.io/question-answer-frontend:latest \
    --target-port 80 \
    --is-main true

az webapp restart --name $FRONTEND_APP --resource-group $RG_NAME
cd ..

# Configure
echo "🔗 Configuring apps..."
az webapp config appsettings set --name $BACKEND_APP --resource-group $RG_NAME --settings CORS_ORIGINS="https://$FRONTEND_URL" --output none
az webapp config appsettings set --name $FRONTEND_APP --resource-group $RG_NAME --settings VITE_API_URL="https://$BACKEND_URL" --output none
az webapp restart --name $BACKEND_APP --resource-group $RG_NAME --output none
az webapp restart --name $FRONTEND_APP --resource-group $RG_NAME --output none

# Health checks
echo "🏥 Health checks..."
sleep 15

for i in {1..10}; do
    curl -sf https://${BACKEND_URL}/health > /dev/null 2>&1 && echo "✅ Backend healthy!" && break
    echo "⏳ Backend $i/10..."
    sleep 5
done

for i in {1..10}; do
    curl -sf https://${FRONTEND_URL} > /dev/null 2>&1 && echo "✅ Frontend healthy!" && break
    echo "⏳ Frontend $i/10..."
    sleep 5
done

echo ""
echo "🎉 Complete!"
echo "📱 Frontend: https://$FRONTEND_URL"
echo "🔌 Backend: https://$BACKEND_URL"
