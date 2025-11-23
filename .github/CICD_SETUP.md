# CI/CD Pipeline Setup Guide

This repository uses GitHub Actions for automated deployment with **separate pipelines** for application and infrastructure changes.

## 🏗️ Pipeline Architecture

### 1. **Application Deployment** (`deploy-app.yml`)
- **Triggers:** Push to `main` branch (only when `backend/**` changes)
- **What it does:**
  - Builds Docker image
  - Pushes to Azure Container Registry
  - Auto-increments version
  - Deploys to Azure Container Apps
  - Runs health checks
- **Runtime:** ~3-5 minutes

### 2. **Terraform Plan** (`terraform-plan.yml`)
- **Triggers:** Pull Request to `main` (only when `terraform/**` changes)
- **What it does:**
  - Validates Terraform code
  - Generates plan
  - Comments plan on PR for review
- **Runtime:** ~1-2 minutes

### 3. **Terraform Apply** (`terraform-apply.yml`)
- **Triggers:** Push to `main` (only when `terraform/**` changes)
- **What it does:**
  - Requires manual approval (via GitHub Environment)
  - Applies infrastructure changes
  - Shows outputs in summary
- **Runtime:** ~5-10 minutes

---

## ⚙️ Setup Instructions

### Step 1: Setup Terraform Remote Backend

**Why?** Terraform state files can be large (100MB+) and should never be in Git. We use Azure Storage for remote state.

```bash
cd terraform
./setup-backend.sh
```

This creates:
- Azure Storage Account for Terraform state
- Blob container with versioning enabled
- Backend configuration file

**Save the output values** - you'll need them for GitHub Secrets.

### Step 2: Configure GitHub Secrets

Go to your repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add the following secrets:

| Secret Name | Description | How to get it |
|-------------|-------------|---------------|
| `AZURE_CREDENTIALS` | Service Principal credentials | See Step 3 below |
| `OPENAI_API_KEY` | Azure OpenAI API key | From your `.env` file |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key | From your `.env` file |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key | From your `.env` file |
| `LANGFUSE_BASE_URL` | Langfuse URL | `http://langfuse.legocase.com` |
| `TF_BACKEND_RESOURCE_GROUP` | Terraform backend RG | From `setup-backend.sh` output |
| `TF_BACKEND_STORAGE_ACCOUNT` | Terraform backend storage | From `setup-backend.sh` output |
| `TF_BACKEND_CONTAINER` | Terraform backend container | `tfstate` |
| `TF_BACKEND_STORAGE_KEY` | Storage account access key | See command below |

**Get the storage key:**
```bash
az storage account keys list \
  --resource-group <TF_BACKEND_RESOURCE_GROUP> \
  --account-name <TF_BACKEND_STORAGE_ACCOUNT> \
  --query '[0].value' -o tsv
```

### Step 3: Create Azure Service Principal

Run this command to create a service principal with the correct permissions:

```bash
# Get your subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Create service principal
az ad sp create-for-rbac \
  --name "github-actions-lego-case" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID \
  --sdk-auth
```

Copy the entire JSON output and save it as the `AZURE_CREDENTIALS` secret in GitHub.

### Step 4: Migrate Local State to Remote Backend (First Time Only)

If you already have a local `terraform.tfstate` file:

```bash
cd terraform

# Initialize with backend configuration
terraform init -migrate-state -backend-config=backend-config.tfbackend

# Verify state is now remote
terraform state list
```

The local `.tfstate` files are now safe to delete (they're backed up in Azure with versioning).

### Step 5: Create GitHub Environment (for Terraform approval)

1. Go to **Settings** → **Environments** → **New environment**
2. Name it: `production`
3. Add **Required reviewers**: Select yourself or team members
4. Click **Save protection rules**

This ensures Terraform changes require manual approval before being applied.

---

## 🚀 Usage

### Deploying Application Changes

1. Make changes to `backend/` code
2. Create PR to `main`
3. After PR is approved and merged → **Automatic deployment** 🎉

### Making Infrastructure Changes

1. Make changes to `terraform/` files
2. Create PR to `main`
3. **Terraform Plan** runs automatically and comments on PR
4. Review the plan carefully
5. After PR is merged → Workflow waits for **manual approval**
6. Approve in GitHub Actions → Terraform applies changes

### Manual Deployment

You can manually trigger deployments:
- Go to **Actions** → Select workflow → **Run workflow**

---

## 📊 Monitoring

### View Deployment Status
- Go to **Actions** tab in GitHub
- Click on latest workflow run
- Check logs and summaries

### Health Checks
- Application deployment includes automatic health check
- Deployment fails if health check doesn't return HTTP 200

### Rollback
If deployment fails:
```bash
# Manually rollback to previous version
cd backend
VERSION="0.1.0"  # Replace with last known good version

az acr build \
  --registry <registry-name> \
  --image question-answer-api:rollback \
  .

az containerapp update \
  --name <app-name> \
  --resource-group rg-case \
  --image <registry-name>.azurecr.io/question-answer-api:$VERSION
```

---

## 🛡️ Security Best Practices

✅ **What we're doing right:**
- Secrets stored in GitHub (not in code)
- `.env` and `.terraform` excluded from Git
- Manual approval required for infrastructure changes
- Separate pipelines for app vs infrastructure
- Health checks before marking deployment successful

⚠️ **Additional recommendations:**
- Enable branch protection on `main`
- Require status checks to pass before merging
- Consider adding staging environment
- Set up Azure Key Vault for production secrets

---

## 🐛 Troubleshooting

### "Azure Credentials Invalid"
- Verify `AZURE_CREDENTIALS` secret is correctly formatted JSON
- Check service principal hasn't expired
- Ensure it has Contributor role on subscription

### "Terraform Plan Failed"
- Check terraform syntax: `cd terraform && terraform validate`
- Verify all secrets are set in GitHub

### "Container App Update Failed"
- Check if Terraform resources exist
- Verify Container Registry access
- Check application logs in Azure Portal

---

## 📝 Notes

- **Version numbering:** Auto-incremented on each deployment (patch version)
- **Image tags:** Both versioned (`0.1.5`) and `latest` tags are created
- **Workflow triggers:** Path filters prevent unnecessary runs
- **Skip CI:** Commit messages with `[skip ci]` won't trigger workflows

