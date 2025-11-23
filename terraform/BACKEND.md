# Terraform State Backend - Azure Storage

## Why Remote State?

❌ **Problems with local state:**
- `.tfstate` files can be 100MB+ (too large for Git)
- Risk of conflicts when multiple people work on infrastructure
- No versioning or backup
- Contains sensitive information

✅ **Benefits of Azure Storage backend:**
- Automatic state locking (prevents concurrent modifications)
- State versioning (rollback capability)
- Encrypted at rest
- Shared across team/CI-CD
- No size limits

---

## Setup Instructions

### 1. Create Backend Storage (One-time setup)

```bash
cd terraform
chmod +x setup-backend.sh
./setup-backend.sh
```

This creates:
- **Resource Group**: `rg-case` (uses existing resource group)
- **Storage Account**: `tfstatelego<random>` (globally unique name)
- **Blob Container**: `tfstate`
- **Backend Config**: `backend-config.tfbackend` (contains connection details)

**Save the output** - you'll need these values for CI/CD.

### 2. Migrate Existing State (if you have local state)

```bash
# This will copy your local state to Azure Storage
terraform init -migrate-state -backend-config=backend-config.tfbackend

# Answer 'yes' when prompted
```

**What happens:**
- Local `terraform.tfstate` → uploaded to Azure Storage
- Future operations use remote state
- Local `.tfstate` files can be deleted

### 3. Verify Remote State

```bash
# Check state is accessible
terraform state list

# View where state is stored
terraform state pull | head -n 10
```

---

## Configuration Files

### `backend-config.tfbackend`
```hcl
resource_group_name  = "rg-case"
storage_account_name = "tfstatelego12ab34cd"
container_name       = "tfstate"
key                  = "lego-case.tfstate"
```

**⚠️ IMPORTANT**: 
- This file is in `.gitignore` (contains account names)
- Keep it safe locally
- Values are stored in GitHub Secrets for CI/CD

### `providers.tf`
```hcl
terraform {
  backend "azurerm" {
    # Configuration loaded from:
    # 1. backend-config.tfbackend (local)
    # 2. Environment variables (CI/CD)
    # 3. CLI flags
  }
}
```

---

## Usage

### Local Development

```bash
# Always initialize with backend config
terraform init -backend-config=backend-config.tfbackend

# Normal operations work as usual
terraform plan
terraform apply
```

### CI/CD (GitHub Actions)

Backend is configured automatically via environment variables:

```yaml
env:
  ARM_ACCESS_KEY: ${{ secrets.TF_BACKEND_STORAGE_KEY }}
run: |
  terraform init \
    -backend-config="resource_group_name=${{ secrets.TF_BACKEND_RESOURCE_GROUP }}" \
    -backend-config="storage_account_name=${{ secrets.TF_BACKEND_STORAGE_ACCOUNT }}" \
    -backend-config="container_name=tfstate" \
    -backend-config="key=lego-case.tfstate"
```

Required GitHub Secrets:
- `TF_BACKEND_RESOURCE_GROUP`
- `TF_BACKEND_STORAGE_ACCOUNT`
- `TF_BACKEND_CONTAINER`
- `TF_BACKEND_STORAGE_KEY`

---

## State Locking

Azure Storage provides **automatic state locking** via blob leases.

**What this means:**
- Only one operation can modify state at a time
- Prevents race conditions
- If Terraform crashes, lock auto-releases after 15 minutes

**Check for locks:**
```bash
# If you get "state is locked" error
az storage blob lease show \
  --container-name tfstate \
  --name lego-case.tfstate \
  --account-name <storage-account-name>

# Force unlock (use with caution!)
terraform force-unlock <lock-id>
```

---

## State Versioning & Rollback

Azure Storage versioning is enabled for disaster recovery.

### View Version History

```bash
az storage blob list \
  --container-name tfstate \
  --account-name <storage-account-name> \
  --include v \
  --prefix lego-case.tfstate
```

### Rollback to Previous Version

```bash
# Download specific version
az storage blob download \
  --container-name tfstate \
  --name lego-case.tfstate \
  --file terraform.tfstate.backup \
  --version-id <version-id> \
  --account-name <storage-account-name>

# Restore it
az storage blob upload \
  --container-name tfstate \
  --name lego-case.tfstate \
  --file terraform.tfstate.backup \
  --account-name <storage-account-name> \
  --overwrite
```

---

## Security

### Access Control

The storage account uses:
- **Private blob access** (no public access)
- **Access keys** for authentication
- **Service principal** for CI/CD (via AZURE_CREDENTIALS)

### Encryption

- ✅ **At rest**: AES-256 encryption (default)
- ✅ **In transit**: HTTPS only
- ✅ **Versioning**: Enabled for rollback

### Best Practices

1. **Never commit** `backend-config.tfbackend` to Git (already in `.gitignore`)
2. **Rotate access keys** periodically
3. **Use RBAC** instead of access keys when possible
4. **Monitor access** via Azure Monitor logs

---

## Troubleshooting

### "Backend initialization required"

```bash
terraform init -backend-config=backend-config.tfbackend -reconfigure
```

### "Error acquiring state lock"

Someone else is running Terraform, or previous run crashed:

```bash
# Wait 15 minutes for auto-release, or force unlock
terraform force-unlock <lock-id>
```

### "Storage account not found"

Verify backend config:

```bash
cat backend-config.tfbackend

# Test connection
az storage account show \
  --name <storage-account-name> \
  --resource-group rg-terraform-state
```

### "Access denied"

```bash
# Login to Azure
az login

# Verify you have access
az storage account keys list \
  --resource-group rg-case \
  --account-name <storage-account-name>
```

---

## Cost

**Estimated monthly cost:**
- Storage Account: $0.02/GB
- Typical state file: 1-10MB
- Version history: ~$0.10/month
- **Total: < $1/month**

State locking has no additional cost.

---

## Migration Guide

### Moving from Local to Remote

```bash
# 1. Setup backend storage
./setup-backend.sh

# 2. Update providers.tf (already done)

# 3. Migrate state
terraform init -migrate-state -backend-config=backend-config.tfbackend

# 4. Verify
terraform state list

# 5. Delete local files (optional)
rm terraform.tfstate terraform.tfstate.backup
```

### Moving Between Storage Accounts

```bash
# 1. Update backend-config.tfbackend with new storage details

# 2. Reinitialize
terraform init -migrate-state -backend-config=backend-config.tfbackend -force-copy
```

---

## Resources

- [Terraform Azure Backend](https://developer.hashicorp.com/terraform/language/settings/backends/azurerm)
- [Azure Storage Security](https://learn.microsoft.com/en-us/azure/storage/common/storage-security-guide)
- [State Locking](https://developer.hashicorp.com/terraform/language/state/locking)

