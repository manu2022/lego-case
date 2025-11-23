# Quick Start Guide

## 🎯 What You Have Now

A production-ready setup with:
- ✅ FastAPI backend with Langfuse observability
- ✅ Docker containerization
- ✅ Terraform for Azure infrastructure
- ✅ **Remote state backend** (Azure Storage)
- ✅ **CI/CD pipeline** (GitHub Actions)
- ✅ Separate workflows for app vs infrastructure

---

## 🚀 First-Time Setup (Do Once)

### 1. Setup Terraform Backend

Store your Terraform state in Azure (not in Git):

```bash
cd terraform
./setup-backend.sh
```

**Save these values** from the output:
- `TF_BACKEND_RESOURCE_GROUP`
- `TF_BACKEND_STORAGE_ACCOUNT`
- `TF_BACKEND_CONTAINER`

### 2. Deploy Infrastructure

```bash
# Create terraform variables from your .env
./setup-vars.sh

# Initialize with remote backend
terraform init -backend-config=backend-config.tfbackend

# Deploy to Azure
terraform plan
terraform apply
```

### 3. Configure GitHub for CI/CD

Go to GitHub → Settings → Secrets and add:

**Application Secrets:**
- `OPENAI_API_KEY` - From your `.env`
- `LANGFUSE_SECRET_KEY` - From your `.env`
- `LANGFUSE_PUBLIC_KEY` - From your `.env`
- `LANGFUSE_BASE_URL` - `http://langfuse.legocase.com`

**Azure Secrets:**
```bash
# Create service principal
az ad sp create-for-rbac \
  --name "github-actions-lego-case" \
  --role contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv) \
  --sdk-auth
```
Copy the JSON output → Add as `AZURE_CREDENTIALS`

**Backend Secrets:**
- `TF_BACKEND_RESOURCE_GROUP` - From step 1
- `TF_BACKEND_STORAGE_ACCOUNT` - From step 1
- `TF_BACKEND_CONTAINER` - `tfstate`
- `TF_BACKEND_STORAGE_KEY` - Run:
  ```bash
  az storage account keys list \
    --resource-group rg-case \
    --account-name <TF_BACKEND_STORAGE_ACCOUNT> \
    --query '[0].value' -o tsv
  ```

### 4. Create Production Environment

GitHub → Settings → Environments → New environment:
- Name: `production`
- Add required reviewers (yourself)

This enables manual approval for infrastructure changes.

---

## 📝 Daily Workflow

### Making Code Changes

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes to backend/app.py

# 3. Test locally
cd backend
uvicorn app:app --reload

# 4. Commit and push
git add .
git commit -m "feat: add new feature"
git push origin feature/my-feature

# 5. Create PR on GitHub
# 6. After approval, merge to main
# 7. 🎉 Automatic deployment happens!
```

**What happens automatically:**
- ✅ Docker image builds
- ✅ Pushes to Azure Container Registry
- ✅ Deploys to Azure Container Apps
- ✅ Runs health check
- ✅ Version increments

### Making Infrastructure Changes

```bash
# 1. Create branch
git checkout -b infra/add-scaling

# 2. Edit terraform/*.tf files

# 3. Test locally
cd terraform
terraform plan

# 4. Commit and create PR
git add terraform/
git commit -m "infra: add auto-scaling"
git push origin infra/add-scaling

# 5. Check PR - Terraform Plan comment appears automatically
# 6. Review the plan carefully
# 7. Merge PR

# 8. Go to GitHub Actions
# 9. Workflow waits for approval
# 10. Click "Review deployments" → Approve
# 11. Terraform applies changes
```

**What happens automatically:**
- ✅ Terraform plan runs on PR
- ✅ Plan posted as PR comment
- ⏸️ Waits for manual approval after merge
- ✅ Applies infrastructure changes after approval

---

## 🔍 Monitoring & Debugging

### Check Deployment Status

```bash
# Application logs
az containerapp logs show \
  --name <app-name> \
  --resource-group rg-case \
  --follow

# Health check
curl https://<your-app>.azurecontainerapps.io/health
```

### View in Langfuse

Visit your Langfuse URL to see:
- Request traces
- Token usage
- Response times

### GitHub Actions

Go to **Actions** tab to see:
- Deployment history
- Success/failure status
- Detailed logs

---

## 📁 Important Files

| File | Purpose | In Git? |
|------|---------|---------|
| `.env` | Local environment variables | ❌ No |
| `terraform.tfvars` | Terraform variables | ❌ No |
| `terraform/*.tfstate` | Terraform state (OLD) | ❌ No |
| `backend-config.tfbackend` | Backend connection info | ❌ No |
| `.gitignore` | Files to exclude from Git | ✅ Yes |
| `backend/Dockerfile` | Container definition | ✅ Yes |
| `terraform/*.tf` | Infrastructure code | ✅ Yes |
| `.github/workflows/*.yml` | CI/CD pipelines | ✅ Yes |

---

## 🔒 Security Checklist

- ✅ `.env` excluded from Git
- ✅ Secrets stored in GitHub Secrets
- ✅ Terraform state in Azure Storage (encrypted)
- ✅ Manual approval for infrastructure changes
- ✅ Backend config excluded from Git
- ✅ No credentials in Docker images

---

## 📚 Documentation

- [Main README](README.md) - Full project documentation
- [CI/CD Setup](.github/CICD_SETUP.md) - Detailed pipeline guide
- [Backend Guide](terraform/BACKEND.md) - Terraform state management

---

## 🆘 Common Issues

### "Can't push to Git - file too large"

Files excluded in `.gitignore` - check you're not committing:
- `.terraform/` directory
- `*.tfstate` files
- `__pycache__/` directories

### "GitHub Actions failing - Terraform init"

Check GitHub Secrets are set:
- `TF_BACKEND_RESOURCE_GROUP`
- `TF_BACKEND_STORAGE_ACCOUNT`
- `TF_BACKEND_CONTAINER`
- `TF_BACKEND_STORAGE_KEY`

### "Local Terraform can't find state"

Run: `terraform init -backend-config=backend-config.tfbackend`

### "Deployment successful but app not working"

Check environment variables in Azure Container Apps:
```bash
az containerapp show \
  --name <app-name> \
  --resource-group rg-case \
  --query "properties.configuration.secrets"
```

---

## 🎓 Learning Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/)

---

## 💡 Tips

1. **Test locally first** before pushing
2. **Write clear commit messages** (helps CI/CD)
3. **Review Terraform plans carefully** before approving
4. **Monitor Langfuse** for observability
5. **Check GitHub Actions** after each push

---

**Need help?** Check the detailed documentation in the links above!

