# Lego Case - Image Question Answering Platform

A production-ready full-stack application that allows users to upload images and ask questions about them using Azure OpenAI multimodal capabilities (GPT-4 Vision / Phi-4), with observability powered by Langfuse.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     GitHub Actions                       │
│       (CI/CD - Auto Deploy on Push to main)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Azure Container Registry                    │
│    (Docker images: frontend + backend)                  │
└────────────┬────────────────────┬───────────────────────┘
             │                    │
             ▼                    ▼
┌────────────────────┐  ┌────────────────────────────────┐
│  Frontend Web App  │  │     Backend API Web App        │
│  (React + Vite)    │◄─┤     (FastAPI)                  │
│  - Image upload    │  │  - POST /multimodal/ask-...    │
│  - Q&A interface   │  │  - GET  /health                │
└────────────────────┘  └─────────┬──────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
         Azure OpenAI (Multimodal)         Langfuse
         (Vision + Text Processing)    (Observability)
```

**Key Features:**
- 🔒 **CORS Configured via CI/CD**: Frontend and backend URLs are dynamically linked
- 🔄 **Automatic Deployment**: Push to main triggers infrastructure + app deployment
- 📦 **Shared Container Registry**: Both apps use the same ACR
- 🏷️ **Version Control**: Automatic semantic versioning on each deployment

## 🚀 Features

- **Image Question Answering**: Upload images and ask questions about them
- **Modern React UI**: Clean, responsive interface built with React + TypeScript
- **Multimodal AI**: Powered by Azure OpenAI vision models (GPT-4 Vision / Phi-4)
- **Full Observability**: Request tracing and token usage tracking with Langfuse
- **Production Ready**: Deployed on Azure App Service with auto-scaling
- **Automated CI/CD**: GitHub Actions handles infrastructure + deployment
- **Infrastructure as Code**: Terraform manages all Azure resources
- **Dynamic Configuration**: CORS and API URLs configured automatically via CI/CD

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

#### 1. Setup Remote Backend (Recommended)

```bash
cd terraform

# Create Azure Storage for Terraform state
./setup-backend.sh

# This creates storage and outputs configuration
# Save the values for later use
```

**Why?** Terraform state files can be 100MB+ and should never be in Git. See [Backend Guide](terraform/BACKEND.md).

#### 2. Configure and Apply Infrastructure

```bash
# Create terraform.tfvars from .env
./setup-vars.sh

# Initialize Terraform with remote backend
terraform init -backend-config=backend-config.tfbackend

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

#### Option 1: Full Stack Deployment (Recommended)

Deploy both frontend and backend at once:

```bash
./deploy-all.sh
```

This script:
1. Builds and pushes both Docker images to ACR
2. Updates both web apps with new images
3. Configures CORS (backend) and API URL (frontend)
4. Performs health checks
5. Auto-increments version numbers

#### Option 2: Individual Deployment

Deploy services separately:

```bash
# Backend only
cd backend && ./deploy.sh

# Frontend only
cd frontend && ./deploy.sh
```

**Note**: You'll need to manually configure CORS and API URLs if deploying individually.

#### Option 3: Automated CI/CD (Recommended for Production)

Push to `main` branch triggers automatic deployment:

```bash
git add .
git commit -m "feat: add new feature"
git push origin main
```

The CI/CD pipeline will:
1. ✅ Deploy infrastructure changes (if any)
2. ✅ Build and deploy backend (if changed)
3. ✅ Build and deploy frontend (if changed)
4. ✅ Configure cross-app environment variables:
   - Backend: `CORS_ORIGINS=https://frontend-url`
   - Frontend: `VITE_API_URL=https://backend-url`
5. ✅ Run health checks on both apps

## 🔄 CI/CD Pipeline

The deployment pipeline automatically handles the complete stack:

### Pipeline Stages

```
Infrastructure → Backend → Frontend → Configure Apps
     ↓              ↓          ↓            ↓
   Terraform    Build API   Build UI    Link Apps
   (if changed)  (if changed) (if changed) (CORS + URL)
```

### What Gets Deployed When

- **`terraform/**` changes**: Updates infrastructure (registry, app services, etc.)
- **`backend/**` changes**: Builds new backend image, deploys, restarts
- **`frontend/**` changes**: Builds new frontend image, deploys, restarts
- **Any change**: Re-configures CORS and API URLs to link apps

### GitHub Actions Workflow

See `.github/workflows/deploy-main.yml` for the complete workflow.

**Required GitHub Secrets:**
- `AZURE_CREDENTIALS`: Service principal for Azure login
- `TF_BACKEND_*`: Terraform backend configuration
- `OPENAI_API_KEY`: Azure OpenAI API key
- `LANGFUSE_*`: Langfuse configuration

## 📁 Project Structure

```
lego-case/
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks
│   │   ├── types/             # TypeScript types
│   │   ├── App.tsx            # Main app component
│   │   └── config.ts          # API configuration
│   ├── Dockerfile             # Frontend container
│   ├── deploy.sh              # Frontend deploy script
│   ├── package.json           # Node dependencies
│   └── version.txt            # Current version
├── backend/                    # FastAPI application
│   ├── routers/
│   │   ├── chat.py            # Text Q&A endpoint
│   │   └── multimodal.py      # Image Q&A endpoint
│   ├── app.py                 # Main application code
│   ├── config.py              # Settings & env vars
│   ├── Dockerfile             # Backend container
│   ├── deploy.sh              # Backend deploy script
│   ├── pyproject.toml         # Python dependencies
│   └── version.txt            # Current version
├── terraform/                  # Infrastructure as Code
│   ├── main.tf                # Azure resources
│   ├── variables.tf           # Input variables
│   ├── outputs.tf             # Output values
│   └── setup-vars.sh          # Env to tfvars helper
├── .github/
│   └── workflows/             # CI/CD pipelines
│       └── deploy-main.yml    # Main deployment pipeline
├── deploy-all.sh              # Deploy full stack locally
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

