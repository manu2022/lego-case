# Lego Case - Question Answer API

A production-ready FastAPI application that provides question-answering capabilities using Azure OpenAI (GPT-5 Mini), with observability powered by Langfuse.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     GitHub Actions                       │
│  (CI/CD Pipeline - Auto Deploy on PR merge to main)     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Azure Container Registry                    │
│         (Docker images: question-answer-api)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│            Azure Container Apps                          │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  FastAPI App (question-answer-api)               │  │
│  │  - POST /ask  : Ask questions                    │  │
│  │  - GET  /health : Health check                   │  │
│  └──────────────────────────────────────────────────┘  │
│           │                        │                    │
│           ▼                        ▼                    │
│   Azure OpenAI (GPT-5 Mini)   Langfuse                 │
│   (Question Processing)       (Observability)           │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Features

- **Question Answering**: Ask questions and get intelligent responses from GPT-5 Mini
- **Observability**: Full request tracing with Langfuse integration
- **Production Ready**: Deployed on Azure Container Apps with auto-scaling
- **CI/CD Pipeline**: Automated deployment via GitHub Actions
- **Infrastructure as Code**: Terraform for Azure resource management
- **Health Checks**: Built-in health endpoints for monitoring

## 📋 Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (Fast Python package manager)
- Docker (for local development)
- Azure CLI (for deployment)
- Terraform 1.9+ (for infrastructure)

## 🔧 Local Development

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd lego-case
```

### 2. Create `.env` file

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
```env
OPENAI_API_KEY=your_azure_openai_key
LANGFUSE_SECRET_KEY=your_langfuse_secret
LANGFUSE_PUBLIC_KEY=your_langfuse_public
LANGFUSE_BASE_URL=http://langfuse.legocase.com
```

### 3. Run locally with Python

```bash
# Install dependencies
uv pip install -r pyproject.toml

# Run the app
cd backend
uvicorn app:app --reload
```

### 4. Run with Docker

```bash
cd backend
docker build -t question-answer-api .
docker run -p 8000:8000 --env-file ../.env question-answer-api
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the capital of France?"}'
```

## ☁️ Deployment

### Infrastructure Setup (One-time)

```bash
cd terraform

# Create terraform.tfvars from .env
./setup-vars.sh

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Apply infrastructure
terraform apply
```

This creates:
- Azure Container Registry
- Azure Container Apps Environment
- Container App with auto-scaling
- Log Analytics workspace

### Application Deployment

#### Manual Deployment

```bash
cd backend
./deploy.sh
```

#### Automated Deployment (CI/CD)

1. **Setup GitHub Actions**: See [CI/CD Setup Guide](.github/CICD_SETUP.md)
2. **Push to main**: Deployment happens automatically after PR merge
3. **Monitor**: Check GitHub Actions tab for deployment status

## 🔄 CI/CD Pipeline

We use **separate pipelines** for application and infrastructure:

### Application Pipeline
- **Trigger**: Push to `main` (when `backend/**` changes)
- **Steps**: Build → Push to ACR → Deploy to Container Apps → Health Check
- **Auto-runs**: Yes, no approval needed

### Infrastructure Pipeline
- **Trigger**: Push to `main` (when `terraform/**` changes)
- **Steps**: Plan → **Manual Approval** → Apply
- **Auto-runs**: Requires manual approval in GitHub

**Full setup instructions**: [CI/CD Setup Guide](.github/CICD_SETUP.md)

## 📁 Project Structure

```
lego-case/
├── backend/                    # FastAPI application
│   ├── app.py                 # Main application code
│   ├── Dockerfile             # Container image definition
│   ├── deploy.sh              # Deployment script
│   ├── pyproject.toml         # Python dependencies
│   └── version.txt            # Current version
├── terraform/                  # Infrastructure as Code
│   ├── main.tf                # Azure resources
│   ├── variables.tf           # Input variables
│   ├── outputs.tf             # Output values
│   └── setup-vars.sh          # Env to tfvars helper
├── .github/
│   └── workflows/             # CI/CD pipelines
│       ├── deploy-app.yml     # App deployment
│       ├── terraform-plan.yml # Terraform plan on PR
│       └── terraform-apply.yml # Terraform apply
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🔒 Security

- ✅ Environment variables stored in GitHub Secrets
- ✅ `.env` files excluded from Git (never committed)
- ✅ `.terraform` directory excluded from version control
- ✅ Terraform state stored in Azure backend
- ✅ Manual approval required for infrastructure changes
- ✅ Secrets injected at runtime (not baked into images)

## 📊 Monitoring

### Application Logs
```bash
# View logs in Azure
az containerapp logs show \
  --name <app-name> \
  --resource-group rg-case \
  --follow
```

### Langfuse Dashboard
Visit your Langfuse URL to see:
- Request traces
- Token usage
- Response times
- Error rates

### Azure Portal
- Container Apps metrics
- Auto-scaling events
- Health probe status

## 🧪 Testing

```bash
# Run tests (if applicable)
pytest

# Check API health
curl https://<your-app-url>.azurecontainerapps.io/health
```

## 🐛 Troubleshooting

### Local Development Issues

**Port already in use:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Dependencies not installing:**
```bash
uv pip install --upgrade pip
uv pip install -r backend/pyproject.toml
```

### Deployment Issues

**Can't push to GitHub (large files):**
- Ensure `.gitignore` excludes `.terraform/` and `__pycache__/`
- Run: `git rm -r --cached terraform/.terraform`

**Azure login fails:**
```bash
az login
az account set --subscription <your-subscription-id>
```

**Container app not updating:**
```bash
# Force new revision
az containerapp update --name <app-name> --resource-group rg-case --revision-suffix $(date +%s)
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure Container Apps Docs](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Langfuse Documentation](https://langfuse.com/docs)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Commit with clear messages: `git commit -m "feat: add new feature"`
4. Push and create PR: `git push origin feature/your-feature`
5. Wait for CI checks to pass
6. Request review and merge

## 📝 License

[Add your license here]

## 👤 Author

[Add your information here]

---

**Note**: This is a case study project demonstrating modern cloud-native application development with CI/CD best practices.

