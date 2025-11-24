#!/bin/bash
set -e

echo "🚀 Deploying complete stack to Azure..."

RG_NAME="rg-case"

# Get resource information
echo "📋 Getting Azure resources..."
cd terraform
REGISTRY=$(terraform output -raw container_registry_name)
BACKEND_APP=$(terraform output -raw web_app_name)
FRONTEND_APP=$(terraform output -raw frontend_app_name)
BACKEND_URL=$(terraform output -raw web_app_url | sed 's|https://||')
FRONTEND_URL=$(terraform output -raw frontend_app_url | sed 's|https://||')
cd ..

echo "   Registry: $REGISTRY"
echo "   Backend App: $BACKEND_APP"
echo "   Frontend App: $FRONTEND_APP"
echo "   Backend URL: https://$BACKEND_URL"
echo "   Frontend URL: https://$FRONTEND_URL"
echo ""

# Deploy Backend
echo "📦 Building and deploying backend..."
cd backend
VERSION=$(cat version.txt)
IFS='.' read -r major minor patch <<< "$VERSION"
NEW_VERSION="$major.$minor.$((patch + 1))"

echo "   Building version: $NEW_VERSION"

az acr build \
    --registry $REGISTRY \
    --image question-answer-api:${NEW_VERSION} \
    --image question-answer-api:latest \
    .

echo $NEW_VERSION > version.txt

echo "   Updating backend container..."
az webapp config container set \
    --name $BACKEND_APP \
    --resource-group $RG_NAME \
    --docker-custom-image-name ${REGISTRY}.azurecr.io/question-answer-api:latest \
    --docker-registry-server-url https://${REGISTRY}.azurecr.io

az webapp restart --name $BACKEND_APP --resource-group $RG_NAME
cd ..

# Deploy Frontend
echo ""
echo "📦 Building and deploying frontend..."
cd frontend
VERSION=$(cat version.txt)
IFS='.' read -r major minor patch <<< "$VERSION"
NEW_VERSION="$major.$minor.$((patch + 1))"

echo "   Building version: $NEW_VERSION"

az acr build \
    --registry $REGISTRY \
    --image question-answer-frontend:${NEW_VERSION} \
    --image question-answer-frontend:latest \
    .

echo $NEW_VERSION > version.txt

echo "   Updating frontend container..."
az webapp config container set \
    --name $FRONTEND_APP \
    --resource-group $RG_NAME \
    --docker-custom-image-name ${REGISTRY}.azurecr.io/question-answer-frontend:latest \
    --docker-registry-server-url https://${REGISTRY}.azurecr.io

az webapp restart --name $FRONTEND_APP --resource-group $RG_NAME
cd ..

# Configure cross-references
echo ""
echo "🔗 Configuring app settings..."

echo "   Setting backend CORS to allow frontend..."
az webapp config appsettings set \
    --name $BACKEND_APP \
    --resource-group $RG_NAME \
    --settings CORS_ORIGINS="https://$FRONTEND_URL" \
    --output none

echo "   Setting frontend API URL to backend..."
az webapp config appsettings set \
    --name $FRONTEND_APP \
    --resource-group $RG_NAME \
    --settings VITE_API_URL="https://$BACKEND_URL" \
    --output none

# Restart apps to apply settings
echo "   Restarting apps..."
az webapp restart --name $BACKEND_APP --resource-group $RG_NAME --output none
az webapp restart --name $FRONTEND_APP --resource-group $RG_NAME --output none

# Health checks
echo ""
echo "🏥 Performing health checks..."

sleep 15

echo "   Checking backend..."
for i in {1..10}; do
    if curl -sf https://${BACKEND_URL}/health > /dev/null 2>&1; then
        echo "   ✅ Backend is healthy!"
        break
    fi
    echo "   ⏳ Attempt $i/10..."
    sleep 5
done

echo "   Checking frontend..."
for i in {1..10}; do
    if curl -sf https://${FRONTEND_URL} > /dev/null 2>&1; then
        echo "   ✅ Frontend is healthy!"
        break
    fi
    echo "   ⏳ Attempt $i/10..."
    sleep 5
done

echo ""
echo "🎉 Deployment complete!"
echo "📱 Frontend: https://$FRONTEND_URL"
echo "🔌 Backend: https://$BACKEND_URL"
echo ""
echo "Test the application by visiting the frontend URL and uploading an image!"

