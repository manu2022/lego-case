#!/bin/bash
# Script to create Azure Storage backend for Terraform state

set -e

echo "🔧 Setting up Terraform remote backend in Azure Storage..."

# Configuration
RESOURCE_GROUP="rg-terraform-state"
STORAGE_ACCOUNT="tfstatelego$(openssl rand -hex 4)"  # Random suffix for uniqueness
CONTAINER_NAME="tfstate"
LOCATION="westeurope"

# Create resource group
echo "Creating resource group: $RESOURCE_GROUP"
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION \
  --tags "purpose=terraform-state" "project=lego-case"

# Create storage account
echo "Creating storage account: $STORAGE_ACCOUNT"
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --encryption-services blob \
  --tags "purpose=terraform-state" "project=lego-case"

# Get storage account key
ACCOUNT_KEY=$(az storage account keys list \
  --resource-group $RESOURCE_GROUP \
  --account-name $STORAGE_ACCOUNT \
  --query '[0].value' \
  --output tsv)

# Create blob container
echo "Creating blob container: $CONTAINER_NAME"
az storage container create \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT \
  --account-key $ACCOUNT_KEY \
  --public-access off

# Enable versioning for state file protection
echo "Enabling versioning on storage account..."
az storage account blob-service-properties update \
  --account-name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --enable-versioning true

# Create backend configuration file
cat > backend-config.tfbackend << EOF
resource_group_name  = "$RESOURCE_GROUP"
storage_account_name = "$STORAGE_ACCOUNT"
container_name       = "$CONTAINER_NAME"
key                  = "lego-case.tfstate"
EOF

echo ""
echo "✅ Terraform backend created successfully!"
echo ""
echo "📝 Backend Configuration:"
echo "  Resource Group:    $RESOURCE_GROUP"
echo "  Storage Account:   $STORAGE_ACCOUNT"
echo "  Container:         $CONTAINER_NAME"
echo ""
echo "🔒 Add these as GitHub Secrets for CI/CD:"
echo "  TF_BACKEND_RESOURCE_GROUP=$RESOURCE_GROUP"
echo "  TF_BACKEND_STORAGE_ACCOUNT=$STORAGE_ACCOUNT"
echo "  TF_BACKEND_CONTAINER=$CONTAINER_NAME"
echo ""
echo "📋 Next steps:"
echo "  1. Update providers.tf with the backend configuration"
echo "  2. Run: terraform init -migrate-state -backend-config=backend-config.tfbackend"
echo "  3. Add backend-config.tfbackend to .gitignore (already done)"
echo ""

